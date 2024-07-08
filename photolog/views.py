from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required


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


# TODO: photos에 대한 처리를 위해 Formset 이용 => CBV보다 FBV가 구현 용이
class NoteUpdateView(LoginRequiredMixin, UpdateView):
    model = Note
    form_class = NoteForm
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

    if request.method == "GET":
        form = NoteForm(instance=note)
    else:
        form = NoteForm(data=request.POST, files=request.FILES, instance=note)
        if form.is_valid():
            saved_note = form.save()

            # 모델에 포함되어있는 필드가 아니므로, 따로 저장 로직 구현
            photo_file_list = form.cleaned_data.get("photos")
            if photo_file_list:
                Photo.create_photos(saved_note, photo_file_list)

            messages.success(request, f"note #{saved_note.pk} saved! :)")
            return redirect(saved_note)

    return render(
        request, "crispy_form.html", {"form": form, "form_title": "Note Edit"}
    )
