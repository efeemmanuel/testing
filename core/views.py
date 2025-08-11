from django.shortcuts import render

# Create your views here.
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import EmailAuthForm

# core.views

# dashboard path (superadmin, principal and teacher)
def _dashboard_path(user):
    return {
        "SUPER_ADMIN":  "/superadmin/",
        "PRINCIPAL": "/principal/",
        "TEACHER": "/teacher/",
    }.get(user.role, "/")


# login view allowing the email instead of username
def login_view(request):
    if request.method == "POST":
        form = EmailAuthForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(_dashboard_path(user))
    else:
        form = EmailAuthForm()
    return render(request, "registration/login.html", {"form": form})


# for redirect
@login_required
def role_home_redirect(request):
    return redirect(_dashboard_path(request.user))


def index(request):
    return render(request, "index.html")












