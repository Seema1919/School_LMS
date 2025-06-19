from django.urls import path
from .import views

urlpatterns = [
    path('', views.register_view, name='register'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('add-student/', views.add_student_view, name='add_student'),

]
