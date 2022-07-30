from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect

from customer.models import BookingRequest, RequestedRoom
from hotel.views import price_calculator
from system_admin.forms import UserForm
from system_admin.models import Hotel
from hotel.models import Room, PaymentInformation
from .decorators import allowed_users
from django.contrib import messages
# Create your views here.
from .forms import PaidForm
from datetime import date


def index(request):
    q = None
    count = None
    hotels = Hotel.objects.all()
    if request.GET.get('q') is not None:
        q = request.GET.get('q')
        hotels = Hotel.objects.filter(
            Q(city__name__icontains=q) |
            Q(name__icontains=q))
        count = hotels.count()

    context = {'hotels': hotels, 'count': count}
    return render(request, 'index.html', context)


def selected_hotel(request):
    # booking_request_handler()
    q = None
    hotel = None
    rooms = None
    features = None
    if request.GET.get('q') is not None:
        q = request.GET.get('q')
        hotel = Hotel.objects.get(id=q)
        features = hotel.feature.all()
        rooms = Room.objects.filter(hotel=hotel)
        if request.method == 'POST':
            if request.user.is_anonymous:
                return redirect('login')
            elif request.user.role != 'customer':
                return HttpResponse("sorry only customers are allowed to book ")
            else:
                booking_request = BookingRequest.objects.create(customer=request.user, hotel=hotel,
                                                                check_in_date=request.POST.get('check_in_date'),
                                                                check_out_date=request.POST.get('check_out_date'))
                for room in rooms:
                    try:
                        chosed = request.POST.getlist(room.type)
                        if chosed[1] is not '':
                            booking_request.room.add(room, through_defaults={'number_of_room': chosed[1]})

                    except:
                        pass
                return HttpResponse('you have booked your room dude')
    context = {'hotel': hotel, 'rooms': rooms, 'features': features}
    return render(request, 'selected_hotel.html', context)


@login_required(login_url='login')
@allowed_users
def my_booking(request):
    # booking_request_handler()
    bookings = BookingRequest.objects.filter(customer=request.user)
    context = {'bookings': bookings}
    return render(request, 'customer/mybooking.html', context)


@login_required(login_url='login')
@allowed_users
def profile(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid:
            form.save()
            return redirect('profile')
    return render(request, 'customer/userprofile.html')


@login_required(login_url='login')
@allowed_users
def pay(request, id):
    booking_request = BookingRequest.objects.get(id=id)
    if booking_request.status != "make payment":
        messages.error(request, 'the booking cannot accept payment ')
        return redirect('booking')
    # There may be many rooms under one Booking request . but all have the same hotel id
    hotel = booking_request.hotel
    payment_information = PaymentInformation.objects.filter(hotel=hotel)
    # requested_rooms = RequestedRoom.objects.filter(booking_request=booking_request).first()
    context = {'payment_information': payment_information, 'booking_request_id': booking_request.id}
    if request.method == "POST":
        # here the posted value should fill the bill information
        pass
    return render(request, 'customer/pay.html', context)


@login_required(login_url='login')
@allowed_users
def payment_detail(request, br_id, pi_id):
    form = PaidForm()
    payment_details = PaymentInformation.objects.get(id=pi_id)
    booking_request = BookingRequest.objects.get(id=br_id)
    requested_rooms = RequestedRoom.objects.filter(booking_request=booking_request)
    booking = RequestedRoom.objects.filter(booking_request=booking_request)
    price = price_calculator(booking)
    for item in price:
        if item['id'] == booking_request.id:
            price = item['price']
    # price = []
    # total_price = 0
    # count = 0
    # old_request = None
    # for item in booking:
    #     total = item.room.price * item.number_of_room
    #     new_request = item.booking_request
    #     total_price = total_price + total
    #     if count == 0:
    #         old_request = new_request
    #         count += 1
    #
    #     elif old_request != new_request:
    #         price.append(total_price)
    #         total_price = 0
    #
    #     elif count == booking.count():
    #         price.append(total_price)
    #     old_request = new_request
    #     count += 1
    # price = price[0]
    # for item in total_price:
    #     price = item.price

    if request.method == "POST":
        form = PaidForm(request.POST, request.FILES)
        if form.is_valid():
            paid = form.save(commit=False)
            paid.booking_request = booking_request
            paid.payment_information = payment_details
            paid.expected_payment = price
            paid.save()
            booking_request.status = "paid"
            booking_request.save()
            messages.success(request, 'you have made the payment successfully')
            context = {"payment_details": payment_details, "requested_rooms": requested_rooms,
                       'price': price}
            return redirect('index')
    context = {"payment_details": payment_details, "requested_rooms": requested_rooms, 'price': price,
               'form': form}
    return render(request, 'customer/payment_detail.html', context)


def contact(request):
    return render(request,'contact_us.html' )
