from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Attendance
from core.models import SchoolSubscription
from .utils import send_parent_attendance_email

# trigger e‑mail whenever a new “Present” row is created
@receiver(post_save, sender=Attendance)
def notify_parent_on_present(sender, instance, created, **kwargs):
    if created and instance.status == "Present":
        school = instance.student.school

        #Check if the school's plan allows email notifications
        try:
            subscription = SchoolSubscription.objects.get(school=school)
            if not subscription.plan.has_email_notifications:
                return  #Skip email if plan doesn’t support it
        except SchoolSubscription.DoesNotExist:
            return  #No subscription found; don't send

        when = timezone.now().replace(
            hour=instance.time.hour,
            minute=instance.time.minute,
            second=instance.time.second,
            microsecond=0,
        )
        send_parent_attendance_email(instance.student, when)