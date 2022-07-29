from django.urls import path
from . import views

urlpatterns = [

    path('login/', views.login_page, name='login'),
    path('register/', views.register, name='register'),
    # path('edit/', views.update_profile, name='edit'),
    path('logout/', views.logout_page, name='logout'),
    path('', views.index, name='system_admin'),
    # manage_hotel
    path('manage_hotel/', views.hotel, name='manage_hotel'),
    path('manage_hotel/add_hotel', views.add_hotel, name='add_hotel'),
    path('manage_hotel/update_hotel/<str:id>/', views.update_hotel, name='update_hotel'),
    path('manage_hotel/add_hotel/hotel_admin/<str:id>/', views.hotel_admin, name='hotel_admin'),
    # manage payment methods
    path('manage_payment_method/', views.payment_method, name='manage_payment_method'),
    path('manage_payment_method/add_payment_method', views.add_payment_method, name='add_payment_method'),
    path('manage_payment_method/update_payment_method/<str:id>/', views.update_payment_method, name='update_payment_method'),
    # manage city
    path('manage_city/', views.city, name='manage_city'),
    path('manage_city/add_city', views.add_city, name='add_city'),
    path('manage_city/update_city/<str:id>/', views.update_city,  name='update_city'),
    # manage feature
    path('manage_feature/', views.feature, name='manage_feature'),
    path('manage_feature/add_feature', views.add_feature, name='add_feature'),
    path('manage_feature/update_feature/<str:id>/', views.update_feature,
         name='update_feature'),


]
