from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

from .models import User


class LoginForm(AuthenticationForm):
    helper = FormHelper()
    helper.attrs = {"novalidate": True}
    helper.layout = Layout("username", "password")
    helper.add_input(Submit("submit", "Login", css_class="w-100"))


class SignUpForm(UserCreationForm):
    helper = FormHelper()
    helper.attrs = {"novalidate": True}
    helper.layout = Layout("username", "password1", "password2")
    helper.add_input(Submit("submit", "Sign Up", css_class="w-100"))

    class Meta(UserCreationForm.Meta):
        model = User
