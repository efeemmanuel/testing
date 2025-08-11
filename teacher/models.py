from django.db import models
from core.models import School, ClassGroup  


class Student(models.Model):
    admission_id      = models.CharField(max_length=30, unique=True, blank=True, null=True)
    firstname         = models.CharField(max_length=60)
    lastname          = models.CharField(max_length=60)
    date_of_birth     = models.DateField(null=True, blank=True)
    guardian_name     = models.CharField(max_length=120, null=True, blank=True)
    guardian_email    = models.EmailField(null=True, blank=True)
    guardian_phone    = models.CharField(max_length=30, null=True, blank=True)
    # biometrics
    fingerprint_data  = models.TextField(null=True, blank=True)
    # relations
    school            = models.ForeignKey(School,     on_delete=models.CASCADE)
    classgroup        = models.ForeignKey(ClassGroup, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"



class Attendance(models.Model):
    STATUS_CHOICES = [("Present", "Present"), ("Absent", "Absent")]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date    = models.DateField()
    time    = models.TimeField()
    status  = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ("student", "date")

    def __str__(self):
        return f"{self.student} – {self.date} – {self.status}"
