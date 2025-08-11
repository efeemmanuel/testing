from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
# Create your models here.



# users models 
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


# users model
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("SUPER_ADMIN", "Super Admin"),
        ("PRINCIPAL", "Principal"),
        ("TEACHER", "Teacher"),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} ({self.role})"
    
    def get_role_display(self):
        return dict(self.ROLE_CHOICES).get(self.role, self.role)





# super admin profile
class SuperAdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


    def __str__(self):
        return self.user


# school models 
class School(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    email = models.EmailField(null=True)
    phone_number = models.CharField(max_length=20, null=True)
    owner_name = models.CharField(max_length=255, null=True)
    principal_name = models.CharField(max_length=255, null=True)
    logo = models.ImageField(upload_to='school_logos/', null=True, blank=True)

    def __str__(self):
        return self.name



# principal models
class PrincipalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="principal_profile")
    school = models.OneToOneField(School, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=20, null=True)
    profile_picture = models.ImageField(upload_to='principal_profiles/', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



# teachers models 
class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile")
    teacher_fullname = models.CharField(max_length=255, null=True)
    profile_picture = models.ImageField(upload_to='teacher_profiles/', default='teacher_profiles/default.png')
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    assigned_classes = models.ManyToManyField("ClassGroup", blank=True, related_name="teachers")

    def __str__(self):
        return f"{self.teacher_fullname} {self.school}"


# classgroups models
class ClassGroup(models.Model):
    name = models.CharField(max_length=255)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.school.name}"



# activity log models
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email if self.user else 'System'} – {self.action} – {self.timestamp}"
    

# message models 
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sent_messages")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages", null=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"To {self.recipient.email} – {self.subject}"




# plans models
class Plan(models.Model):
    PLAN_CHOICES = [
        ("FREEMIUM", "Freemium"),
        ("PREMIUM", "Premium"),
        ("PLATINUM", "Platinum"),
    ]

    name = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)  # e.g., $2.00
    duration_days = models.IntegerField()  # 7 for freemium trial, 120 for 4-month plan
    max_teachers = models.IntegerField(null=True, blank=True)  # None = unlimited
    max_students = models.IntegerField(null=True, blank=True)  # None = unlimited
    has_email_notifications = models.BooleanField(default=False)
    has_sms_notifications = models.BooleanField(default=False)
    has_advanced_reports = models.BooleanField(default=False)
    has_ml_analytics = models.BooleanField(default=False)
    has_custom_branding = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    

# school plan models
class SchoolSubscription(models.Model):
    school = models.OneToOneField("School", on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField()

    def is_active(self):
        return self.expiry_date >= timezone.now().date()

    def days_remaining(self):
        return max((self.expiry_date - timezone.now().date()).days, 0)

    def __str__(self):
        return f"{self.school.name} - {self.plan.name}"


# super admin create ticket model
class Ticket(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("IN_PROGRESS", "In Progress"),
        ("RESOLVED", "Resolved"),
        ("CLOSED", "Closed"),
    ]

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="OPEN")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TicketResponse(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="responses")
    responder = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.responder} - {self.ticket}"