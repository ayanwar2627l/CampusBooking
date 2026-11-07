from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'get_full_name', 'email', 'role', 'registration_number', 'is_approved', 'created_at']
    list_filter = ['role', 'is_approved', 'department']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'registration_number']
    actions = ['approve_users']

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'{queryset.count()} user(s) approved.')
    approve_users.short_description = 'Approve selected users'
