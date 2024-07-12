from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView,
    ListView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django_htmx.http import trigger_client_event, HttpResponseClientRedirect
from core.decorators import login_required_hx
from django.utils.decorators import method_decorator

from .models import Note, Photo, Comment
from accounts.models import User
from .forms import NoteCreateForm, PhotoUpdateFormSet, NoteUpdateForm, CommentForm


def index(request):
    tag_name = request.GET.get("tag", "").strip()
    query = request.GET.get("query", "").strip()
    if tag_name:
        qs = Note.objects.filter(tags__name__in=[tag_name])

    elif query:
        qs = Note.objects.filter(Q(title__icontains=query) | Q(author__username=query))

    else:
        if not request.user.is_authenticated:
            qs = Note.objects.all()

        else:
            user = request.user
            qs = Note.objects.filter(
                Q(author__in=user.following_set.all()) | Q(author=user)
            )

    qs = qs.select_related("author").prefetch_related("photo_set", "tags")

    return render(request, "photolog/index.html", {"note_list": qs, "query": query})


def user_page(request, username):
    author = get_object_or_404(User, is_active=True, username=username)

    qs = Note.objects.filter(author=author)
    qs = qs.select_related("author").prefetch_related("photo_set", "tags")

    return render(
        request, "photolog/user_page.html", {"note_list": qs, "author": author}
    )


def user_follow(request, username: str):
    from_user = request.user
    to_user = get_object_or_404(User, username=username, is_active=True)

    # 1. method GET or POST
    # 2. user.is_authenticated
    # 3. is_follower

    # GET일 경우에는 단순 팔로잉 버튼 렌더링
    if request.method == "GET":
        if from_user.is_authenticated:
            is_follower = from_user.is_follower(to_user)
        else:
            is_follower = False
    else:
        if from_user.is_authenticated:
            # 이미 팔로우 되있는 지 확인 여부에 따라 다른 로직 수행
            is_follower = from_user.is_follower(to_user)

            from_user.follow(to_user)
            print("전", is_follower)
            is_follower = not is_follower
            print("후", is_follower)
        else:
            current_uri = request.META.get("HTTP_HX_CURRENT_URL")
            redirect_uri = reverse_lazy("accounts:login") + f"?next={current_uri}"
            return HttpResponseClientRedirect(redirect_uri)

    return render(
        request,
        "photolog/_user_follower.html",
        {"is_follower": is_follower, "username": username},
    )


# class UserNoteListView(ListView):
#     model = Note
#     template_name = "photolog/user_page.html"

#     def get_queryset(self) -> QuerySet:
#         qs = super().get_queryset()
#         username = self.kwargs["username"]
#         qs = qs.filter(
#             author__username=username, author__is_active=True
#         ).prefetch_related("photo_set", "tags")
#         return qs

#     def get_context_data(self, **kwargs) -> dict:
#         kwargs = super().get_context_data(**kwargs)
#         kwargs["username"] = self.kwargs["username"]
#         return kwargs


class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    form_class = NoteCreateForm
    template_name = "crispy_form.html"
    extra_context = {"form_title": "New Note"}
    # success_url = reverse_lazy("photolog:index")  # TODO: detail 페이지 구현 후 변경

    def form_valid(self, form):
        new_note = form.save(commit=False)
        new_note.author = self.request.user
        new_note.save()

        # 모델에 포함되어있는 필드가 아니므로, 따로 저장 로직 구현
        photo_file_list = form.cleaned_data.get("photos")
        if photo_file_list:
            Photo.create_photos(new_note, photo_file_list)

        response = super().form_valid(form)
        messages.success(self.request, "new note saved! :)")
        return response


class NoteDetailView(DetailView):
    model = Note

    # N+1 문제 발생 : template단에서는 select_related, prefetch_related를 사용할 수 없기 때문에 view로 로직 이동
    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        note = self.object
        context["comment_list"] = note.comment_set.select_related("author__profile")
        return context


# TODO: photos에 대한 처리를 위해 Formset 이용 => CBV보다 FBV가 구현 용이
class NoteUpdateView(LoginRequiredMixin, UpdateView):
    model = Note
    form_class = NoteCreateForm
    template_name = "crispy_form.html"
    extra_context = {"form_title": "Edit Note"}

    # Note.author에 한해서만 수정 가능하도록 queryset 설정
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(author=self.request.user)
        return qs


@login_required
def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk, author=request.user)
    photo_qs = note.photo_set.all()

    if request.method == "GET":
        note_form = NoteUpdateForm(instance=note, prefix="note")
        photo_formset = PhotoUpdateFormSet(
            queryset=photo_qs, instance=note, prefix="photos"
        )
    else:
        note_form = NoteUpdateForm(
            data=request.POST, files=request.FILES, instance=note, prefix="note"
        )
        photo_formset = PhotoUpdateFormSet(
            queryset=photo_qs,
            instance=note,
            data=request.POST,
            files=request.FILES,
            prefix="photos",
        )
        if note_form.is_valid() and photo_formset.is_valid():
            saved_note = note_form.save()

            # 새롭게 생성되는 Photo
            photo_file_list = note_form.cleaned_data.get("photos")
            if photo_file_list:
                Photo.create_photos(saved_note, photo_file_list)

            # 기존 Photo 수정
            photo_formset.save()

            messages.success(request, f"note #{saved_note.pk} saved! :)")
            return redirect(saved_note)

    return render(
        request,
        "crispy_form_and_formset.html",
        {
            "form": note_form,
            "form_title": "Note Edit",
            "formset": photo_formset,
            "form_submit_label": "Save",
        },
    )


@method_decorator(login_required_hx, name="dispatch")
class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "photolog/_comment_form.html"

    # 에러 상황 발생 테스트를 위해 dispatch 메서드 사용
    # def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
    #     1 / 0
    #     return super().dispatch(request, *args, **kwargs)

    # form에 request 값 전달을 위해 get_form_kwargs 메서드 재정의
    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    # 유효성 검사가 끝나고 나서 호출
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        comment = form.save(commit=False)
        comment.author = self.request.user
        note_pk = self.kwargs["note_pk"]
        comment.note = get_object_or_404(Note, pk=note_pk)
        comment.save()

        messages.success(self.request, f"note #{note_pk} comment saved :)")

        response = render(self.request, "_messages_as_event.html")

        # "refresh-comment-list" 이벤트를 전달
        response = trigger_client_event(response, "refresh-comment-list")

        return response


class CommentListView(ListView):
    model = Comment
    template_name = "photolog/_comment_list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        note_pk = self.kwargs["note_pk"]
        qs = qs.filter(note__pk=note_pk)
        qs = qs.select_related("author__profile")
        return qs


@method_decorator(login_required_hx, name="dispatch")
class CommentUpdateView(UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "photolog/_comment_form.html"

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        qs = qs.filter(author=self.request.user)
        return qs

    # 유효성 검사가 끝나고 나서 호출
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        note_pk = self.kwargs["note_pk"]
        form.save()

        messages.success(self.request, f"note #{note_pk} comment saved :)")
        response = render(self.request, "_messages_as_event.html")
        response = trigger_client_event(response, "refresh-comment-list")

        return response


@method_decorator(login_required_hx, name="dispatch")
class CommentDeleteView(DeleteView):
    model = Comment

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        note_pk = self.kwargs["note_pk"]
        qs = qs.filter(note__pk=note_pk, author=self.request.user)
        return qs

    def form_valid(self, form):
        self.object.delete()

        messages.success(self.request, f"comment deleted :(")
        response = render(self.request, "_messages_as_event.html")
        response = trigger_client_event(response, "refresh-comment-list")

        return response
