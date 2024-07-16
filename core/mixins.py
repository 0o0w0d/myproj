from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.response import Response
from rest_framework.request import Request


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
