from django.shortcuts import render
from django.contrib.auth.views import (
    LoginView as DjangoLoginView,
    LogoutView as DjangoLogoutView,
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm


class LoginView(DjangoLoginView):
    form_class = LoginForm
    template_name = "crispy_form.html"

    # context 추가
    extra_context = {"form_title": "Login"}


class LogoutView(DjangoLogoutView):
    next_page = "accounts:login"

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, "logout successed :)")
        return response


@login_required
def profile(request):
    return render(request, "accounts/profile.html")
