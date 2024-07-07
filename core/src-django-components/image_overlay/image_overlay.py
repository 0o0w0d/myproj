from typing import Any, Dict
from django_components.component import Component, register


@register("image-overlay")
class ImageOverlay(Component):
    template_name = "image_overlay/image_overlay.html"

    def get_context_data(self, href=None, target=None, **kwargs):
        # class가 파이썬에서는 예약어이기 때문에 kwargs로 받아서 사용
        classattr = kwargs.get("class")
        return {"href": href, "target": target, "class": classattr}

    class Media:
        css = {"all": ["image_overlay/image_overlay.css"]}
