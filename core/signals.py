# core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, SuperAdminProfile, PrincipalProfile, TeacherProfile
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from core.models import ActivityLog





@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == "SUPER_ADMIN":
            SuperAdminProfile.objects.create(user=instance)
        elif instance.role == "PRINCIPAL":
            PrincipalProfile.objects.create(user=instance)
        elif instance.role == "TEACHER":
            TeacherProfile.objects.create(user=instance)



# this is for activities
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ActivityLog.objects.create(user=user, action="Logged in")


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ActivityLog.objects.create(
        user=user,
        action=f"{user.get_role_display()} logged in"
    )