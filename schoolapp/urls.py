from django.urls import path
from .import views
from django.contrib.auth.views import LogoutView
from .views import register_view, verify_otp_view




urlpatterns = [
    path('', views.register_view, name='register'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('add_student/', views.add_student_view, name='add_student'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('add-student/', views.add_student_view, name='add_student'),
    path('edit-student/<int:student_id>/', views.edit_student_view, name='edit_student'),
    path('delete-student/<int:student_id>/', views.delete_student_view, name='delete_student'),
    path('add-task/', views.add_task_view, name='add_task'),
    path('edit-task/<int:task_id>/', views.edit_task_view, name='edit_task'),
    path('delete-task/<int:task_id>/', views.delete_task_view, name='delete_task'),
    path('verify-otp/', verify_otp_view, name='verify_otp'),


]
