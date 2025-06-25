
from .models import CustomUser, Student, Subject
from django.forms.models import inlineformset_factory
from .models import Task
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'user_type']

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

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 9 or not re.search(r'[A-Za-z]', password1):
            raise ValidationError(
                "Password must be at least 9 characters long and contain at least one letter."
            )
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match.")


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


SubjectFormSet = inlineformset_factory(
    Student, Subject, fields=('name', 'percentage'), extra=1, can_delete=True
)