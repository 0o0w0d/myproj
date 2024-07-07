from io import BytesIO
from os.path import splitext
from uuid import uuid4
from django_lifecycle import LifecycleModelMixin, hook, BEFORE_SAVE
from PIL import Image

from django.db import models
from django.utils import timezone
from django.utils.encoding import force_str

from accounts.models import User


class Note(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def uuid_name_upload_to(instance: models.Model, filename: str) -> str:
    app_label = instance.__class__._meta.app_label
    cls_name = instance.__class__.__name__.lower()
    ymd_path = force_str(timezone.now().strftime("%Y/%m/%d"))
    extension = splitext(filename)[-1].lower()
    new_filename = uuid4().hex + extension
    return "/".join((app_label, cls_name, ymd_path, new_filename))


class Photo(LifecycleModelMixin, models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    image = models.ImageField(
        # upload_to="photolog/photo/%Y/%m/%d"
        upload_to=uuid_name_upload_to
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # BEFORE_UPDATE: 기존 레코드를 수정해서 저장할 때 호출
    # BEFORE_CREATE: 새 레코드를 생성해서 저장할 때 호출
    # BEFORE_SAVE: 레코드 생성/수정 시 저장할 때 호출
    @hook(BEFORE_SAVE, when="image", has_changed=True)
    def on_image_changed(self):
        if self.image:
            pil_image = Image.open(self.image.file)
            MAX_SIZE = (1024, 1024)
            pil_image.thumbnail(MAX_SIZE)
            if pil_image.mode == "RGBA":
                pil_image = pil_image.convert("RGB")

            io = BytesIO()
            pil_image.save(io, format="jpeg", quality=60)
            io.seek(0)

            thumb_name = splitext(self.image.name)[0] + ".jpg"
            # 새로운 파일명, 새로운 파일 내용, 모델 인스턴스의 save 자동 호출 여부
            self.image.save(thumb_name, io, save=False)
