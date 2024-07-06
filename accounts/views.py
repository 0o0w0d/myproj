from django.shortcuts import render
from django.contrib.auth.views import (
    LoginView as DjangoLoginView,
    LogoutView as DjangoLogoutView,
)
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse_lazy

from .forms import LoginForm, SignUpForm
from .models import User
from .utils import send_welcome_email


class LoginView(DjangoLoginView):
    form_class = LoginForm
    template_name = "crispy_form.html"

    # context 추가
    extra_context = {"form_title": "Login"}

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"{self.request.user}! hello :)")
        return response


class LogoutView(DjangoLogoutView):
    next_page = "accounts:login"

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, "logout successed :)")
        return response


class SignupView(CreateView):
    model = User
    form_class = SignUpForm
    template_name = "crispy_form.html"
    extra_context = {"form_title": "Sign Up"}
    success_url = reverse_lazy("accounts:login")

    # 유효성 검사 후에 폼 처리 결과를 마무리하는 메서드
    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, "Welcome you to join our service!")

        user = self.object
        send_welcome_email(user, fail_silently=True)
        return response


@login_required
def profile(request):
    return render(request, "accounts/profile.html")
