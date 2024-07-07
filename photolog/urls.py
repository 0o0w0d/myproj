from django.urls import path
from . import views


app_name = "photolog"

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.NoteCreateView.as_view(), name="note_new"),
    path("<int:pk>/", views.NoteDetailView.as_view(), name="note_detail"),
]
