from django.shortcuts import render, get_object_or_404, redirect
from core.utils import role_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, FileResponse
from .models import *
from .forms import *
from django.contrib import messages
from datetime import date
import requests
import datetime, io, requests
from core.models import TeacherProfile   
from teacher.models import Student, Attendance
from django.db.models import Count, Q
from core.utils import can_enroll_student
from xhtml2pdf import pisa
import datetime  
from collections import Counter
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet
from django.template.loader import get_template
from django.http import HttpResponse






@login_required
@role_required("TEACHER")
def dashboard(request):
    teacher = request.user.teacher_profile
    school = teacher.school
    today = date.today()

    # All students across all classes the teacher is assigned to
    students_qs = Student.objects.filter(classgroup__in=teacher.assigned_classes.all())

    unread_count = Message.objects.filter(recipient=request.user, is_read=False).count()

    subscription = SchoolSubscription.objects.filter(school=teacher.school).first()
    has_email = subscription and subscription.plan and subscription.plan.has_email_notifications

    #Enforce subscription plan limits
    subscription = SchoolSubscription.objects.get(school=school)
    if not subscription.is_active():
        messages.error(request, "Your subscription has expired. Upgrade to enroll more students.")
        return redirect("teacher:dashboard")

    # Handle enrollment form
    if request.method == "POST":
        if not can_enroll_student(school):
            messages.error(request, "You’ve reached your student limit. Upgrade to enroll more students.")
            return redirect("teacher:dashboard")

        form = StudentEnrollmentForm(request.POST)
        form.fields['classgroup'].queryset = teacher.assigned_classes.all()

        if form.is_valid():
            student = form.save(commit=False)
            student.school = teacher.school
            student.classgroup = form.cleaned_data.get("classgroup")
            student.fingerprint_data = form.cleaned_data.get("fingerprint_data")
            student.save()
            messages.success(request, "Student enrolled successfully.")
            return redirect("teacher:dashboard")
    else:
        form = StudentEnrollmentForm()
        form.fields['classgroup'].queryset = teacher.assigned_classes.all()

    # Metrics
    total_students = students_qs.count()
    present_today_count = Attendance.objects.filter(
        student__classgroup__in=teacher.assigned_classes.all(),
        date=today,
        status="Present"
    ).count()

    class_count = Student.objects.filter(
        school=teacher.school,
        classgroup__in=teacher.assigned_classes.all()
    ).values("classgroup").distinct().count()

    recent_attendance = Attendance.objects.filter(
        student__classgroup__in=teacher.assigned_classes.all()
    ).select_related("student").order_by("-date")[:4]

    daily_stats = Attendance.objects.filter(
        student__classgroup__in=teacher.assigned_classes.all()
    ).values("date").annotate(
        present=Count("id", filter=Q(status="Present")),
        absent=Count("id", filter=Q(status="Absent"))
    ).order_by("-date")[:7]

    # Peak Attendance Hours (Bar Chart)
    today_attendance = Attendance.objects.filter(
        student__classgroup__in=teacher.assigned_classes.all(),
        date=today,
        status="Present"
    )
    attendance_times = today_attendance.values_list("time", flat=True)
    hour_counts = Counter([t.hour for t in attendance_times])
    hours = list(range(6, 16))  # 6 AM to 3 PM
    attendance_by_hour = [hour_counts.get(h, 0) for h in hours]

    # Attendance Trends (Pie Chart)
    total_today = students_qs.count()
    present_today = today_attendance.count()
    absent_today_count = total_students - present_today_count
    absent_today = total_today - present_today

    context = {
        "teacher": teacher,
        "students": students_qs,
        "form": form,
        "total_students": total_students,
        "present_today_count": present_today_count,
        "class_count": class_count,
        "recent_attendance": recent_attendance,
        "daily_stats": daily_stats,
        "unread_count": unread_count,
        "can_enroll": can_enroll_student(school),
        "has_email_notifications": has_email,

        # Charts
        "hours": hours,
        "attendance_by_hour": attendance_by_hour,
        "present_today": present_today,
        "absent_today_count": absent_today_count,
        "absent_today": absent_today,
    }

    return render(request, "teacher/dashboard.html", context)

FASTAPI = "http://127.0.0.1:8001"   # micro‑service



# # mark attendnace views 
# @login_required
# @role_required("TEACHER")
# def mark_attendance_page(request):
#     teacher  = request.user.teacher_profile
#     students = Student.objects.filter(classgroup__in=teacher.assigned_classes.all()) 
#     today    = datetime.date.today()
#     school = teacher.school

#     subscription = SchoolSubscription.objects.filter(school=teacher.school).first()
#     has_email = subscription and subscription.plan and subscription.plan.has_email_notifications

#     #Enforce subscription plan limits
#     subscription = SchoolSubscription.objects.get(school=school)
#     if not subscription.is_active():
#         messages.error(request, "Your subscription has expired. Upgrade to enroll more students.")
#         return redirect("teacher:dashboard")

#     # rows for today, once
#     today_rows = (
#         Attendance.objects
#         .filter(date=today, student__in=students)
#         .values_list("student_id", "time")
#     )

#     present_ids   = {sid for sid, _ in today_rows}
#     present_times = {sid: t.strftime("%H:%M:%S") for sid, t in today_rows}

#     return render(request, "teacher/mark_attendance_page.html", {
#         "students":       students,
#         "today":          today,
#         "present_ids":    present_ids,
#         "present_times":  present_times,   # ← new
#         "has_email_notifications": has_email,
#         "can_enroll": can_enroll_student(school),
#     })


# # mark attendnace ajax

# @login_required
# @role_required("TEACHER")
# def mark_attendance_ajax(request):
#     """
#     AJAX: capture a live fingerprint, compare to each student,
#     and mark the first match as Present for today.
#     """
#     teacher = request.user.teacher_profile
#     students = Student.objects.filter(
#         classgroup__in=teacher.assigned_classes.all(),
#         fingerprint_data__isnull=False
#     )

#     try:
#         live = requests.post(f"{FASTAPI}/scan", timeout=20).json()["fmd"]
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

#     for stu in students:
#         resp = requests.post(
#             f"{FASTAPI}/compare",
#             json={"stored_fmd": stu.fingerprint_data},
#             timeout=20
#         ).json()

#         if resp.get("match"):
#             now = datetime.datetime.now()
#             Attendance.objects.update_or_create(
#                 student=stu,
#                 date=datetime.date.today(),
#                 defaults={
#                     "status": "Present",
#                     "time": now.time()
#                 },
#             )
#             return JsonResponse({
#                 "match": True,
#                 "student": stu.firstname,
#                 "time": now.strftime("%H:%M:%S")
#             })

#     return JsonResponse({"match": False})

# mark attendnace views 



# mark attendnace views 
@login_required
def mark_attendance_page(request):
    teacher  = request.user.teacher_profile
    students = Student.objects.filter(classgroup__in=teacher.assigned_classes.all()) 
    today    = datetime.date.today()
    school = teacher.school

    subscription = SchoolSubscription.objects.filter(school=teacher.school).first()
    has_email = subscription and subscription.plan and subscription.plan.has_email_notifications

    #Enforce subscription plan limits
    subscription = SchoolSubscription.objects.get(school=school)
    if not subscription.is_active():
        messages.error(request, "Your subscription has expired. Upgrade to enroll more students.")
        return redirect("teacher:dashboard")

    # rows for today, once
    today_rows = (
        Attendance.objects
        .filter(date=today, student__in=students)
        .values_list("student_id", "time")
    )

    present_ids   = {sid for sid, _ in today_rows}
    present_times = {sid: t.strftime("%H:%M:%S") for sid, t in today_rows}

    return render(request, "teacher/mark_attendance_page.html", {
        "students":       students,
        "today":          today,
        "present_ids":    present_ids,
        "present_times":  present_times,   # ← new
        "has_email_notifications": has_email,
        "can_enroll": can_enroll_student(school),
    })





@login_required
def mark_attendance_ajax(request):
    """
    AJAX: capture a live fingerprint once, then compare to each student using FastAPI /compare.
    """
    teacher = request.user.teacher_profile
    students = Student.objects.filter(
        classgroup__in=teacher.assigned_classes.all(),
        fingerprint_data__isnull=False
    )

    try:
        # Step 1: Capture live fingerprint from FastAPI
        scan_response = requests.post(f"{FASTAPI}/scan", timeout=20)
        scan_response.raise_for_status()
        live_fmd = scan_response.json().get("fmd")

        if not live_fmd:
            return JsonResponse({"error": "No fingerprint data captured."}, status=500)

    except Exception as e:
        return JsonResponse({"error": f"Fingerprint scan failed: {str(e)}"}, status=500)

    # Step 2: Send each stored FMD to FastAPI's /compare endpoint (scanner will rescan for each)
    for stu in students:
        try:
            resp = requests.post(
                f"{FASTAPI}/compare",
                json={"stored_fmd": stu.fingerprint_data},
                timeout=10
            )
            resp.raise_for_status()

            if resp.json().get("match") is True:
                now = timezone.now()
                Attendance.objects.update_or_create(
                    student=stu,
                    date=datetime.date.today(),
                    defaults={
                        "status": "Present",
                        "time": now.time()
                    },
                )
                return JsonResponse({
                    "match": True,
                    "student": stu.firstname,
                    "time": now.strftime("%H:%M:%S")
                })

        except Exception:
            continue  # Skip students that failed to match

    return JsonResponse({"match": False}) 







































# def mark_attendance_ajax(request):
#     teacher = request.user.teacher_profile
#     students = Student.objects.filter(
#         classgroup__in=teacher.assigned_classes.all(),
#         fingerprint_data__isnull=False
#     )

#     try:
#         # Step 1: Capture live scan
#         live = requests.post(f"{FASTAPI}/scan", timeout=20).json()["fmd"]
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

#     # Step 2: Loop and compare live vs stored
#     for stu in students:
#         try:
#             resp = requests.post(
#                 f"{FASTAPI}/compare",
#                 json={"stored_fmd": stu.fingerprint_data, "live_fmd": live},
#                 timeout=20
#             ).json()

#             if resp.get("match"):
#                 now = datetime.datetime.now()
#                 Attendance.objects.update_or_create(
#                     student=stu,
#                     date=datetime.date.today(),
#                     defaults={"status": "Present", "time": now.time()},
#                 )
#                 return JsonResponse({
#                     "match": True,
#                     "student": stu.firstname,
#                     "time": now.strftime("%H:%M:%S")
#                 })
#         except Exception as e:
#             continue  # optionally log failure

#     return JsonResponse({"match": False})


# pdf
@login_required
@role_required("TEACHER")
def attendance_pdf(request, day):  # day is "YYYY-MM-DD"
    teacher = request.user.teacher_profile
    school = teacher.school

    assigned_classes = teacher.assigned_classes.all()
    actual_date = date.fromisoformat(day)  # ✅ No strptime

    attendance = Attendance.objects.filter(
        student__classgroup__in=assigned_classes,
        date=actual_date
    ).select_related("student", "student__classgroup")

    class_data = []
    total_students = 0
    total_present = 0
    total_absent = 0

    for group in assigned_classes:
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
        'teacher': teacher,
        'date': actual_date,  # now it’s a date object so filter works
        'class_data': class_data,
        'total_students': total_students,
        'total_present': total_present,
        'total_absent': total_absent,
        'overall_percentage': round((total_present / total_students) * 100, 1) if total_students > 0 else 0,
    }

    template = get_template('teacher/pdf_report.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="attendance_{day}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("PDF generation failed", status=500)
    return response


# manage students
@login_required
@role_required("TEACHER")
def manage_students(request):
    teacher = request.user.teacher_profile
    school = teacher.school

    #Enforce subscription plan limits
    subscription = SchoolSubscription.objects.get(school=school)
    if not subscription.is_active():
        messages.error(request, "Your subscription has expired. Upgrade to enroll more students.")
        return redirect("teacher:dashboard")

    if request.method == "POST":
        if not can_enroll_student(school):
            messages.error(request, "You’ve reached your student limit. Upgrade to enroll more students.")
            return redirect("teacher:dashboard")
        
    qs = Student.objects.filter(
        school=teacher.school,
        classgroup__in=teacher.assigned_classes.all()
    )

    # simple search ?q=efe
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(firstname__icontains=q) | qs.filter(lastname__icontains=q)

    return render(request, "teacher/manage_students.html", {
        "students": qs,
        "query": q,
        "classgroups": ClassGroup.objects.filter(school=teacher.school),  # 👈 Add this
        "can_enroll": can_enroll_student(school),
    })


# update students
@login_required
@role_required("TEACHER")
def update_student(request):
    if request.method == "POST":
        pk = request.POST.get("pk")
        student = get_object_or_404(Student, pk=pk)

        form = StudentEditForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

# delete students
@login_required
@role_required("TEACHER")
def delete_student(request):
    if request.method == "POST":
        pk = request.POST.get("pk")
        student = get_object_or_404(Student, pk=pk)
        student.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"error": "Invalid request method"}, status=405)


# dashboard report report_pdf
@login_required
@role_required("TEACHER")
def report_pdf(request):
    """Generate a PDF for the same ?from=yyyy-mm-dd&to=yyyy-mm-dd range."""
    teacher = request.user.teacher_profile
    d_from  = datetime.date.fromisoformat(request.GET["from"])
    d_to    = datetime.date.fromisoformat(request.GET["to"])

    qs = (Attendance.objects
          .filter(student__classgroup=teacher.classgroup,
                  date__gte=d_from, date__lte=d_to)
          .select_related("student")
          .order_by("date", "student__lastname"))

    # ---- table data ----
    table_rows = [["Date", "Time", "Student", "Status"]]
    for r in qs:
        table_rows.append([
            r.date.strftime("%Y-%m-%d"),
            r.time.strftime("%H:%M:%S") if r.time else "—",
            f"{r.student.lastname} {r.student.firstname}",
            r.status,
        ])

    # ---- PDF ----
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()

    table = Table(table_rows, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), colors.lightgrey),
        ("GRID",       (0,0),(-1,-1), 0.25, colors.black),
    ]))

    doc.build([
        Paragraph(f"Attendance Report – {teacher.classgroup.name}", styles["Title"]),
        Paragraph(f"{d_from:%Y-%m-%d} to {d_to:%Y-%m-%d}", styles["Normal"]),
        table,
    ])
    buf.seek(0)
    filename = f"{teacher.classgroup.name}_{d_from:%Y%m%d}-{d_to:%Y%m%d}.pdf"
    return FileResponse(buf, as_attachment=True, filename=filename)


# inbox
@login_required
def inbox(request):
    teacher  = request.user.teacher_profile
    # students = Student.objects.filter(classgroup__in=teacher.assigned_classes.all())
    school = teacher.school

    
    subscription = SchoolSubscription.objects.filter(school=teacher.school).first()
    has_email = subscription and subscription.plan and subscription.plan.has_email_notifications

    #Enforce subscription plan limits
    subscription = SchoolSubscription.objects.get(school=school)
    if not subscription.is_active():
        messages.error(request, "Your subscription has expired. Upgrade to enroll more students.")
        return redirect("teacher:dashboard")
    

    messages = Message.objects.filter(
        recipient__isnull=True
    ) | Message.objects.filter(recipient=request.user)

    messages = messages.order_by("-timestamp")
    return render(request, "teacher/inbox.html", {"messages": messages, "can_enroll": can_enroll_student(school),})

# view message in inbox
@login_required
@role_required("TEACHER")
def view_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    if not message.is_read:
        message.is_read = True
        message.save()
    return JsonResponse({"status": "read"})


# create ticket to the super admin
@login_required
@role_required("TEACHER")  
def create_ticket(request):

    teacher  = request.user.teacher_profile
    # students = Student.objects.filter(classgroup__in=teacher.assigned_classes.all())
    school = teacher.school

    
    subscription = SchoolSubscription.objects.filter(school=teacher.school).first()
    has_email = subscription and subscription.plan and subscription.plan.has_email_notifications

    # Enforce subscription plan limits
    subscription = SchoolSubscription.objects.get(school=school)
    if not subscription.is_active():
        messages.error(request, "Your subscription has expired. Upgrade to enroll more students.")
        return redirect("teacher:dashboard")

    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.creator = request.user
            ticket.save()
            return redirect("teacher:my_tickets") 
    else:
        form = TicketForm()
    return render(request, "teacher/create_ticket.html", {"form": form, "can_enroll": can_enroll_student(school)})

@login_required
@role_required("TEACHER") 
def my_tickets(request):

    teacher  = request.user.teacher_profile
    # students = Student.objects.filter(classgroup__in=teacher.assigned_classes.all())
    school = teacher.school

    
    subscription = SchoolSubscription.objects.filter(school=teacher.school).first()
    has_email = subscription and subscription.plan and subscription.plan.has_email_notifications

    # Enforce subscription plan limits
    subscription = SchoolSubscription.objects.get(school=school)
    if not subscription.is_active():
        messages.error(request, "Your subscription has expired. Upgrade to enroll more students.")
        return redirect("teacher:dashboard")

    tickets = (
        Ticket.objects
        .filter(creator=request.user)
    )
    return render(request, "teacher/my_tickets.html", {"tickets": tickets, "can_enroll": can_enroll_student(school)})


@login_required
@role_required("TEACHER")
def ticket_detail(request, ticket_id):

    teacher  = request.user.teacher_profile
    # students = Student.objects.filter(classgroup__in=teacher.assigned_classes.all())
    school = teacher.school

    
    subscription = SchoolSubscription.objects.filter(school=teacher.school).first()
    has_email = subscription and subscription.plan and subscription.plan.has_email_notifications

    # Enforce subscription plan limits
    subscription = SchoolSubscription.objects.get(school=school)
    if not subscription.is_active():
        messages.error(request, "Your subscription has expired. Upgrade to enroll more students.")
        return redirect("teacher:dashboard")

    ticket = get_object_or_404(Ticket, id=ticket_id, creator=request.user)
    responses = ticket.responses.all()
    return render(request, "teacher/ticket_detail.html", {
        "ticket": ticket,
        "responses": responses,
        "can_enroll": can_enroll_student(school)
    })







# @login_required
# @role_required("TEACHER")
# def report_picker(request):
#     """Initial page with date‑range picker; data loaded via AJAX."""
#     today = datetime.date.today()
#     default_from = today.replace(day=1)  # first day of month
#     return render(request, "teacher/report_picker.html", {
#         "default_from": default_from.isoformat(),
#         "default_to":   today.isoformat(),
#     })

# @login_required
# @role_required("TEACHER")
# def report_data_ajax(request):
#     """Return JSON summary + rows for the given range."""
#     teacher = request.user.teacher_profile
#     d_from  = datetime.date.fromisoformat(request.GET["from"])
#     d_to    = datetime.date.fromisoformat(request.GET["to"])

#     qs = (Attendance.objects
#           .filter(student__classgroup=teacher.classgroup,
#                   date__gte=d_from, date__lte=d_to)
#           .select_related("student")
#           .order_by("date", "student__lastname"))

#     # ---- metrics ----
#     total_records = qs.count()
#     present_count = qs.filter(status="Present").count()
#     absent_count  = qs.filter(status="Absent").count()

#     # ---- rows ----
#     rows = []
#     for rec in qs:
#         rows.append({
#             "date":   rec.date.isoformat(),
#             "time":   rec.time.strftime("%H:%M:%S") if rec.time else "—",
#             "name":   f"{rec.student.lastname} {rec.student.firstname}",
#             "status": rec.status,
#         })

#     return JsonResponse({
#         "metrics": {
#             "total":   total_records,
#             "present": present_count,
#             "absent":  absent_count,
#         },
#         "rows": rows,
#     })

# @login_required
# @role_required("TEACHER")
# def attendance_day(request, day):         
#     teacher = request.user.teacher_profile
#     date_obj = datetime.date.fromisoformat(day)

#     records = (Attendance.objects
#                .filter(student__classgroup=teacher.classgroup, date=date_obj)
#                .select_related("student")
#                .order_by("student__lastname"))

#     return render(request, "teacher/attendance_day.html",
#                   {"day": date_obj, "records": records})

