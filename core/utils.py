from django.http import HttpResponseForbidden
from core.models import SchoolSubscription, TeacherProfile
from teacher.models import Student


# role required decorator
def role_required(expected_role):
    def decorator(view_func):
        def _wrapped(request, *args, **kwargs):
            print("User role:", request.user.role)
            if request.user.role != expected_role:
                return HttpResponseForbidden("Forbidden")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator






# functions for subscription plans
# def for enroll teachers based on plans
def can_enroll_teacher(school):
    subscription = SchoolSubscription.objects.get(school=school)
    plan = subscription.plan
    if plan.max_teachers is None:
        return True  # Unlimited
    current_teacher_count = TeacherProfile.objects.filter(school=school).count()
    return current_teacher_count < plan.max_teachers


# def for enroll students based on plans
def can_enroll_student(school):
    try:
        subscription = SchoolSubscription.objects.get(school=school)
        if not subscription.is_active():
            return False

        plan = subscription.plan
        if plan.max_students is None:
            return True  # Unlimited students allowed

        current_count = Student.objects.filter(classgroup__school=school).count()
        return current_count < plan.max_students
    except SchoolSubscription.DoesNotExist:
        return False  # No subscription at all
