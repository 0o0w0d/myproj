from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.forms import ValidationError

from .models import User


class LoginForm(AuthenticationForm):
    helper = FormHelper()
    helper.attrs = {"novalidate": True}
    helper.layout = Layout("username", "password")
    helper.add_input(Submit("submit", "Login", css_class="w-100"))


class SignUpForm(UserCreationForm):
    helper = FormHelper()
    helper.attrs = {"novalidate": True}
    helper.layout = Layout("username", "email", "password1", "password2")
    helper.add_input(Submit("submit", "Sign Up", css_class="w-100"))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            user = User.objects.filter(email__iexact=email)
            if user.exists():
                raise ValidationError("email already exists :(")
        return email
