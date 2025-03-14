from django.urls import path
from . import views


app_name = "photolog"

urlpatterns = [
    path("", views.index, name="index"),
    path("@<str:username>/", views.user_page, name="user_page"),
    path("@<str:username>/follow/", views.user_follow, name="user_follow"),
    path("user/following/", views.following_list, name="following_list"),
    path("user/discover/", views.discover_list, name="discover_list"),
    path("new/", views.NoteCreateView.as_view(), name="note_new"),
    path("<int:pk>/", views.NoteDetailView.as_view(), name="note_detail"),
    path("<int:pk>/edit/", views.note_edit, name="note_edit"),
    path(
        "<int:note_pk>/comments/", views.CommentListView.as_view(), name="comment_list"
    ),
    path(
        "<int:note_pk>/comment/new/",
        views.CommentCreateView.as_view(),
        name="comment_new",
    ),
    path(
        "<int:note_pk>/comment/<int:pk>/edit/",
        views.CommentUpdateView.as_view(),
        name="comment_edit",
    ),
    path(
        "<int:note_pk>/comment/<int:pk>/delete/",
        views.CommentDeleteView.as_view(),
        name="comment_delete",
    ),
]
