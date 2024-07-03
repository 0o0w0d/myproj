from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = "core"

urlpatterns = [
    path("", TemplateView.as_view(template_name="core/root.html"), name="root"),
]
