from django.shortcuts import render

# Create your views here.





from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.utils import role_required

from django.shortcuts import render
from core.models import *
from teacher.models import Student  # update this if your Student model lives elsewhere
from django.shortcuts import render, get_object_or_404, redirect

from core.models import School
from .forms import *
from django.http import JsonResponse
from django.contrib import messages


from django.http import JsonResponse
import json






@login_required
@role_required("SUPER_ADMIN")
def dashboard(request):
    total_schools = School.objects.count()
    total_teachers = TeacherProfile.objects.count()
    total_students = Student.objects.count()

    context = {
        "total_schools": total_schools,
        "total_teachers": total_teachers,
        "total_students": total_students,
    }
    return render(request, "superadmin/dashboard.html", context)







@login_required
@role_required("SUPER_ADMIN")
def manage_schools(request):
    form = SchoolForm(request.POST or None)

    if request.method == "POST" and "school_id" not in request.POST:
        if form.is_valid():
            form.save()
            messages.success(request, "School added successfully.")
            return redirect("superadmin:manage_schools")  # Prevent resubmission on refresh
        else:
            messages.error(request, "Please correct the errors below.")

    schools = School.objects.all()
    return render(request, "superadmin/manage_schools.html", {
        "schools": schools,
        "form": form
    })




@login_required
@role_required("SUPER_ADMIN")
def edit_school(request, school_id):
    school = get_object_or_404(School, id=school_id)

    if request.method == "POST":
        form = SchoolForm(request.POST, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, "School updated successfully.")
        else:
            messages.error(request, "Please correct the errors.")
    return redirect("superadmin:manage_schools")



@login_required
@role_required("SUPER_ADMIN")
def delete_school(request, school_id):
    school = get_object_or_404(School, id=school_id)
    school.delete()
    messages.success(request, "School deleted successfully.")
    return redirect("superadmin:manage_schools")













@login_required
@role_required("SUPER_ADMIN")
def manage_classgroups(request):
    if request.method == "POST" and "classgroup_id" not in request.POST:
        form = ClassGroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Class group created successfully.")
            return redirect("superadmin:manage_classgroups")
        else:
            messages.error(request, "Failed to create class group.")
    
    classgroups = ClassGroup.objects.select_related('school').all()
    schools = School.objects.all()
    return render(request, "superadmin/manage_classgroups.html", {
        "classgroups": classgroups,
        "schools": schools,
    })


@login_required
@role_required("SUPER_ADMIN")
def edit_classgroup(request, classgroup_id):
    classgroup = get_object_or_404(ClassGroup, id=classgroup_id)
    if request.method == "POST":
        form = ClassGroupForm(request.POST, instance=classgroup)
        if form.is_valid():
            form.save()
            messages.success(request, "Class group updated successfully.")
        else:
            messages.error(request, "Failed to update class group.")
    return redirect("superadmin:manage_classgroups")


@login_required
@role_required("SUPER_ADMIN")
def delete_classgroup(request, classgroup_id):
    classgroup = get_object_or_404(ClassGroup, id=classgroup_id)
    classgroup.delete()
    messages.success(request, "Class group deleted successfully.")
    return redirect("superadmin:manage_classgroups")





















@login_required
@role_required("SUPER_ADMIN")
def manage_teachers(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        classgroup_id = request.POST.get("classgroup")
        school_id = request.POST.get("school_id")

        # ✅ Check for duplicate email
        if User.objects.filter(email=email).exists():
            messages.error(request, "A user with this email already exists.")
            return redirect("superadmin:manage_teachers")

        # ✅ Fetch school and classgroup
        school = get_object_or_404(School, id=school_id)
        classgroup = get_object_or_404(ClassGroup, id=classgroup_id)

        # ✅ Create user and teacher profile
        user = User.objects.create_user(email=email, password=password, role="TEACHER")
        teacher = TeacherProfile.objects.create(user=user, school=school)
        teacher.assigned_classes.set([classgroup])

        messages.success(request, "Teacher enrolled successfully.")
        return redirect("superadmin:manage_teachers")

    # GET method: load data
    schools = School.objects.all()
    classgroups = ClassGroup.objects.select_related("school")
    teachers = TeacherProfile.objects.select_related("user", "school").prefetch_related("assigned_classes")

    return render(request, "superadmin/manage_teachers.html", {
        "schools": schools,
        "classgroups": classgroups,
        "teachers": teachers
    })


@login_required
@role_required("SUPER_ADMIN")
def edit_teacher(request, user_id):
    teacher = get_object_or_404(TeacherProfile, user__id=user_id)

    if request.method == "POST":
        classgroup_ids = request.POST.getlist("edit_classgroup")  # multiple select
        teacher_fullname = request.POST.get("fullname")
        school_id = request.POST.get("school_id")

        teacher.teacher_fullname = teacher_fullname
        teacher.school_id = school_id
        teacher.assigned_classes.set(classgroup_ids)
        teacher.save()

        messages.success(request, "Teacher updated successfully.")
    else:
        messages.error(request, "Invalid method.")

    return redirect("superadmin:manage_teachers")


@login_required
@role_required("SUPER_ADMIN")
def delete_teacher(request, user_id):
    teacher = get_object_or_404(TeacherProfile, user__id=user_id)
    teacher.user.delete()
    messages.success(request, "Teacher deleted successfully.")
    return redirect("superadmin:manage_teachers")








@login_required
@role_required("SUPER_ADMIN")
def manage_students(request):
    students = Student.objects.select_related("school", "classgroup").all()
    schools = School.objects.all()
    form = StudentForm()

    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Student enrolled successfully.")
            return redirect("superadmin:manage_students")
        else:
            messages.error(request, "Failed to enroll student. Please check the form.")

    return render(request, "superadmin/manage_students.html", {
        "students": students,
        "schools": schools,
        "form": form,
    })

@login_required
@role_required("SUPER_ADMIN")
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully.")
        else:
            messages.error(request, "Failed to update student.")
        return redirect("superadmin:manage_students")

@login_required
@role_required("SUPER_ADMIN")
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    messages.success(request, "Student deleted.")
    return redirect("superadmin:manage_students")


@login_required
@role_required("SUPER_ADMIN")
def manage_plans(request):
    plans = Plan.objects.all()

    if request.method == "POST":
        plan_id = request.POST.get("plan_id")
        plan = get_object_or_404(Plan, id=plan_id)

        plan.price = request.POST.get("price")
        plan.duration_days = request.POST.get("duration_days")
        plan.max_teachers = request.POST.get("max_teachers") or None
        plan.max_students = request.POST.get("max_students") or None
        plan.has_email_notifications = bool(request.POST.get("has_email_notifications"))
        plan.has_sms_notifications = bool(request.POST.get("has_sms_notifications"))
        plan.has_advanced_reports = bool(request.POST.get("has_advanced_reports"))
        plan.has_ml_analytics = bool(request.POST.get("has_ml_analytics"))
        plan.has_custom_branding = bool(request.POST.get("has_custom_branding"))

        plan.save()
        messages.success(request, "Plan updated successfully.")
        return redirect("superadmin:manage_plans")

    return render(request, "superadmin/manage_plans.html", {
        "plans": plans
    })


@login_required
@role_required("SUPER_ADMIN")
def delete_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    if request.method == "POST":
        plan.delete()
        messages.success(request, "Plan deleted successfully.")
    return redirect("superadmin:manage_plans")



from datetime import datetime

@login_required
@role_required("SUPER_ADMIN")
def manage_school_subscriptions(request):
    subscriptions = SchoolSubscription.objects.select_related("school", "plan").all()
    plans = Plan.objects.all()
    return render(request, "superadmin/manage_subscriptions.html", {
        "subscriptions": subscriptions,
        "plans": plans,
    })


@login_required
@role_required("SUPER_ADMIN")
def update_school_subscription(request, sub_id):
    subscription = get_object_or_404(SchoolSubscription, id=sub_id)

    if request.method == "POST":
        plan_id = request.POST.get("plan")
        expiry_date = request.POST.get("expiry_date")

        try:
            subscription.plan = Plan.objects.get(id=plan_id)
            subscription.expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
            subscription.save()
            messages.success(request, "Subscription updated successfully.")
        except Exception as e:
            messages.error(request, f"Error updating subscription: {str(e)}")

    return redirect("superadmin:manage_school_subscriptions")






@login_required
@role_required("SUPER_ADMIN")
def manage_principals(request):
    if request.method == 'POST':
        # Creating new principal from modal
        email = request.POST.get("email")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone_number")
        school_id = request.POST.get("school")
        profile_picture = request.FILES.get("profile_picture")

        try:
            # Ensure email is unique
            if User.objects.filter(username=email).exists():
                messages.error(request, "A user with this email already exists.")
            else:
                user = User.objects.create_user(username=email, email=email, password=password)
                school = School.objects.get(id=school_id)
                PrincipalProfile.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    profile_picture=profile_picture,
                    school=school
                )
                messages.success(request, "Principal created successfully.")
        except Exception as e:
            messages.error(request, f"Error creating principal: {str(e)}")

        return redirect("superadmin:manage_principals")  # Avoid duplicate POST if refreshed

    # GET request: just show the page
    principals = PrincipalProfile.objects.select_related('school', 'user')
    schools = School.objects.all()
    return render(request, "superadmin/manage_principals.html", {
        "principals": principals,
        "schools": schools,
    })



@login_required
@role_required("SUPER_ADMIN")
def update_principal(request, pk):
    principal = get_object_or_404(PrincipalProfile, pk=pk)

    if request.method == 'POST':
        principal.first_name = request.POST.get('first_name')
        principal.last_name = request.POST.get('last_name')
        principal.phone_number = request.POST.get('phone_number')
        school_id = request.POST.get('school')
        
        if school_id:
            principal.school = School.objects.get(id=school_id)

        if 'profile_picture' in request.FILES:
            principal.profile_picture = request.FILES['profile_picture']

        principal.save()
        messages.success(request, "Principal updated successfully.")

    return redirect("superadmin:manage_principals")



@login_required
@role_required("SUPER_ADMIN")
def delete_principal(request, pk):
    principal = get_object_or_404(PrincipalProfile, pk=pk)
    if request.method == 'POST':
        principal.user.delete()  # Delete associated user
        principal.delete()
        messages.success(request, "Principal deleted.")
    return redirect("superadmin:manage_principals")











@login_required
@role_required("SUPER_ADMIN")
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    responses = ticket.responses.all()

    if request.method == "POST":
        form = TicketResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.ticket = ticket
            response.responder = request.user
            response.save()
            ticket.status = request.POST.get("status", ticket.status)
            ticket.save()
            return redirect("superadmin:ticket_detail", ticket_id=ticket.id)
    else:
        form = TicketResponseForm()

    return render(request, "superadmin/ticket_detail.html", {
        "ticket": ticket,
        "responses": responses,
        "form": form,
        "status_choices": Ticket.STATUS_CHOICES,
    })






from datetime import timedelta

@login_required
@role_required("SUPER_ADMIN")
def all_tickets(request):
    tickets = Ticket.objects.all().order_by("-created_at")
    twelve_hours_ago = timezone.now() - timedelta(hours=12)

    context = {
        "tickets": tickets,
        "total_count": tickets.count(),
        "new_count": tickets.filter(created_at__gte=twelve_hours_ago).count(),
        "in_progress_count": tickets.filter(status="IN_PROGRESS").count(),
        "resolved_count": tickets.filter(status="RESOLVED").count(),
        "status_choices": Ticket.STATUS_CHOICES,
        "form": TicketResponseForm(),  # needed inside modal
    }
    return render(request, "superadmin/all_tickets.html", context)




@login_required
@role_required("SUPER_ADMIN")
def update_ticket_status(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    new_status = request.POST.get("status")
    if new_status in dict(Ticket.STATUS_CHOICES).keys():
        ticket.status = new_status
        ticket.save()
        messages.success(request, "Ticket status updated.")
    else:
        messages.error(request, "Invalid status.")
    return redirect("superadmin:all_tickets")



@login_required
def send_message(request):
    if request.method == "POST":
        form = SuperAdminMessageForm(request.POST)
        if form.is_valid():
            message = Message(
                sender=request.user,
                recipient=form.cleaned_data["recipient"],
                subject=form.cleaned_data["subject"],
                body=form.cleaned_data["body"],
            )
            message.save()
            return redirect("superadmin:send_message")  # or any success page
    else:
        form = SuperAdminMessageForm()
    return render(request, "superadmin/send_message.html", {"form": form})