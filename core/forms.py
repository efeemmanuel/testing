# core/forms.py
from django.contrib.auth.forms import AuthenticationForm
from django import forms


# login form
class EmailAuthForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "autofocus": True,
            "class": "form-control",
            "placeholder": "Email",
            "style": (
                "width: 100%; padding: 14px; border-radius: 8px; border: none; "
                "background-color: #333; color: #fff; font-size: 1rem;"
            )
        })
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password",
            "style": (
                "width: 100%; padding: 14px; border-radius: 8px; border: none; "
                "background-color: #333; color: #fff; font-size: 1rem;"
            )
        })
    )