import os
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.forms import ValidationError
from django.core.files import File
from django.core.files.base import ContentFile
from PIL import Image

from .models import Profile, User


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


class ProfileForm(forms.ModelForm):
    # if modelForm in imageField/FieldField, automatically add enctype="multipart/form-data"
    helper = FormHelper()
    helper.attrs = {"novalidate": True}
    helper.layout = Layout("avatar")
    helper.add_input(Submit("submit", "save", css_class="w-100"))

    class Meta:
        model = Profile
        fields = ["avatar"]

    def clean_avatar(self):
        avatar_file: File = self.cleaned_data.get("avatar")
        if avatar_file:
            img = Image.open(avatar_file)
            MAX_SIZE = (512, 512)
            img.thumbnail(MAX_SIZE)
            img = img.convert("RGB")

            thumb_name = os.path.splitext(avatar_file.name)[0]
            thumb_file = ContentFile(b"", name=thumb_name)
            img.save(thumb_file, format="jpeg")

            return thumb_file

        return avatar_file
