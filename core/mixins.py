from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.response import Response
from rest_framework.request import Request

from colorama import Fore
from django.conf import settings
from django.db.models import Model


class JSONResponseWrapperMixin:
    def finalize_response(
        self, request: Request, response: Response, *args, **kwargs
    ) -> Response:
        # 응답 코드에 따라 ok 값을 동적으로 구현
        is_ok = 200 <= response.status_code < 400
        accepted_renderer = getattr(request, "accepted_renderer", None)

        # 허용되지 않은 renderer(format querystring) or 에러 발생 시
        if accepted_renderer is None or response.exception is True:
            response.data = {"ok": is_ok, "result": response.data}

        elif isinstance(
            request.accepted_renderer, (JSONRenderer, BrowsableAPIRenderer)
        ):
            # response.data  # 원본 응답 데이터
            response.data = ReturnDict(
                {"ok": is_ok, "result": response.data},  # 원본 데이터를 래핑하여 전달
                serializer=response.data.serializer,  # 원본 데이터의 serializer 추가 전달
            )

        return super().finalize_response(request, response, *args, **kwargs)


class PermissionDebugMixin:
    if settings.DEBUG:

        def get_label_text(self, is_permit: bool) -> str:
            return (
                f"{Fore.GREEN}Permit{Fore.RESET}"  # colorama 라이브러리 활용
                if is_permit
                else f"{Fore.RED}Deny{Fore.RESET}"
            )

        def check_permissions(self, request: Request) -> None:
            print(f"{request.method} {request.path} has_permission")
            for permission in self.get_permissions():
                is_permit: bool = permission.has_permission(request, self)
                print(
                    f"\t{permission.__class__.__name__} = {self.get_label_text(is_permit)}"
                )
                if not is_permit:
                    self.permission_denied(
                        request,
                        message=getattr(permission, "message", None),
                        code=getattr(permission, "code", None),
                    )

        def check_object_permissions(self, request: Request, obj: Model) -> None:
            print(f"{request.method} {request.path} has_object_permission")
            for permission in self.get_permissions():
                is_permit: bool = permission.has_object_permission(request, self, obj)
                print(
                    f"\t{permission.__class__.__name__} = {self.get_label_text(is_permit)}"
                )
                if not is_permit:
                    self.permission_denied(
                        request,
                        message=getattr(permission, "message", None),
                        code=getattr(permission, "code", None),
                    )
