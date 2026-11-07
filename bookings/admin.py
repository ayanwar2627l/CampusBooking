from django.contrib import admin
from .models import Facility, Booking, BookingDocument, TimeSlot, Announcement


class BookingDocumentInline(admin.TabularInline):
    model = BookingDocument
    extra = 0


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'facility_type', 'block', 'capacity', 'is_available']
    list_filter = ['facility_type', 'block', 'is_available']
    search_fields = ['name', 'block', 'room_number']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['facility', 'student', 'booking_date', 'start_time', 'end_time', 'status', 'created_at']
    list_filter = ['status', 'purpose', 'facility__facility_type']
    search_fields = ['student__first_name', 'student__last_name', 'facility__name', 'event_name']
    inlines = [BookingDocumentInline]
    actions = ['approve_bookings', 'reject_bookings']

    def approve_bookings(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f'{queryset.count()} booking(s) approved.')
    approve_bookings.short_description = 'Approve selected bookings'

    def reject_bookings(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f'{queryset.count()} booking(s) rejected.')
    reject_bookings.short_description = 'Reject selected bookings'


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'is_active', 'created_at']
    list_filter = ['is_active']
