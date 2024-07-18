from django.db.models import Model
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView
from typing import Callable, Type, cast


class IsAuthorOrReadonly(permissions.BasePermission):

    # 1차 필터
    def has_permission(self, request: Request, view: APIView) -> bool:
        # GET, HEAD, OPTIONS -> 인스턴스에 영향을 주지 않음
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    # 2차 필터 : 개별 조회, 개별 수정, 개별 삭제에 대한 (get_object 메서드 수행 시에만 수행)
    def has_object_permission(self, request: Request, view: APIView, obj: Model):
        if request.method in permissions.SAFE_METHODS:
            return True

        # 삭제는 관리자만 가능
        # if request.method == "DELETE":
        #     return request.user.is_staff

        if not hasattr(obj, "author"):  # author 필드가 있다면레코드 조회 수행
            return False

        return obj.author == request.user


# mixin 사용 -> 재사용성을 높이고 코드 중복을 줄임
# 권한 클래스 팩토리 함수 <make_drf_permission_class>
# BasePermission을 상속받지 않아도 함수 호출만으로 권한 호출을 동적으로 생성
# APIView 호출 시 구현 가능
# APIView 구현 코드와 가깝게 권한 설정이 위치해있어 가독성 + 유지보수성 향상
def make_drf_permission_class(
    class_name: str = "PermissionClass",
    permit_safe_methods: bool = False,
    has_permission_test_func: Callable[[Request, APIView], bool] = None,
    has_permission_test_func_name: str = None,
    has_object_permission_test_func: Callable[[Request, APIView, Model], bool] = None,
    has_object_permission_test_func_name: str = None,
) -> Type[permissions.BasePermission]:

    def has_permission(self, request: Request, view: APIView) -> bool:
        if permit_safe_methods and request.method in permissions.SAFE_METHODS:
            return True
        if has_permission_test_func is not None:
            return has_permission_test_func(request, view)
        if has_permission_test_func_name is not None:
            test_func = getattr(view, has_permission_test_func_name)
            return test_func(request, view)
        return True

    def has_object_permission(
        self, request: Request, view: APIView, obj: Model
    ) -> bool:
        if permit_safe_methods and request.method in permissions.SAFE_METHODS:
            return True
        if has_object_permission_test_func is not None:
            return has_object_permission_test_func(request, view, obj)
        if has_object_permission_test_func_name is not None:
            test_func = getattr(view, has_object_permission_test_func_name)
            return test_func(request, view, obj)
        return True

    permission_class = type(
        class_name,
        (permissions.BasePermission,),
        {
            "has_permission": has_permission,
            "has_object_permission": has_object_permission,
        },
    )

    return cast(Type[permissions.BasePermission], permission_class)
