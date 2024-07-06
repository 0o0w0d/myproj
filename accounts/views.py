from django.shortcuts import render
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView
from django.contrib.auth.decorators import login_required
from .forms import LoginForm


# Create your views here.
class LoginView(DjangoLoginView):
    form_class = LoginForm
    template_name = "crispy_form.html"

    # context 추가
    extra_context = {"form_title": "Login"}


@login_required
def profile(request):
    return render(request, "accounts/profile.html")
