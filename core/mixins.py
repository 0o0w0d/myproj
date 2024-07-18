from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import permissions
from rest_framework.views import APIView

from typing import List
from colorama import Fore
from django.conf import settings
from django.db.models import Model
from .permissions import make_drf_permission_class


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


class TestFuncPermissionMixin:
    TEST_FUNC_PERMISSION_CLASS_NAME = None

    @classmethod
    def get_test_func_permission_instance(cls) -> permissions.BasePermission:
        permission_class = make_drf_permission_class(
            class_name=cls.TEST_FUNC_PERMISSION_CLASS_NAME or cls.__name__,
            # *_test_func_name 속성이 지정되면, 이 권한 클래스가 사용된 APIView 클래스에서
            # 지정 이름의 메서드를 찾습니다.
            has_permission_test_func_name="has_permission",
            has_object_permission_test_func_name="has_object_permission",
        )
        return permission_class()

    def get_permissions(self) -> List[permissions.BasePermission]:
        # 기존 permission_classes 설정에 권한 정책을 추가하는 방식으로 동작
        return super().get_permissions() + [self.get_test_func_permission_instance()]

    def has_permission(self, request: Request, view: APIView) -> bool:
        return True

    def has_object_permission(
        self, request: Request, view: APIView, obj: Model
    ) -> bool:
        return True
