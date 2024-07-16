from django.http import HttpRequest, HttpResponse, JsonResponse
from .models import Post
from .serializers import PostSerializer, PostListSerializer, PostDetailSerializer
from django.shortcuts import get_object_or_404

from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.renderers import BaseRenderer, JSONRenderer, BrowsableAPIRenderer

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

    # 응답 데이터 후처리를 위해 list 메서드 재정의
    def list(self, request: Request, *args, **kwargs):
        response: Response = super().list(request, *args, **kwargs)

        # json 응답일 경우에만 후처리를 위해 JSONRenderer나 BrowsableAPIRenderer를 사용하는지 확인
        if isinstance(request.accepted_renderer, (JSONRenderer, BrowsableAPIRenderer)):
            # response.data  # 원본 응답 데이터 : ReturnList
            response.data = ReturnDict(
                {"ok": True, "result": response.data},  # 원본 데이터를 래핑하여 전달
                serializer=response.data.serializer,  # 원본 데이터의 serializer 추가 전달
            )

        return response


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

    # 응답 데이터 후처리를 위해 retrieve 메서드 재정의
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        response.data = ReturnDict(
            {"ok": True, "result": response.data},
            serializer=response.data.serializer,
        )
        return response


post_detail = PostRetrieveAPIView.as_view()
