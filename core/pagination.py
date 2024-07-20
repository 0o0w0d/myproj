from typing import Type, cast, Literal
from rest_framework.pagination import PageNumberPagination, BasePagination
from rest_framework import pagination as drf_pagination
import re


def make_pagination_class(
    cls_type: Literal["page_number", "limit_offset", "cursor"],
    page_size: int,
    max_limit: int = None,
    cursor_ordering: str = None,
) -> Type[BasePagination]:
    """
    class type에 따라 각각 다른 Pagination class를 생성하는 class factory function
        - 'page_number'
            : page_size에 따라 동적으로 pagination class 생성
        - 'limit_offset'
            : max_limit와 page_size(default_limit)에 따라 동적으로 pagination class 생성
        - 'cursor'
            : cursor_ordering(ordering)과 page_size에 따라 동적으로 pagination class 생성
    """
    base_cls_name = f"{cls_type.title().replace('_', '')}Pagination"
    base_cls = getattr(drf_pagination, base_cls_name)

    if cls_type == "page_number":
        cls_name = f"{base_cls_name}withPageSize{page_size}"
        attrs = {"page_size": page_size}
    elif cls_type == "limit_offset":
        cls_name = f"{base_cls_name}withDefaultLimit{page_size}AndMaxLimit{max_limit}"
        attrs = {"default_limit": page_size, "max_limit": max_limit}
    elif cls_type == "cursor":
        ordering = (cursor_ordering or "").title().replace("_", "")
        ordering = re.sub(r"^[+-]", "", ordering)
        cls_name = f"{base_cls_name}withPageSize{page_size}AndOrdering{ordering}"
        attrs = {"page_size": page_size, "ordering": cursor_ordering}
    else:
        raise NotImplementedError(f"Not implemented cls_type : {cls_type}")

    cls = type(cls_name, (base_cls,), attrs)
    return cast(Type[drf_pagination.BasePagination], cls)
