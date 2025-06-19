from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=50)
    student_class = models.CharField(max_length=50)
    attendance = models.DecimalField(max_digits=5, decimal_places=2)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='created_students', null=True)

    def __str__(self):
        return f"{self.name} ({self.roll_number})"

class Subject(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=100)
    percentage = models.FloatField()

class Task(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
