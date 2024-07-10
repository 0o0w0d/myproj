from django.urls import path
from . import views


app_name = "photolog"

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.NoteCreateView.as_view(), name="note_new"),
    path("<int:pk>/", views.NoteDetailView.as_view(), name="note_detail"),
    path("<int:pk>/edit/", views.note_edit, name="note_edit"),
    path(
        "<int:note_pk>/comment/new/",
        views.CommentCreateView.as_view(),
        name="comment_new",
    ),
]
