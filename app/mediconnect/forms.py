from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import MedicalDocument


class RegisterForm(UserCreationForm):
    ROLE_CHOICES = [
        ("user", "User"),
        ("doctor", "Doctor"),
        ("hospital", "Hospital"),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label="Register As",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = User
        fields = ["username", "email", "role", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "password1": forms.PasswordInput(attrs={"class": "form-control"}),
            "password2": forms.PasswordInput(attrs={"class": "form-control"}),
        }


class MedicalDocumentForm(forms.ModelForm):
    class Meta:
        model = MedicalDocument
        fields = ["document"]
