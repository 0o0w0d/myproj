from django.db.models import Model
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView


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
