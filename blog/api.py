from django.http import HttpRequest, HttpResponse, JsonResponse
from .models import Post
from .serializers import PostSerializer, PostListSerializer, PostDetailSerializer
from django.shortcuts import get_object_or_404

from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView,
)
from rest_framework.renderers import BaseRenderer, JSONRenderer, BrowsableAPIRenderer
from rest_framework.permissions import IsAuthenticated

from core.mixins import JSONResponseWrapperMixin, PermissionDebugMixin
from core.permissions import IsAuthorOrReadonly, make_drf_permission_class

# api.py ~= views.py

# api_view 사용 시 rest_framework의 Response, Resquest를 사용


# @api_view(["GET"])
# def post_list(request: Request) -> Response:
#     # 모든 Post 객체를 가져오지만 content 필드는 지연 로드
#     # N + 1 문제 해결을 위해 author 필드에 대한 즉시 로딩 수행
#     post_qs = Post.objects.all().defer("content").select_related("author")

#     # list일 때 many 인자를 지정하지 않으면 모델 instance로 인식해 error
#     serializer = PostListSerializer(instance=post_qs, many=True)
#     # serializer의 data 속성을 통해 python 기본 데이터 타입으로 변환된 값 참조
#     list_data: ReturnList = serializer.data

#     return Response(list_data)


# django generic class 기반으로 변경
class PostListAPIView(JSONResponseWrapperMixin, PermissionDebugMixin, ListAPIView):
    queryset = PostListSerializer.get_optimized_queryset()
    serializer_class = PostListSerializer

    # 반복되는 내용을 사용해 mixin class 정의 (core.mixins)
    # def finalize_response(self, request, response, *args, **kwargs):
    #     if isinstance(request.accepted_renderer, (JSONRenderer, BrowsableAPIRenderer)):
    #         # response.data  # 원본 응답 데이터 : ReturnList
    #         response.data = ReturnDict(
    #             {"ok": True, "result": response.data},  # 원본 데이터를 래핑하여 전달
    #             serializer=response.data.serializer,  # 원본 데이터의 serializer 추가 전달
    #         )

    #     return super().finalize_response(request, response, *args, **kwargs)


post_list = PostListAPIView.as_view()


# @api_view(["GET"])
# def post_detail(request: Request, pk: int) -> Response:
#     post = get_object_or_404(Post, pk=pk)

#     serializer = PostDetailSerializer(instance=post)
#     detail_data: ReturnDict = serializer.data

#     return Response(detail_data)


class PostRetrieveAPIView(
    JSONResponseWrapperMixin, PermissionDebugMixin, RetrieveAPIView
):
    queryset = PostDetailSerializer.get_optimized_queryset()
    serializer_class = PostDetailSerializer


post_detail = PostRetrieveAPIView.as_view()


class PostCreateAPIView(PermissionDebugMixin, CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    # 전달받은 내용이 아닌, 추가 내용 전달을 위해서 perform_create 메서드 재정의
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


post_new = PostCreateAPIView.as_view()


class PostUpdateAPIView(PermissionDebugMixin, UpdateAPIView):
    queryset = PostSerializer.get_optimized_queryset()
    serializer_class = PostSerializer
    # permission_classes = [IsAuthorOrReadonly]
    permission_classes = [
        make_drf_permission_class(
            class_name="PostUpdateAPIView",
            permit_safe_methods=True,
            has_permission_test_func=lambda request, view: request.user.is_authenticated,
            has_object_permission_test_func=(
                lambda request, view, obj: obj.author == request.user
            ),
        ),
    ]


post_edit = PostUpdateAPIView.as_view()


class PostDeleteAPIView(PermissionDebugMixin, DestroyAPIView):
    # 레코드 조회를 위해 쿼리셋 지정 필요
    # 삭제에는 serializer 필요 X
    queryset = Post.objects.all()
    permission_classes = [IsAuthorOrReadonly]


post_delete = PostDeleteAPIView.as_view()
