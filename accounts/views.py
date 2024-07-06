from typing import Optional
from django.shortcuts import render
from django.contrib.auth.views import (
    LoginView as DjangoLoginView,
    LogoutView as DjangoLogoutView,
    RedirectURLMixin,
)
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy

from .forms import LoginForm, ProfileForm, SignUpForm
from .models import Profile, User
from .utils import send_welcome_email


class LoginView(DjangoLoginView):
    form_class = LoginForm
    template_name = "crispy_form.html"
    redirect_authenticated_user = True

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


class SignupView(RedirectURLMixin, CreateView):
    model = User
    form_class = SignUpForm
    template_name = "crispy_form.html"
    extra_context = {"form_title": "Sign Up"}
    success_url = reverse_lazy("accounts:profile")

    # 유효성 검사 후에 폼 처리 결과를 마무리하는 메서드
    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, "Welcome you to join our service!")

        user = self.object
        login(self.request, user)
        messages.success(self.request, "Automatically login after signup :)")

        send_welcome_email(user, fail_silently=True)
        return response

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            redirect_to = self.success_url
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your REDIRECT_URL doesn't point to a signup page."
                )
            messages.warning(request, "Login user can't sign up :(")
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)


@login_required
def profile(request):
    return render(request, "accounts/profile.html")


class ProfileUpdateView(UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "crispy_form.html"
    extra_context = {"form_title": "Profile Edit"}
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None) -> Optional[Profile]:
        try:
            return self.request.user.profile
        except Profile.DoesNotExist:
            # None이 지정되면 생성으로 동작
            return None

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "successfully profile saved :)")
        return response
