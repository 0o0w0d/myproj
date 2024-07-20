from django.db.models import Model, QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from rest_framework.views import APIView
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
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination

from core.mixins import (
    JSONResponseWrapperMixin,
    PermissionDebugMixin,
    TestFuncPermissionMixin,
    ActionBasedViewSetMixin,
)
from core.permissions import IsAuthorOrReadonly, make_drf_permission_class

# api.py ~= views.py

# api_view 사용 시 rest_framework의 Response, Resquest를 사용


class PostModelViewSet(ActionBasedViewSetMixin, ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadonly]
    queryset_map = {
        "list": PostListSerializer.get_optimized_queryset(),
        "retrieve": PostDetailSerializer.get_optimized_queryset(),
        "update": PostSerializer.get_optimized_queryset(),
        "partial_update": PostSerializer.get_optimized_queryset(),
        "destroy": Post.objects.all(),
    }
    serializer_class_map = {
        "list": PostListSerializer,
        "retrieve": PostDetailSerializer,
        "create": PostSerializer,
        "update": PostSerializer,
        "partial_update": PostSerializer,
    }

    # pagination_class를 지정해, 각 API마다 서로 다른 pagination class 지정 가능
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # def get_queryset(self):
    #     if self.action == "list":
    #         self.queryset = PostListSerializer.get_optimized_queryset()
    #     elif self.action == "retrieve":
    #         self.queryset = PostDetailSerializer.get_optimized_queryset()
    #     elif self.action in ("update", "partial_update"):
    #         self.queryset = PostSerializer.get_optimized_queryset()
    #     elif self.action == "destroy":
    #         self.queryset = Post.objects.all()
    #     return super().get_queryset()

    # def get_serializer_class(self):
    #     # self.request.method == "GET"  # "list" or "retrieve" => self.action 속성 사용
    #     if self.action == "list":
    #         return PostListSerializer
    #     elif self.action == "retrieve":
    #         return PostDetailSerializer
    #     elif self.action in ("create", "update", "partial_update"):
    #         return PostSerializer
    #     return super().get_serializer_class()


# post_list = PostModelViewSet.as_view(actions={"get": "list", "post": "create"})


# post_detail = PostModelViewSet.as_view(
#     actions={
#         "get": "retrieve",
#         "put": "update",
#         "patch": "partial_update",
#         "delete": "destroy",
#     }
# )


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
# class PostListAPIView(JSONResponseWrapperMixin, PermissionDebugMixin, ListAPIView):
#     queryset = PostListSerializer.get_optimized_queryset()
#     serializer_class = PostListSerializer

#     # 반복되는 내용을 사용해 mixin class 정의 (core.mixins)
#     # def finalize_response(self, request, response, *args, **kwargs):
#     #     if isinstance(request.accepted_renderer, (JSONRenderer, BrowsableAPIRenderer)):
#     #         # response.data  # 원본 응답 데이터 : ReturnList
#     #         response.data = ReturnDict(
#     #             {"ok": True, "result": response.data},  # 원본 데이터를 래핑하여 전달
#     #             serializer=response.data.serializer,  # 원본 데이터의 serializer 추가 전달
#     #         )

#     #     return super().finalize_response(request, response, *args, **kwargs)


# post_list = PostListAPIView.as_view()


# # @api_view(["GET"])
# # def post_detail(request: Request, pk: int) -> Response:
# #     post = get_object_or_404(Post, pk=pk)

# #     serializer = PostDetailSerializer(instance=post)
# #     detail_data: ReturnDict = serializer.data

# #     return Response(detail_data)


# class PostRetrieveAPIView(
#     JSONResponseWrapperMixin, PermissionDebugMixin, RetrieveAPIView
# ):
#     queryset = PostDetailSerializer.get_optimized_queryset()
#     serializer_class = PostDetailSerializer


# post_detail = PostRetrieveAPIView.as_view()


# class PostCreateAPIView(PermissionDebugMixin, CreateAPIView):
#     serializer_class = PostSerializer
#     permission_classes = [IsAuthenticated]

#     # 전달받은 내용이 아닌, 추가 내용 전달을 위해서 perform_create 메서드 재정의
#     def perform_create(self, serializer):
#         serializer.save(author=self.request.user)


# post_new = PostCreateAPIView.as_view()


# class PostUpdateAPIView(PermissionDebugMixin, TestFuncPermissionMixin, UpdateAPIView):
#     queryset = PostSerializer.get_optimized_queryset()
#     serializer_class = PostSerializer
#     # permission_classes = [IsAuthorOrReadonly]
#     # permission_classes = [
#     #     make_drf_permission_class(
#     #         class_name="PostUpdateAPIView",
#     #         permit_safe_methods=True,
#     #         has_permission_test_func=lambda request, view: request.user.is_authenticated,
#     #         has_object_permission_test_func=(
#     #             lambda request, view, obj: obj.author == request.user
#     #         ),
#     #     ),
#     # ]

#     # TestFuncPermissionMixin에서 상속받아
#     # APIView에서 has_permission와 has_object_permission 메서드를 직접 재정의 가능
#     TEST_FUNC_PERMISSION_CLASS_NAME = "PostUpdateAPIView"

#     def has_permission(self, request: Request, view: APIView) -> bool:
#         if request.method in SAFE_METHODS:
#             return True
#         return request.user.is_authenticated

#     def has_object_permission(
#         self, request: Request, view: APIView, obj: Model
#     ) -> bool:
#         if request.method in SAFE_METHODS:
#             return True
#         return request.user == obj.author


# post_edit = PostUpdateAPIView.as_view()


# class PostDeleteAPIView(PermissionDebugMixin, DestroyAPIView):
#     # 레코드 조회를 위해 쿼리셋 지정 필요
#     # 삭제에는 serializer 필요 X
#     queryset = Post.objects.all()
#     permission_classes = [IsAuthorOrReadonly]


# post_delete = PostDeleteAPIView.as_view()
