from typing import Type, cast
from rest_framework.pagination import PageNumberPagination, BasePagination


# page_size를 동적으로 받아 pagination 클래스를 생성하는 class factory 함수
def make_pagination_class(page_size: int) -> Type[BasePagination]:
    cls_name = f"PageNumberPagination{page_size}"
    base_cls = PageNumberPagination
    attrs = {"page_size": page_size}

    cls = type(cls_name, (base_cls,), attrs)
    return cast(Type[BasePagination], cls)
