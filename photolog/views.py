from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy


from .models import Note, Photo
from .forms import NoteForm


def index(request):
    qs = Note.objects.all().select_related("author").prefetch_related("photo_set")

    return render(request, "photolog/index.html", {"note_list": qs})


class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    template_name = "crispy_form.html"
    extra_context = {"form_title": "New Note"}
    success_url = reverse_lazy("photolog:index")  # TODO: detail 페이지 구현 후 변경

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
