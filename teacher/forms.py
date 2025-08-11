from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import *
from core.models import *


class StudentEnrollmentForm(forms.ModelForm):
    fingerprint_data = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model  = Student
        fields = [
            "admission_id",
            "firstname",
            "lastname",
            "date_of_birth",
            "classgroup",
            "guardian_name",
            "guardian_email",
            "guardian_phone",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            
            "classgroup": forms.Select(attrs={
                "class": "form-select classgroup-select"
            }),
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'status']


class StudentEditForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "admission_id",
            "firstname",
            "lastname",
            "date_of_birth",
            "classgroup",
            "guardian_name",
            "guardian_email",
            "guardian_phone",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }



class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["subject", "message"]
        widgets = {
            "subject": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter the subject of your issue"
            }),
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Describe your issue in detail…"
            }),
        }