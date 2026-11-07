from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import StudentRegistrationForm, AdminRegistrationForm, CustomLoginForm, ProfileUpdateForm
from .models import CustomUser


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_student_user and not user.is_approved:
                messages.error(request, 'Your account is pending admin approval. Please wait.')
                return render(request, 'accounts/login.html', {'form': form})
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def student_register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Your account is pending admin approval.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentRegistrationForm()

    return render(request, 'accounts/student_register.html', {'form': form})


def admin_register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Admin account created successfully! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminRegistrationForm()

    return render(request, 'accounts/admin_register.html', {'form': form})


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def approve_student(request, user_id):
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    try:
        student = CustomUser.objects.get(id=user_id, role='student')
        student.is_approved = True
        student.save()
        messages.success(request, f'{student.get_full_name()} has been approved.')
    except CustomUser.DoesNotExist:
        messages.error(request, 'Student not found.')

    return redirect('admin_dashboard')


@login_required
def reject_student(request, user_id):
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    try:
        student = CustomUser.objects.get(id=user_id, role='student')
        student.delete()
        messages.success(request, 'Student registration rejected and removed.')
    except CustomUser.DoesNotExist:
        messages.error(request, 'Student not found.')

    return redirect('admin_dashboard')
