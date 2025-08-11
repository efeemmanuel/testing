from django.contrib import admin
from .models import SuperAdminProfile, School , PrincipalProfile, TeacherProfile, ClassGroup, Message, ActivityLog, Plan, SchoolSubscription, Ticket, TicketResponse

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
# , School, ClassGroup, SuperAdminProfile, PrincipalProfile, TeacherProfile



# Register your models here.



admin.site.register(SuperAdminProfile)
admin.site.register(School)
admin.site.register(PrincipalProfile)
admin.site.register(TeacherProfile)
admin.site.register(ClassGroup)
admin.site.register(Message)
admin.site.register(ActivityLog)
admin.site.register(Plan)
admin.site.register(SchoolSubscription)
admin.site.register(Ticket)
admin.site.register(TicketResponse)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("email", "role", "is_staff", "is_active")
    list_filter  = ("role", "is_staff", "is_active")
    search_fields = ("email",)
    fieldsets = (
        (None,               {"fields": ("email", "password")}),
        ("Permissions",      {"fields": ("role", "is_active", "is_staff", "is_superuser")}),
        ("Important dates",  {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "role", "password1", "password2", "is_staff", "is_active"),
        }),
    )