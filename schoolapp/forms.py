from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Student, Subject
from django.forms.models import inlineformset_factory
from django import forms
from .models import Task



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'user_type']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = ''
        self.fields['username'].error_messages.update({
            'unique': 'This username already exists. Please choose another.'
        })
        self.fields['email'].error_messages.update({
            'unique': 'This email is already registered.'
        })

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'roll_number', 'student_class', 'attendance']
        widgets = {
            'attendance': forms.NumberInput(attrs={'placeholder': 'Enter attendance in %'})
        }

SubjectFormSet = inlineformset_factory(Student, Subject, fields=('name', 'percentage'), extra=1, can_delete=True)


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter task title'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter task description'}),
        }
