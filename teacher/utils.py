# teacher/utils.py
# helper that actually sends the mail

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone




# send email to parents when attendnace is marked
def send_parent_attendance_email(student, time_obj):
    """
    Sends an e‑mail to the student's parent/guardian when attendance is marked Present.
    """
    if not student.guardian_email:          # nothing to do
        return

    timestamp = timezone.localtime(time_obj)
    subject = f"🎓 {student.firstname} {student.lastname} marked PRESENT ({timestamp:%d %b %Y})"
    greeting = student.guardian_name or "Parent/Guardian"
    message = (
        f"Dear {greeting},\n\n"
        f"We are pleased to inform you that {student.firstname} {student.lastname} "
        f"was successfully marked present at {timestamp:%I:%M %p} on {timestamp:%A, %d %B %Y}.\n\n"
        f"Regards,\n{student.school.name} Attendance Desk"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [student.guardian_email],
        fail_silently=False,               # raise if mis‑configured
    )
