from django.urls import path, include
from .views import *
app_name="principal"


urlpatterns = [
    
    path('',dashboard,name='dashboard' ),

    # manage teachers
    path("teachers/", manage_teachers, name="manage_teachers"),
    path("teachers/<int:user_id>/edit/", edit_teacher, name="edit_teacher"),
    path("teachers/<int:user_id>/delete/", delete_teacher, name="delete_teacher"),


    # profile management
    path("profile/", profile_management, name="profile_management"),

    # school urls
    path("profile/edit_school/", edit_school, name="edit_school"),
    path("profile/edit_principal/", edit_principal, name="edit_principal"),



    # message urls
    path("messages/", communication_center, name="communication_center"),
    path("communication/delete/<int:message_id>/", delete_message, name="delete_message"),

    # upgrade plan 
    path("upgrade/", upgrade_plan, name="upgrade_plan"), 




    # tickets url
    path("support/create/", create_ticket, name="create_ticket"),
    path("support/my-tickets/", my_tickets, name="my_tickets"),
    path("support/ticket/<int:ticket_id>/", ticket_detail, name="ticket_detail"),

    # pdf attendance
    path("attendance-pdf/<slug:day>/", attendance_pdf, name="attendance_pdf"),

]