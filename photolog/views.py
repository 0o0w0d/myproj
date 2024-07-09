from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required


from .models import Note, Photo
from .forms import NoteCreateForm, PhotoUpdateFormSet, NoteUpdateForm


def index(request):
    qs = Note.objects.all().select_related("author").prefetch_related("photo_set")

    return render(request, "photolog/index.html", {"note_list": qs})


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
