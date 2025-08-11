from django.urls import path, include
from .views import dashboard
from .views import *
app_name="superadmin"


urlpatterns = [
    
    path('',dashboard,name='dashboard' ),



    path("schools/", manage_schools, name="manage_schools"),
    path("schools/edit/<int:school_id>/", edit_school, name="edit_school"),
    path("schools/delete/<int:school_id>/", delete_school, name="delete_school"),



    path('classgroups/', manage_classgroups, name='manage_classgroups'),
    path('classgroups/edit/<int:classgroup_id>/', edit_classgroup, name='edit_classgroup'),
    path('classgroups/delete/<int:classgroup_id>/', delete_classgroup, name='delete_classgroup'),

    

    path("teachers/", manage_teachers, name="manage_teachers"),
    path("teachers/edit/<int:user_id>/", edit_teacher, name="edit_teacher"),
    path("teachers/delete/<int:user_id>/", delete_teacher, name="delete_teacher"),



    path("principals/", manage_principals, name="manage_principals"),
    path("principals/update/<int:pk>/", update_principal, name="update_principal"),
    path("principals/delete/<int:pk>/", delete_principal, name="delete_principal"),

    path("plans/", manage_plans, name="manage_plans"),
    path("plans/delete/<int:plan_id>/", delete_plan, name="delete_plan"),


    path("subscriptions/", manage_school_subscriptions, name="manage_school_subscriptions"),
    path("subscriptions/update/<int:sub_id>/", update_school_subscription, name="update_subscription"),




    path("students/", manage_students, name="manage_students"),
    path("students/edit/<int:student_id>/", edit_student, name="edit_student"),
    path("students/delete/<int:student_id>/", delete_student, name="delete_student"),




    path("support/all/", all_tickets, name="all_tickets"),
    path("support/ticket/<int:ticket_id>/", ticket_detail, name="ticket_detail"),
    path("support/update_status/<int:ticket_id>/", update_ticket_status, name="update_ticket_status"), 
    


    path("send_message/", send_message, name="send_message"),
    



]