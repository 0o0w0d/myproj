from django.http import HttpRequest, HttpResponse, JsonResponse
from .models import Post
from .serializers import PostSerializer, PostListSerializer, PostDetailSerializer
from django.shortcuts import get_object_or_404

from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import ListAPIView, RetrieveAPIView

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
class PostListAPIView(ListAPIView):
    queryset = PostListSerializer.get_optimized_queryset()
    serializer_class = PostListSerializer


post_list = PostListAPIView.as_view()


# @api_view(["GET"])
# def post_detail(request: Request, pk: int) -> Response:
#     post = get_object_or_404(Post, pk=pk)

#     serializer = PostDetailSerializer(instance=post)
#     detail_data: ReturnDict = serializer.data

#     return Response(detail_data)


class PostRetrieveAPIView(RetrieveAPIView):
    queryset = PostDetailSerializer.get_optimized_queryset()
    serializer_class = PostDetailSerializer


post_detail = PostRetrieveAPIView.as_view()
