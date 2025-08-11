from django import forms
from core.models import TeacherProfile, ClassGroup, Ticket, PrincipalProfile,School, User
from django.contrib.auth import get_user_model
User = get_user_model()


class EnrollTeacherForm(forms.Form):
    teacher_fullname = forms.CharField(
        label="Full Name",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        label="Teacher Email",
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        label="Temporary Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    classgroup = forms.ModelMultipleChoiceField(
        label="Class Group(s)",
        queryset=ClassGroup.objects.none(),
        widget=forms.SelectMultiple(attrs={"class": "form-select", "multiple": "multiple"})
    )
    profile_picture = forms.ImageField(
        label="Profile Picture",
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control"})
    )

    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            self.fields["classgroup"].queryset = ClassGroup.objects.filter(school=school)


class EditTeacherForm(forms.ModelForm):
    assigned_classes = forms.ModelMultipleChoiceField(
        queryset=ClassGroup.objects.none(),
        widget=forms.SelectMultiple(attrs={"class": "form-select", "multiple": "multiple"}),
        required=False
    )

    class Meta:
        model = TeacherProfile
        fields = ["teacher_fullname", "profile_picture", "assigned_classes"]

    def __init__(self, *args, **kwargs):
        school = kwargs.pop("school", None)
        super().__init__(*args, **kwargs)
        if school:
            self.fields["assigned_classes"].queryset = ClassGroup.objects.filter(school=school)


class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ["name", "address", "email", "phone_number", "owner_name", "principal_name", "logo"]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-input', 'placeholder': 'Enter school name'}),
            'address': forms.TextInput(attrs={'class': 'form-control form-input', 'placeholder': 'Enter school address'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-input', 'placeholder': 'Enter school email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control form-input', 'placeholder': 'Enter school phone'}),
            'owner_name': forms.TextInput(attrs={'class': 'form-control form-input', 'placeholder': 'Enter owner name'}),
            'principal_name': forms.TextInput(attrs={'class': 'form-control form-input', 'placeholder': 'Enter principal name'}),
        }

class PrincipalUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email"]
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control form-input', 'placeholder': 'Enter email address'}),
        }

class PrincipalProfileForm(forms.ModelForm):
    class Meta:
        model = PrincipalProfile
        fields = ["first_name", "last_name", "phone_number", "profile_picture"]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control form-input', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-input', 'placeholder': 'Enter last name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control form-input', 'placeholder': 'Enter phone number'}),
        }


class MessageForm(forms.Form):
    RECIPIENT_CHOICES = [("all", "All Teachers")]

    subject = forms.CharField(
        label="Subject",
        max_length=255,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter subject"
        })
    )

    body = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 5,
            "placeholder": "Type your message..."
        })
    )

    recipients = forms.ChoiceField(
        label="Send To",
        choices=RECIPIENT_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )

    def __init__(self, *args, **kwargs):
        school = kwargs.pop("school", None)
        super().__init__(*args, **kwargs)
        if school:
            teachers = TeacherProfile.objects.filter(school=school).select_related("user")
            teacher_choices = [(teacher.id, teacher.user.email) for teacher in teachers]
            self.fields["recipients"].choices = [("all", "All Teachers")] + teacher_choices



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