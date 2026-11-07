from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class StudentRegistrationForm(UserCreationForm):
    DEPARTMENT_CHOICES = [
        ('', 'Select Department'),
        ('CSE', 'Computer Science & Engineering'),
        ('ECE', 'Electronics & Communication Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('CE', 'Civil Engineering'),
        ('EE', 'Electrical Engineering'),
        ('IT', 'Information Technology'),
        ('BBA', 'Business Administration'),
        ('MBA', 'Master of Business Administration'),
        ('BA', 'Bachelor of Arts'),
        ('BCA', 'Bachelor of Computer Applications'),
        ('MCA', 'Master of Computer Applications'),
        ('BSc', 'Bachelor of Science'),
        ('Other', 'Other'),
    ]

    PROGRAM_CHOICES = [
        ('', 'Select Program'),
        ('B.Tech', 'B.Tech'),
        ('M.Tech', 'M.Tech'),
        ('BBA', 'BBA'),
        ('MBA', 'MBA'),
        ('BCA', 'BCA'),
        ('MCA', 'MCA'),
        ('B.Sc', 'B.Sc'),
        ('M.Sc', 'M.Sc'),
        ('BA', 'BA'),
        ('MA', 'MA'),
        ('Ph.D', 'Ph.D'),
        ('Other', 'Other'),
    ]

    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    registration_number = forms.CharField(max_length=20, required=True,
                                           help_text='Your LPU Registration Number (e.g., 12345678)')
    phone_number = forms.CharField(max_length=15, required=True)
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, required=True)
    program = forms.ChoiceField(choices=PROGRAM_CHOICES, required=True)
    year_of_study = forms.IntegerField(min_value=1, max_value=6, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email',
                  'registration_number', 'phone_number', 'department',
                  'program', 'year_of_study', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['year_of_study'].widget.attrs.update({'min': 1, 'max': 6})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        user.is_approved = False
        if commit:
            user.save()
        return user


class AdminRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    department = forms.CharField(max_length=100, required=True)
    admin_code = forms.CharField(max_length=20, required=True,
                                  help_text='Admin registration code provided by DSW')

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email',
                  'phone_number', 'department', 'password1', 'password2']

    ADMIN_SECRET_CODE = 'LPU-ADMIN-2024'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_admin_code(self):
        code = self.cleaned_data.get('admin_code')
        if code != self.ADMIN_SECRET_CODE:
            raise forms.ValidationError("Invalid admin registration code.")
        return code

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'admin'
        user.is_staff = True
        user.is_approved = True
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username or Registration No.'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number',
                  'department', 'program', 'year_of_study', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
