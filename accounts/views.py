from django.shortcuts import render
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView
from .forms import LoginForm


# Create your views here.
class LoginView(DjangoLoginView):
    form_class = LoginForm
    template_name = "crispy_form.html"

    # context 추가
    extra_context = {"form_title": "Login"}
