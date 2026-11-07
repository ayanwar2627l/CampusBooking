from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    registration_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    program = models.CharField(max_length=100, blank=True, null=True)
    year_of_study = models.IntegerField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.registration_number or self.username})"

    @property
    def is_admin_user(self):
        return self.role == 'admin' or self.is_staff

    @property
    def is_student_user(self):
        return self.role == 'student'
