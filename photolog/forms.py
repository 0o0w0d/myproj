from typing import List, Union
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.forms import ValidationError
from django.core.files import File
from django.core.files.base import ContentFile
from django.forms import inlineformset_factory
from PIL import Image

from .models import Note, Photo


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    widget = MultipleFileInput

    # ImageField는 단일 파일에 대한 유효성 검사 및 변환을 수행할 뿐,
    # 여러 파일에 대한 유효성 검사 및 변환을 위해서 별도의 로직 추가 필요

    # clean 메서드에서도 data 인자가 File 타입임을 가정하고 구현되어 있음
    # 위젯에서는 List[File] 타입 값이 전달
    def clean(self, data: Union[List[File], File], initial=None):
        # 단일 File만을 처리하는 부모의 메서드를 호출하지 않은 상태로 재정의
        single_clean = super().clean

        # 파일이 list or tuple이라면,
        if isinstance(data, (list, tuple)):
            return [single_clean(file) for file in data]
        else:
            return single_clean(data)


class NoteCreateForm(forms.ModelForm):
    photos = MultipleImageField(required=True)

    # 클래스 변수로 선언한 FormHelper는 자식과 공유 => 인스턴스 변수로 선언해,
    # NoteUpdateForm에서 FormHelper 속성을 override 가능하도록 설정
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout("title", "content", "photos")
        self.helper.add_input(Submit("submit", "save", css_class="w-100"))

    class Meta:
        model = Note
        fields = ["title", "content"]

    # 이미지 크기 조정 및 jpeg 변환 수행 -> 이미지 변환에 실패하면 유효성 검사 에러
    def clean_photos(self):
        is_photo_required = self.fields["photos"].required
        photo_list: List[File] = self.cleaned_data.get("photos")
        if not photo_list and is_photo_required:
            raise forms.ValidationError("require at least one image :<")
        elif photo_list:
            try:
                photo_list = [Photo.make_thumb(photo) for photo in photo_list]
            except Exception as e:
                raise forms.ValidationError(e) from e
        return photo_list


# NoteUpdateForm에서는 form 태그를 생성하지 않도록 helepr 속성 지정
class NoteUpdateForm(NoteCreateForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["photos"].required = False
        self.helper.form_tag = False
        self.helper.inputs = []


class PhotoInlineForm(forms.ModelForm):

    class Meta:
        model = Photo
        fields = ["image"]


PhotoUpdateFormSet = inlineformset_factory(
    parent_model=Note, model=Photo, form=PhotoInlineForm, extra=0, can_delete=True
)

# formset에서 form 태그 제거
PhotoUpdateFormSet.helper = FormHelper()
PhotoUpdateFormSet.helper.form_tag = False
