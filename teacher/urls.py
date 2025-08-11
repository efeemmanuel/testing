from django.urls import path, include
from .views import *
from django.contrib.auth.views import LogoutView
app_name="teacher"


urlpatterns = [
    
    path('',dashboard,name='dashboard' ),

    # mark attendnace urls
    path("mark_attendance_page/",  mark_attendance_page, name="mark_attendance_page"),
    path("attendance_scan", mark_attendance_ajax, name="attendance_scan"),

    # pdf download
    path("attendance-pdf/<slug:day>/", attendance_pdf, name="attendance_pdf"),
    path("reports/pdf/",  report_pdf, name="report_pdf"),

    # Manage Students
    path("students/", manage_students, name="manage_students"),
    path("students/update/", update_student, name="update_student"),
    path("students/delete/", delete_student, name="delete_student"),

    # sending messages
    path("inbox/", inbox, name="inbox"),
    path("messages/<int:message_id>/", view_message, name="view_message"),

    # logout
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),

    # create tickets
    path("support/create/", create_ticket, name="create_ticket"),
    path("support/my-tickets/", my_tickets, name="my_tickets"),
    path("support/ticket/<int:ticket_id>/", ticket_detail, name="ticket_detail"),


]