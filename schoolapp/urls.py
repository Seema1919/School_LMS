from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Authentication & OTP
    path('', views.register, name='register'),  # default page
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('verify_email/<slug:username>/', views.verify_email, name='verify_email'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),

    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Student Management
    path('add-student/', views.add_student_view, name='add_student'),
    path('edit-student/<int:student_id>/', views.edit_student_view, name='edit_student'),

    # Task Management
    path('add-task/', views.add_task_view, name='add_task'),
    path('edit-task/<int:task_id>/', views.edit_task_view, name='edit_task'),
    path('delete-task/<int:task_id>/', views.delete_task_view, name='delete_task'),
]
