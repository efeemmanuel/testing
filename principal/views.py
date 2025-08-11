from django.contrib.auth.decorators import login_required
from core.utils import role_required
from django.shortcuts import render, get_object_or_404, redirect
from core.models import User, TeacherProfile, ClassGroup, School, Message
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponseForbidden
from core.models import TeacherProfile, ClassGroup, ActivityLog
from .forms import *
from teacher.models import Student, Attendance
from django.utils import timezone
from .models import *
from datetime import date
from core.utils import can_enroll_teacher, can_enroll_student
from core.models import *
from django.core.paginator import Paginator
from django.db.models import Prefetch
from collections import Counter
from datetime import date, timedelta
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
User = get_user_model()
from django.http import JsonResponse
from django.views.decorators.http import require_POST








# dashboard views
@login_required
@role_required("PRINCIPAL")
def dashboard(request):
    principal = request.user.principal_profile
    school = principal.school
    today = timezone.localdate()

    # Subscription info
    subscription = SchoolSubscription.objects.get(school=school)
    plan = subscription.plan
    days_left = subscription.days_remaining()

    # Total students
    total_students = Student.objects.filter(school=school).count()

    # Attendance for today
    attendance_today = Attendance.objects.filter(student__school=school, date=today)
    total_present = attendance_today.filter(status="Present").count()
    total_absent = total_students - total_present

    # Recent activity logs
    recent_logs = ActivityLog.objects.select_related("user").order_by("-timestamp")[:4]

    # Per-class attendance summary
    class_summaries = []
    classgroups = ClassGroup.objects.filter(school=school)

    for classgroup in classgroups:
        students_in_class = Student.objects.filter(classgroup=classgroup)
        total_in_class = students_in_class.count()
        present_in_class = Attendance.objects.filter(
            student__in=students_in_class,
            date=today,
            status="Present"
        ).count()
        absent_in_class = total_in_class - present_in_class
        percentage = round((present_in_class / total_in_class * 100), 1) if total_in_class else 0

        class_summaries.append({
            "name": classgroup.name,
            "total": total_in_class,
            "present": present_in_class,
            "absent": absent_in_class,
            "percentage": percentage,
        })

    # Attendance by hour (for bar chart)
    attendance_times = attendance_today.filter(status="Present").values_list("time", flat=True)
    hour_counts = Counter([t.hour for t in attendance_times])
    hours = list(range(6, 16))  # From 6 AM to 3 PM
    attendance_by_hour = [hour_counts.get(h, 0) for h in hours]

    # Recent attendance trends (for PDF links)
    last_7_days = today - timedelta(days=6)
    recent_attendance = Attendance.objects.filter(student__school=school, date__range=(last_7_days, today))

    grouped_dates = recent_attendance.values("date").distinct().order_by("-date")
    daily_stats = []

    for entry in grouped_dates:
        d = entry["date"]
        present = recent_attendance.filter(date=d, status="Present").count()
        absent = total_students - present
        daily_stats.append({
            "date": d,
            "present": present,
            "absent": absent
        })

    context = {
        "total_students": total_students,
        "total_present": total_present,
        "total_absent": total_absent,
        "attendance_percent": round((total_present / total_students) * 100, 1) if total_students else 0,
        "class_summaries": class_summaries,
        "date": today,
        "recent_logs": recent_logs,
        "plan": plan,
        "days_left": days_left,
        "hours": hours,
        "attendance_by_hour": attendance_by_hour,
        "daily_stats": daily_stats,  
    }

    return render(request, "principal/dashboard.html", context)




# attendnace_pdf
@login_required
@role_required("PRINCIPAL")
def attendance_pdf(request, day):
    principal = request.user.principal_profile
    school = principal.school
    classgroups = ClassGroup.objects.filter(school=school)
    attendance = Attendance.objects.filter(student__school=school, date=day)

    class_data = []
    total_students = 0
    total_present = 0
    total_absent = 0

    for group in classgroups:
        students = Student.objects.filter(classgroup=group)
        total = students.count()
        present = attendance.filter(student__in=students, status="PRESENT").count()
        absent = total - present
        percentage = round((present / total * 100), 1) if total > 0 else 0

        total_students += total
        total_present += present
        total_absent += absent

        class_data.append({
            'name': group.name,
            'total': total,
            'present': present,
            'absent': absent,
            'percentage': percentage
        })

    context = {
        'school': school,
        'principal': principal,
        'date': day,
        'class_data': class_data,
        'total_students': total_students,
        'total_present': total_present,
        'total_absent': total_absent,
        'overall_percentage': round((total_present / total_students) * 100, 1) if total_students > 0 else 0,
    }

    template = get_template('principal/pdf_report.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="attendance_{day}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('PDF generation failed')
    return response





# manage teachers
@login_required
@role_required("PRINCIPAL")
def manage_teachers(request):
    principal = request.user.principal_profile
    school = principal.school

    search_query = request.GET.get("q", "")
    teachers_qs = TeacherProfile.objects.filter(school=school).select_related("user").prefetch_related("assigned_classes")

    if search_query:
        teachers_qs = teachers_qs.filter(user__email__icontains=search_query)

    paginator = Paginator(teachers_qs, 5)
    page_number = request.GET.get("page")
    teachers = paginator.get_page(page_number)

    try:
        subscription = SchoolSubscription.objects.get(school=school)
    except SchoolSubscription.DoesNotExist:
        messages.error(request, "Subscription not found.")
        return redirect("principal:upgrade_plan")

    if not subscription.is_active():
        messages.error(request, "Your subscription has expired.")
        return redirect("principal:upgrade_plan")

    # Handle edit form
    if request.method == "POST" and request.POST.get("edit_mode") == "true":
        user_id = request.POST.get("user_id")
        try:
            teacher = TeacherProfile.objects.get(user__id=user_id, school=school)
        except TeacherProfile.DoesNotExist:
            messages.error(request, "Teacher not found.")
            return redirect("principal:manage_teachers")

        teacher.teacher_fullname = request.POST.get("teacher_fullname")
        teacher.user.email = request.POST.get("email")
        teacher.user.save()

        class_ids = request.POST.getlist("assigned_classes[]")
        teacher.assigned_classes.set(class_ids)

        if request.FILES.get("profile_picture"):
            teacher.profile_picture = request.FILES["profile_picture"]

        teacher.save()

        ActivityLog.objects.create(
            user=request.user,
            action=f"Updated teacher: {teacher.user.email}"
        )

        messages.success(request, "Teacher updated successfully.")
        return redirect("principal:manage_teachers")

    # Handle enroll form
    elif request.method == "POST":
        if not can_enroll_teacher(school):
            messages.error(request, "You have reached the teacher limit.")
            return redirect("principal:manage_teachers")

        form = EnrollTeacherForm(request.POST, request.FILES, school=school)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            classgroups = form.cleaned_data["classgroup"]
            teacher_fullname = form.cleaned_data["teacher_fullname"]
            profile_picture = form.cleaned_data.get("profile_picture")

            if User.objects.filter(email=email).exists():
                messages.error(request, "User already exists.")
                return redirect("principal:manage_teachers")

            user = User.objects.create_user(email=email, password=password, role="TEACHER")
            teacher = TeacherProfile.objects.create(
                user=user, school=school, teacher_fullname=teacher_fullname, profile_picture=profile_picture
            )
            teacher.assigned_classes.set(classgroups)

            ActivityLog.objects.create(user=request.user, action=f"Enrolled teacher: {email}")
            messages.success(request, "Teacher enrolled successfully.")
            return redirect("principal:manage_teachers")
        else:
            messages.error(request, "There was an error with your form.")
    else:
        form = EnrollTeacherForm(school=school)

    classgroups = ClassGroup.objects.filter(school=school)
    can_enroll = can_enroll_teacher(school)

    return render(request, "principal/manage_teachers.html", {
        "form": form,
        "teachers": teachers,
        "classgroups": classgroups,
        "can_enroll_teacher": can_enroll,
        "search_query": search_query,
    })




# edit teachers
@login_required
@role_required("PRINCIPAL")
def edit_teacher(request, user_id):
    if request.method != "POST":
        return HttpResponseForbidden()

    user = get_object_or_404(User, id=user_id, role="TEACHER")
    teacher = get_object_or_404(TeacherProfile, user=user)
    school = request.user.principal_profile.school  

    form = EditTeacherForm(request.POST, request.FILES, instance=teacher, school=school) 

    if form.is_valid():
        teacher = form.save()
        email = request.POST.get("email")
        if email:
            user.email = email
            user.save()
        return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error", "errors": form.errors}, status=400)




# delete teachers
@login_required
@role_required("PRINCIPAL")
def delete_teacher(request, user_id):
    if request.method != "POST":
        return HttpResponseForbidden()

    user = get_object_or_404(User, id=user_id, role="TEACHER")
    email = user.email
    user.delete()

    # ✅ Log activity
    ActivityLog.objects.create(
        user=request.user,
        action=f"Deleted teacher: {email}"
    )

    return JsonResponse({"status": "deleted"})



# profile management
@login_required
@role_required("PRINCIPAL")
def profile_management(request):
    principal = request.user.principal_profile
    school = principal.school

    school_form = SchoolForm(instance=school)
    principal_user_form = PrincipalUserForm(instance=principal.user)
    principal_profile_form = PrincipalProfileForm(instance=principal)

    return render(request, "principal/profile_management.html", {
        "principal": principal,
        "school_form": school_form,
        "principal_user_form": principal_user_form,
        "principal_profile_form": principal_profile_form,
    })



# edit school
@login_required
@role_required("PRINCIPAL")
def edit_school(request):
    principal = request.user.principal_profile
    school = principal.school

    if request.method == "POST":
        form = SchoolForm(request.POST, request.FILES, instance=school)
        if form.is_valid():
            form.save()
    return redirect("principal:profile_management")



# edit principal
@login_required
@role_required("PRINCIPAL")
def edit_principal(request):
    user = request.user
    principal = user.principal_profile

    if request.method == "POST":
        user_form = PrincipalUserForm(request.POST, instance=user)
        profile_form = PrincipalProfileForm(request.POST, request.FILES, instance=principal)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

    return redirect("principal:profile_management")


# messages
@login_required
@role_required("PRINCIPAL")
def communication_center(request):
    principal = request.user.principal_profile
    school = principal.school
    teachers = TeacherProfile.objects.filter(school=school)
    form = MessageForm(school=school)

    if request.method == "POST" and request.headers.get("Hx-Request") != "true":
        form = MessageForm(request.POST, school=school)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            body = form.cleaned_data["body"]
            recipients = form.cleaned_data["recipients"]

            # 📨 One message for all or one individual teacher
            if recipients == "all":
                Message.objects.create(
                    sender=request.user,
                    recipient=None,
                    subject=subject,
                    body=body,
                )
            else:
                teacher = TeacherProfile.objects.get(id=recipients)
                Message.objects.create(
                    sender=request.user,
                    recipient=teacher.user,
                    subject=subject,
                    body=body,
                )

            messages.success(request, "Message sent successfully.")
            return redirect("principal:communication_center")
        else:
            messages.error(request, "Failed to send message. Please correct the errors below.")

 
    message_qs = Message.objects.filter(sender=request.user).order_by("-timestamp")
    paginator = Paginator(message_qs, 5)
    page = request.GET.get("page")
    messages_history = paginator.get_page(page)

    return render(request, "principal/communication_center.html", {
        "form": form,
        "teachers": teachers,
        "messages_history": messages_history,
        "page_obj": messages_history 
    })


# delete messages
@login_required
@role_required("PRINCIPAL")
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    message.delete()
    return JsonResponse({"status": "ok"})


# upgrade plan
@login_required
@role_required("PRINCIPAL")
def upgrade_plan(request):
    return render(request, "principal/upgrade_plan.html")





# create ticket
@login_required
@role_required("PRINCIPAL")  
def create_ticket(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.creator = request.user
            ticket.save()
            return redirect("principal:my_tickets")  
    else:
        form = TicketForm()
    return render(request, "principal/create_ticket.html", {"form": form})



# all my tickets
@login_required
@role_required("PRINCIPAL")
def my_tickets(request):
    tickets = (
        Ticket.objects
        .filter(creator=request.user)
    )
    return render(request, "principal/my_tickets.html", {"tickets": tickets})



# tickets details
@login_required
@role_required("PRINCIPAL")
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, creator=request.user)
    responses = ticket.responses.all()
    return render(request, "principal/ticket_detail.html", {
        "ticket": ticket,
        "responses": responses
    })


