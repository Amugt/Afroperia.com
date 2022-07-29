from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.views.decorators.cache import never_cache

from hotel.models import Chat
from .models import User, Hotel, ContactUs, PaymentMethod, Feature, City
from django.shortcuts import render, redirect, HttpResponse
from .forms import OurUserCreationForm, PaymentMethodForm, HotelForm, CityForm, FeatureForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import allowed_users


# Create your views here.
# ------------------------------------------------------------------------------------------------------|
#                                                                                                      |
#   REGISTRATION AND USER MANAGEMENT
# ------------------------------------------------------------------------------------------------------|


def register(request):
    form = OurUserCreationForm()
    # This role should be assigned based on the place the request come  or by some hidden input field
    if request.method == 'POST':
        form = OurUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else:
            context = {'form': form}
            return render(request, 'register.html', context)

    context = {'form': form}
    return render(request, 'register.html', context)


@never_cache
def login_page(request):
    # if user.is_authenticated:
    #     return HttpResponseRedirect(reverse('my_redirect'))
    if request.user.is_authenticated:
        if request.user.role == 'customer':
            return redirect('index')
        elif request.user.role == 'hotel_admin':
            # here the hotel related to the user should be found and the user  will be sent there.
            # hotel = Hotel.objects.filter(admin=request.user).first()
            # context = {'hotel': hotel}
            #
            # return render(request, 'hotel/index.html', context)
            return redirect('hotel')
        elif request.user.role == 'system_admin':
            return redirect('system_admin')
    if request.method == "POST":
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        try:
            user = User.objects.get(phone_number=phone_number)

        except:
            messages.error(request, 'Phone number does not exist')
            return redirect('login')
        user = authenticate(request, phone_number=phone_number, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'customer':
                return redirect('index')
            elif user.role == 'hotel_admin':
                # here the hotel related to the user should be found and the user  will be sent there.
                hotel = Hotel.objects.filter(admin=user).first()
                context = {'hotel': hotel}

                return render(request, 'hotel/index.html', context)
            elif user.role == 'system_admin':
                return redirect('system_admin')
            else:
                return HttpResponse('you are not belong here please re register')

        else:
            return HttpResponse('WHAT IS HAPPENING')
    return render(request, 'login.html')


def logout_page(request):
    logout(request)
    return redirect('index')


# Admin Index
@login_required(login_url='login')
@allowed_users
def index(request):
    # the system should now who registered any hotel and any manager for more security
    hotel = Hotel.objects.all()
    # chat = Chat.objects.filter(user=request.user, seen=False)
    # contact_us = ContactUs.objects.filter(seen=False)
    context = {'hotel': hotel}
    return render(request, 'system_admin/index.html', context)


# ------------------------------------------------------------------------------------------------------|
# #                                                                                                      |
# #   MANAGE HOTELS
# # ------------------------------------------------------------------------------------------------------|
@login_required(login_url='login')
@allowed_users
def hotel(request):
    hotels = Hotel.objects.all()
    context = {'hotels': hotels}
    return render(request, 'system_admin/manage_hotel.html', context)

@login_required(login_url='login')
@allowed_users
def add_hotel(request):
    form = HotelForm()
    context = {'form': form}
    if request.method == 'POST':
        form = HotelForm(request.POST,request.FILES)
        if form.is_valid():
            hotel = form.save()
            return redirect('hotel_admin', hotel.id)
        else:
            messages.error(request,'there are some errors')
    return render(request, 'system_admin/new.html', context)

@login_required(login_url='login')
@allowed_users
def hotel_admin(request, id):
    hotel = Hotel.objects.get(id=id)
    form = OurUserCreationForm()
    # This role should be assigned based on the place the request come  or by some hidden input field
    if request.method == 'POST':
        form = OurUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            hotel.admin.add(user)
            messages.success(request, 'you have added new hotel successfully')
            return redirect('system_admin')
        else:
            context = {'form': form, 'hotel': hotel}
            return render(request, 'system_admin/hotel_admin.html', context)

    context = {'form': form, 'hotel': hotel}
    return render(request, 'system_admin/hotel_admin.html', context)

@login_required(login_url='login')
@allowed_users
def update_hotel(request, id):
    hotel = Hotel.objects.get(id=id)
    form = HotelForm(instance=hotel)
    if request.method == "POST":
        form = HotelForm(request.POST, request.FILES, instance=Hotel)
        if form.is_valid():
            form.save()
            # success message
            messages.success(request, ' updated successfully')
            return redirect('system_admin')
    context = {'form': form}
    return render(request, 'system_admin/edit.html', context)


# # ------------------------------------------------------------------------------------------------------|
# #
# #   MANAGE PAYMENT  METHODS
# # ------------------------------------------------------------------------------------------------------|
@login_required(login_url='login')
@allowed_users
def payment_method(request):
    payment_methods = PaymentMethod.objects.all()
    context = {'payment_methods': payment_methods}
    return render(request, 'system_admin/manage_payment_method.html', context)

@login_required(login_url='login')
@allowed_users
def add_payment_method(request):
    form = PaymentMethodForm()
    if request.method == "POST":
        form = PaymentMethodForm(request.FILES, request.POST)
        if form.is_valid():
            form.save()
            return redirect('system_admin')
        else:
            messages.error(request, 'there is error in your input try again')
    context = {'form': form}
    return render(request, 'system_admin/new.html', context)

@login_required(login_url='login')
@allowed_users
def update_payment_method(request, id):
    payment_method = PaymentMethod.objects.get(id=id)
    form = PaymentMethodForm(instance=payment_method)
    if request.method == "POST":
        form = PaymentMethodForm(request.POST, request.FILES, instance=payment_method)
        if form.is_valid():
            form.save()
            # success message
            messages.success(request, ' updated successfully')
            return redirect('system_admin')
    context = {'form': form}
    return render(request, 'system_admin/edit.html', context)

@login_required(login_url='login')
@allowed_users
def delete_payment_method(request, id):
    payment_method = PaymentMethod(id=id)
    if request.method == "POST":
        payment_method.delete()
        messages.success(request, 'you have deleted the selected item!')
        return redirect('index')
    context = {'form': payment_method}
    return render(request, '', context)


# ------------------------------------------------------------------------------------------------------|
#                                                                                                      |
#   MANAGE CITY
# ------------------------------------------------------------------------------------------------------|
@login_required(login_url='login')
@allowed_users
def city(request):
    cities = City.objects.all()
    context = {'cities': cities}
    return render(request, 'system_admin/manage_city.html', context)

@login_required(login_url='login')
@allowed_users
def add_city(request):
    form = CityForm()
    if request.method == "POST":
        form = CityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('system_admin')
        else:
            messages.error(request, 'there is error in your input try again')
    context = {'form': form}
    return render(request, 'system_admin/new.html', context)

@login_required(login_url='login')
@allowed_users
def update_city(request, id):
    city = City.objects.get(id=id)
    form = CityForm(instance=city)
    if request.method == "POST":
        form = CityForm(request.POST, instance=city)
        if form.is_valid():
            form.save()
            # success message
            messages.success(request, ' updated successfully')
            return redirect('system_admin')
    context = {'form': form}
    return render(request, 'system_admin/edit.html', context)

@login_required(login_url='login')
@allowed_users
def delete_city(request, id):
    city = City.objects.get(id=id)
    if request.method == "POST":
        city.delete()
        messages.success(request, 'you have deleted the selected item!')
        return redirect('index')
    context = {'form': city}
    return render(request, '', context)


# ------------------------------------------------------------------------------------------------------|
#                                                                                                      |
#   MANAGE FEATURES
# ------------------------------------------------------------------------------------------------------|
@login_required(login_url='login')
@allowed_users
def feature(request):
    features = Feature.objects.all()
    context = {'features': features}
    return render(request, 'system_admin/manage_feature.html', context)

@login_required(login_url='login')
@allowed_users
def add_feature(request):
    form = FeatureForm()
    if request.method == "POST":
        form = FeatureForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('system_admin')
        else:
            messages.error(request, 'there is error in your input try again')
    context = {'form': form}
    return render(request, 'system_admin/new.html', context)


def update_feature(request, id):
    feature = Feature.objects.get(id=id)
    form = FeatureForm(instance=feature)
    if request.method == "POST":
        form = FeatureForm(request.POST, instance=feature)
        if form.is_valid():
            form.save()
            # success message
            messages.success(request, ' updated successfully')
            return redirect('system_admin')
    context = {'form': form}
    return render(request, 'system_admin/edit.html', context)


def delete_feature(request, id):
    feature = Feature.objects.get(id=id)
    if request.method == "POST":
        feature.delete()
        messages.success(request, 'you have deleted the selected item!')
        return redirect('index')
    context = {'form': feature}
    return render(request, '', context)
