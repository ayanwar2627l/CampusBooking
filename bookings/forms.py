from django import forms
from .models import Booking, BookingDocument, Facility
from django.utils import timezone
import datetime


class BookingForm(forms.ModelForm):
    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': str(timezone.now().date() + datetime.timedelta(days=1)),
            'max': str(timezone.now().date() + datetime.timedelta(days=30)),
        })
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )

    class Meta:
        model = Booking
        fields = ['facility', 'booking_date', 'start_time', 'end_time',
                  'purpose', 'purpose_description', 'expected_attendees',
                  'club_name', 'event_name']
        widgets = {
            'facility': forms.Select(attrs={'class': 'form-select'}),
            'purpose': forms.Select(attrs={'class': 'form-select'}),
            'purpose_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'expected_attendees': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'club_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., IEEE Student Chapter'}),
            'event_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., One India Cultural Fest'}),
        }

    def __init__(self, *args, facility=None, **kwargs):
        super().__init__(*args, **kwargs)
        if facility:
            self.fields['facility'].initial = facility
            self.fields['facility'].widget = forms.HiddenInput()
        else:
            self.fields['facility'].queryset = Facility.objects.filter(is_available=True)

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        booking_date = cleaned_data.get('booking_date')

        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError("End time must be after start time.")

        if booking_date:
            if booking_date <= timezone.now().date():
                raise forms.ValidationError("Booking date must be in the future.")

        # Check for conflicting bookings
        facility = cleaned_data.get('facility')
        if facility and booking_date and start_time and end_time:
            conflicts = Booking.objects.filter(
                facility=facility,
                booking_date=booking_date,
                status__in=['pending', 'approved'],
            ).exclude(
                start_time__gte=end_time
            ).exclude(
                end_time__lte=start_time
            )
            if self.instance.pk:
                conflicts = conflicts.exclude(pk=self.instance.pk)
            if conflicts.exists():
                raise forms.ValidationError(
                    f"This facility is already booked for the selected date and time. "
                    f"Please choose a different time slot."
                )

        return cleaned_data


class BookingDocumentForm(forms.ModelForm):
    class Meta:
        model = BookingDocument
        fields = ['doc_type', 'document', 'description']
        widgets = {
            'doc_type': forms.Select(attrs={'class': 'form-select'}),
            'document': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.jpg,.png'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief description'}),
        }


class BookingReviewForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['status', 'admin_remarks']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                    'placeholder': 'Add remarks for the student...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [
            ('approved', 'Approve'),
            ('rejected', 'Reject'),
        ]


class FacilityForm(forms.ModelForm):
    class Meta:
        model = Facility
        fields = ['name', 'facility_type', 'block', 'floor', 'room_number',
                  'capacity', 'description', 'amenities', 'image',
                  'is_available', 'booking_advance_days']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'facility_type': forms.Select(attrs={'class': 'form-select'}),
            'block': forms.Select(attrs={'class': 'form-select'}),
            'floor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Ground, 1st, 2nd'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 101, A-201'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'amenities': forms.TextInput(attrs={'class': 'form-control',
                                                'placeholder': 'e.g., Projector, AC, Whiteboard, WiFi'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'booking_advance_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
