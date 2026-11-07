from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/student/', views.student_register, name='student_register'),
    path('register/admin/', views.admin_register, name='admin_register'),
    path('profile/', views.profile_view, name='profile'),
    path('approve/<int:user_id>/', views.approve_student, name='approve_student'),
    path('reject/<int:user_id>/', views.reject_student, name='reject_student'),
]
