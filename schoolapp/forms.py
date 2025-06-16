from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(
        max_length=150,
        required=True,
        label="Username",
        help_text=""
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'user_type']

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 10:
            raise forms.ValidationError("Password must be at least 10 characters long.")
        return password
