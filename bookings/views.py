from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from .models import Facility, Booking, BookingDocument, Announcement
from .forms import BookingForm, BookingDocumentForm, BookingReviewForm, FacilityForm
from accounts.models import CustomUser
import datetime


def home(request):
    """Public landing page"""
    facilities = Facility.objects.filter(is_available=True)
    facility_types = {}
    for ft in Facility.FACILITY_TYPES:
        count = facilities.filter(facility_type=ft[0]).count()
        if count > 0:
            facility_types[ft[1]] = count

    announcements = Announcement.objects.filter(is_active=True)[:3]
    total_facilities = facilities.count()
    total_bookings = Booking.objects.filter(status='approved').count()

    context = {
        'facilities': facilities[:6],
        'facility_types': facility_types,
        'announcements': announcements,
        'total_facilities': total_facilities,
        'total_bookings': total_bookings,
        'default_facility_types': [
            'Computer Lab', 'Mac Lab', 'Electronics Lab',
            'Seminar Hall', 'Auditorium', 'DSW Room',
        ],
        'how_it_works_steps': [
            'Register & Verify',
            'Browse Facilities',
            'Submit Booking',
            'Upload Documents',
            'Get Approval',
        ],
    }
    return render(request, 'bookings/home.html', context)


@login_required
def dashboard(request):
    """Main dashboard - redirects based on role"""
    if request.user.is_admin_user:
        return redirect('admin_dashboard')
    return redirect('student_dashboard')


@login_required
def student_dashboard(request):
    """Student dashboard"""
    if request.user.is_admin_user:
        return redirect('admin_dashboard')

    my_bookings = Booking.objects.filter(student=request.user).order_by('-created_at')
    upcoming = my_bookings.filter(
        booking_date__gte=timezone.now().date(),
        status='approved'
    ).count()
    pending = my_bookings.filter(status='pending').count()
    total = my_bookings.count()

    announcements = Announcement.objects.filter(is_active=True)[:3]
    recent_bookings = my_bookings[:5]

    context = {
        'my_bookings': my_bookings[:10],
        'upcoming': upcoming,
        'pending': pending,
        'total': total,
        'announcements': announcements,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'bookings/student_dashboard.html', context)


@login_required
def admin_dashboard(request):
    """Admin dashboard"""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('student_dashboard')

    all_bookings = Booking.objects.all().order_by('-created_at')
    pending_bookings = all_bookings.filter(status='pending')
    pending_students = CustomUser.objects.filter(role='student', is_approved=False)

    stats = {
        'total_facilities': Facility.objects.count(),
        'total_bookings': all_bookings.count(),
        'pending_bookings': pending_bookings.count(),
        'approved_bookings': all_bookings.filter(status='approved').count(),
        'total_students': CustomUser.objects.filter(role='student', is_approved=True).count(),
        'pending_approvals': pending_students.count(),
    }

    recent_bookings = all_bookings[:10]
    announcements = Announcement.objects.all()[:5]

    context = {
        'stats': stats,
        'pending_bookings': pending_bookings[:10],
        'pending_students': pending_students,
        'recent_bookings': recent_bookings,
        'announcements': announcements,
    }
    return render(request, 'bookings/admin_dashboard.html', context)


@login_required
def facility_list(request):
    """List all facilities with filtering"""
    facilities = Facility.objects.filter(is_available=True)

    # Filtering
    facility_type = request.GET.get('type', '')
    block = request.GET.get('block', '')
    search = request.GET.get('search', '')

    if facility_type:
        facilities = facilities.filter(facility_type=facility_type)
    if block:
        facilities = facilities.filter(block=block)
    if search:
        facilities = facilities.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    context = {
        'facilities': facilities,
        'facility_types': Facility.FACILITY_TYPES,
        'blocks': Facility.BLOCK_CHOICES,
        'selected_type': facility_type,
        'selected_block': block,
        'search': search,
    }
    return render(request, 'bookings/facility_list.html', context)


@login_required
def facility_detail(request, pk):
    """Facility detail and booking form"""
    facility = get_object_or_404(Facility, pk=pk)

    # Get upcoming approved bookings for calendar
    upcoming_bookings = Booking.objects.filter(
        facility=facility,
        booking_date__gte=timezone.now().date(),
        status__in=['pending', 'approved']
    ).order_by('booking_date', 'start_time')

    form = BookingForm(facility=facility)

    context = {
        'facility': facility,
        'upcoming_bookings': upcoming_bookings,
        'form': form,
    }
    return render(request, 'bookings/facility_detail.html', context)


@login_required
def create_booking(request, facility_pk):
    """Create a new booking"""
    facility = get_object_or_404(Facility, pk=facility_pk, is_available=True)

    if not request.user.is_approved and not request.user.is_admin_user:
        messages.error(request, 'Your account needs admin approval before making bookings.')
        return redirect('facility_detail', pk=facility_pk)

    if request.method == 'POST':
        form = BookingForm(request.POST, facility=facility)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.student = request.user
            booking.facility = facility
            booking.save()

            # Handle document uploads
            doc_types = request.POST.getlist('doc_type')
            doc_files = request.FILES.getlist('document')
            doc_descs = request.POST.getlist('doc_description')

            for i, (doc_type, doc_file) in enumerate(zip(doc_types, doc_files)):
                if doc_file:
                    desc = doc_descs[i] if i < len(doc_descs) else ''
                    BookingDocument.objects.create(
                        booking=booking,
                        doc_type=doc_type,
                        document=doc_file,
                        description=desc
                    )

            messages.success(request, 'Booking request submitted! Awaiting admin approval.')
            return redirect('my_bookings')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = BookingForm(facility=facility)

    context = {
        'facility': facility,
        'form': form,
        'doc_types': BookingDocument.DOC_TYPES,
    }
    return render(request, 'bookings/create_booking.html', context)


@login_required
def my_bookings(request):
    """Student's booking list"""
    bookings = Booking.objects.filter(student=request.user).order_by('-created_at')

    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    context = {
        'bookings': bookings,
        'status_filter': status_filter,
        'status_choices': Booking.STATUS_CHOICES,
    }
    return render(request, 'bookings/my_bookings.html', context)


@login_required
def booking_detail(request, pk):
    """Booking detail view"""
    if request.user.is_admin_user:
        booking = get_object_or_404(Booking, pk=pk)
    else:
        booking = get_object_or_404(Booking, pk=pk, student=request.user)

    documents = booking.documents.all()

    context = {
        'booking': booking,
        'documents': documents,
    }
    return render(request, 'bookings/booking_detail.html', context)


@login_required
def cancel_booking(request, pk):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, pk=pk, student=request.user)

    if booking.status in ['pending', 'approved']:
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully.')
    else:
        messages.error(request, 'This booking cannot be cancelled.')

    return redirect('my_bookings')


@login_required
def admin_booking_list(request):
    """Admin view all bookings"""
    if not request.user.is_admin_user:
        return redirect('student_dashboard')

    bookings = Booking.objects.all().order_by('-created_at')

    status_filter = request.GET.get('status', '')
    facility_filter = request.GET.get('facility', '')
    date_filter = request.GET.get('date', '')
    search = request.GET.get('search', '')

    if status_filter:
        bookings = bookings.filter(status=status_filter)
    if facility_filter:
        bookings = bookings.filter(facility__id=facility_filter)
    if date_filter:
        bookings = bookings.filter(booking_date=date_filter)
    if search:
        bookings = bookings.filter(
            Q(student__first_name__icontains=search) |
            Q(student__last_name__icontains=search) |
            Q(student__registration_number__icontains=search) |
            Q(facility__name__icontains=search) |
            Q(event_name__icontains=search)
        )

    context = {
        'bookings': bookings,
        'facilities': Facility.objects.all(),
        'status_filter': status_filter,
        'facility_filter': facility_filter,
        'status_choices': Booking.STATUS_CHOICES,
        'search': search,
    }
    return render(request, 'bookings/admin_booking_list.html', context)


@login_required
def review_booking(request, pk):
    """Admin reviews/approves/rejects a booking"""
    if not request.user.is_admin_user:
        return redirect('student_dashboard')

    booking = get_object_or_404(Booking, pk=pk)
    documents = booking.documents.all()

    if request.method == 'POST':
        form = BookingReviewForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            action = form.cleaned_data['status']
            messages.success(request, f'Booking {action} successfully.')
            return redirect('admin_booking_list')
    else:
        form = BookingReviewForm(instance=booking)

    context = {
        'booking': booking,
        'form': form,
        'documents': documents,
    }
    return render(request, 'bookings/review_booking.html', context)


@login_required
def manage_facilities(request):
    """Admin manage facilities"""
    if not request.user.is_admin_user:
        return redirect('student_dashboard')

    facilities = Facility.objects.all()
    context = {'facilities': facilities}
    return render(request, 'bookings/manage_facilities.html', context)


@login_required
def add_facility(request):
    """Admin add facility"""
    if not request.user.is_admin_user:
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = FacilityForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Facility added successfully!')
            return redirect('manage_facilities')
    else:
        form = FacilityForm()

    return render(request, 'bookings/facility_form.html', {'form': form, 'action': 'Add'})


@login_required
def edit_facility(request, pk):
    """Admin edit facility"""
    if not request.user.is_admin_user:
        return redirect('student_dashboard')

    facility = get_object_or_404(Facility, pk=pk)

    if request.method == 'POST':
        form = FacilityForm(request.POST, request.FILES, instance=facility)
        if form.is_valid():
            form.save()
            messages.success(request, 'Facility updated successfully!')
            return redirect('manage_facilities')
    else:
        form = FacilityForm(instance=facility)

    return render(request, 'bookings/facility_form.html', {'form': form, 'action': 'Edit', 'facility': facility})


@login_required
def delete_facility(request, pk):
    """Admin delete facility"""
    if not request.user.is_admin_user:
        return redirect('student_dashboard')

    facility = get_object_or_404(Facility, pk=pk)
    if request.method == 'POST':
        facility.delete()
        messages.success(request, 'Facility deleted successfully.')
        return redirect('manage_facilities')

    return render(request, 'bookings/confirm_delete.html', {'facility': facility})


@login_required
def add_announcement(request):
    """Admin add announcement"""
    if not request.user.is_admin_user:
        return redirect('student_dashboard')

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            Announcement.objects.create(title=title, content=content, created_by=request.user)
            messages.success(request, 'Announcement posted!')
        return redirect('admin_dashboard')

    return redirect('admin_dashboard')


def get_booked_slots(request, facility_pk):
    """API endpoint to get booked slots for a facility on a date"""
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'slots': []})

    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'slots': [], 'error': 'Invalid date'})

    bookings = Booking.objects.filter(
        facility_id=facility_pk,
        booking_date=date,
        status__in=['pending', 'approved']
    ).values('start_time', 'end_time', 'status')

    slots = [
        {
            'start': b['start_time'].strftime('%H:%M'),
            'end': b['end_time'].strftime('%H:%M'),
            'status': b['status']
        }
        for b in bookings
    ]
    return JsonResponse({'slots': slots})
