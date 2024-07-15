from django.http import HttpRequest, HttpResponse, JsonResponse
from .models import Post


def post_list(request: HttpRequest) -> HttpResponse:
    post_qs = Post.objects.all()

    return JsonResponse(list(post_qs.values()), safe=False)
