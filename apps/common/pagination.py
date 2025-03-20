from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from django.core.paginator import InvalidPage

from apps.common.responses import CustomResponse


class CustomPagination(PageNumberPagination):
    """
    Paginate a queryset if required, either returning a
    page object, or `None` if pagination is not configured for this view.
    """

    page_size_query_param = (
        "page_size"  # Optional: allow clients to override the page size
    )

    def paginate_queryset(self, queryset, request, view=None):
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage:
            # Raise 404 error instead of 400 for invalid pages
            raise NotFound("The page you requested could not be found.")

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        return list(self.page)

    def get_paginated_response(self, data):
        """
        Customize the paginated response to include metadata.
        """
        pagination_data = {
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,  # The serialized page data
            "per_page": self.page.paginator.per_page,
            "current_page": self.page.number,
            "last_page": self.page.paginator.num_pages,
        }
        return CustomResponse.success(
            message="Paginated data retrieved successfully.",
            data=pagination_data,
            status_code=200,
        )


class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        data = {
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        }
        return CustomResponse.success(
            message="Paginated data retrieved successfully", data=data
        )
