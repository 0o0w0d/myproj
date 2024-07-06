from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

from .models import User


def send_welcome_email(user, fail_silently=False):
    if user.email:
        subject = render_to_string("accounts/welcome_email/subject.txt")
        # 제목을 한 줄 문자열로
        subject = " ".join(subject.splitlines())
        content = render_to_string(
            "accounts/welcome_email/content.txt", {"username": user.username}
        )
        sender = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        send_mail(subject, content, sender, recipient_list, fail_silently=fail_silently)
