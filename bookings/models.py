from django.db import models
from django.conf import settings
from django.utils import timezone


class Facility(models.Model):
    FACILITY_TYPES = [
        ('computer_lab', 'Computer Lab'),
        ('mac_lab', 'Mac Lab'),
        ('electronics_lab', 'Electronics Lab'),
        ('seminar_hall', 'Seminar Hall'),
        ('auditorium', 'Auditorium'),
        ('dsw_room', 'DSW Room'),
        ('conference_room', 'Conference Room'),
        ('project_room', 'Project Room'),
    ]

    BLOCK_CHOICES = [
        ('Block-1', 'Block 1'),
        ('Block-2', 'Block 2'),
        ('Block-3', 'Block 3'),
        ('Block-4', 'Block 4'),
        ('Block-5', 'Block 5'),
        ('Block-6', 'Block 6'),
        ('Block-7', 'Block 7'),
        ('Block-8', 'Block 8'),
        ('Block-9', 'Block 9'),
        ('Block-10', 'Block 10'),
        ('Shanti-Devi', 'Shanti Devi Block'),
        ('UniPro', 'UniPro Block'),
        ('Auditorium', 'Auditorium Complex'),
        ('DSW', 'DSW Block'),
        ('Main-Block', 'Main Block'),
    ]

    name = models.CharField(max_length=200)
    facility_type = models.CharField(max_length=50, choices=FACILITY_TYPES)
    block = models.CharField(max_length=50, choices=BLOCK_CHOICES)
    floor = models.CharField(max_length=20, blank=True)
    room_number = models.CharField(max_length=20, blank=True)
    capacity = models.IntegerField(default=30)
    description = models.TextField(blank=True)
    amenities = models.TextField(blank=True, help_text='Comma-separated list of amenities')
    image = models.ImageField(upload_to='facilities/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    booking_advance_days = models.IntegerField(default=7, help_text='Max days in advance to book')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Facilities'
        ordering = ['facility_type', 'name']

    def __str__(self):
        return f"{self.name} - {self.block}"

    def get_amenities_list(self):
        if self.amenities:
            return [a.strip() for a in self.amenities.split(',')]
        return []

    @property
    def facility_type_icon(self):
        icons = {
            'computer_lab': 'fa-desktop',
            'mac_lab': 'fa-apple-alt',
            'electronics_lab': 'fa-microchip',
            'seminar_hall': 'fa-chalkboard-teacher',
            'auditorium': 'fa-theater-masks',
            'dsw_room': 'fa-door-open',
            'conference_room': 'fa-users',
            'project_room': 'fa-project-diagram',
        }
        return icons.get(self.facility_type, 'fa-building')


class TimeSlot(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='time_slots')
    start_time = models.TimeField()
    end_time = models.TimeField()
    label = models.CharField(max_length=50, blank=True, help_text='e.g., Morning, Afternoon')

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.facility.name}: {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    PURPOSE_CHOICES = [
        ('class', 'Regular Class'),
        ('lab_session', 'Lab Session'),
        ('club_activity', 'Club Activity'),
        ('event', 'Event/Function'),
        ('workshop', 'Workshop/Seminar'),
        ('exam', 'Examination'),
        ('project_work', 'Project Work'),
        ('cultural', 'Cultural Activity'),
        ('sports', 'Sports Activity'),
        ('meeting', 'Meeting/Conference'),
        ('other', 'Other'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES)
    purpose_description = models.TextField(help_text='Detailed description of the event/activity')
    expected_attendees = models.IntegerField(default=1)
    club_name = models.CharField(max_length=100, blank=True, null=True, help_text='If booking for club activity')
    event_name = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.facility.name} - {self.booking_date} - {self.student.get_full_name()}"

    @property
    def is_upcoming(self):
        return self.booking_date >= timezone.now().date() and self.status == 'approved'

    @property
    def status_color(self):
        colors = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'cancelled': 'secondary',
            'completed': 'info',
        }
        return colors.get(self.status, 'secondary')


class BookingDocument(models.Model):
    DOC_TYPES = [
        ('portfolio', 'Portfolio of Work'),
        ('enrollment', 'Registration/Enrollment Proof'),
        ('undertaking', 'Undertaking'),
        ('supporting', 'Supporting Document'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=30, choices=DOC_TYPES)
    document = models.FileField(upload_to='booking_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.booking} - {self.get_doc_type_display()}"


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
