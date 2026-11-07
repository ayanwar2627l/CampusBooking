from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    # Facilities
    path('facilities/', views.facility_list, name='facility_list'),
    path('facilities/<int:pk>/', views.facility_detail, name='facility_detail'),
    path('facilities/manage/', views.manage_facilities, name='manage_facilities'),
    path('facilities/add/', views.add_facility, name='add_facility'),
    path('facilities/<int:pk>/edit/', views.edit_facility, name='edit_facility'),
    path('facilities/<int:pk>/delete/', views.delete_facility, name='delete_facility'),

    # Bookings
    path('book/<int:facility_pk>/', views.create_booking, name='create_booking'),
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('bookings/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),

    # Admin booking management
    path('admin-bookings/', views.admin_booking_list, name='admin_booking_list'),
    path('admin-bookings/<int:pk>/review/', views.review_booking, name='review_booking'),

    # Announcements
    path('announcements/add/', views.add_announcement, name='add_announcement'),

    # API
    path('api/booked-slots/<int:facility_pk>/', views.get_booked_slots, name='get_booked_slots'),
]
