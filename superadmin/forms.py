from django import forms
from core.models import School
from teacher.models import *
from core.models import *


class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['name', 'address','email','phone_number','owner_name','principal_name','logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control','rows': 3}),
            'email': forms.Textarea(attrs={'class': 'form-control'}),
            'phone_number': forms.Textarea(attrs={'class': 'form-control'}),
            'owner_name': forms.Textarea(attrs={'class': 'form-control'}),
            'principal_name': forms.Textarea(attrs={'class': 'form-control'}),
        }





class ClassGroupForm(forms.ModelForm):
    class Meta:
        model = ClassGroup
        fields = ['name', 'school']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'school': forms.Select(attrs={'class': 'form-control'})
        }






class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "admission_id",
            "firstname",
            "lastname",
            "date_of_birth",
            "guardian_name",
            "guardian_email",
            "guardian_phone",
            "school",
            "classgroup",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["classgroup"].queryset = ClassGroup.objects.select_related("school").all()

# duperadmin forms 
class TicketResponseForm(forms.ModelForm):
    class Meta:
        model = TicketResponse
        fields = ["message"]



class PrincipalForm(forms.ModelForm):
    class Meta:
        model = PrincipalProfile
        fields = ['first_name', 'last_name', 'phone_number', 'profile_picture', 'school']
        widgets = {
            'school': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }






class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = [
            "name", "price", "duration_days",
            "max_teachers", "max_students",
            "has_email_notifications", "has_sms_notifications",
            "has_advanced_reports", "has_ml_analytics",
            "has_custom_branding"
        ]



class SchoolSubscriptionForm(forms.ModelForm):
    class Meta:
        model = SchoolSubscription
        fields = ['school', 'plan', 'expiry_date']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super(SchoolSubscriptionForm, self).__init__(*args, **kwargs)
        self.fields['school'].queryset = School.objects.all()
        self.fields['plan'].queryset = Plan.objects.all()



class SuperAdminMessageForm(forms.Form):
    recipient = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True), label="Send To")
    subject = forms.CharField(max_length=255)
    body = forms.CharField(widget=forms.Textarea)