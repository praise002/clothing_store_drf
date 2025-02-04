from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from drf_spectacular.utils import extend_schema

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.common.serializers import SuccessResponseSerializer


class HealthCheckView(APIView):
    serializer_class = None
    
    @extend_schema(
        "/",
        summary="API Health Check",
        description="This endpoint checks the health of the API",
        responses=SuccessResponseSerializer,
        tags=["HealthCheck"],
    )
    def get(self, request):
        return Response({"message": "pong"}, status=status.HTTP_200_OK)
    


def handler404(request, exception=None):
    response = JsonResponse({"status": "failure", "message": "Not Found"})
    response.status_code = 404
    return response


def handler500(request, exception=None):
    response = JsonResponse({"status": "failure", "message": "Server Error"})
    response.status_code = 500
    return response


handler404 = handler404
handler500 = handler500

urlpatterns = [
    path("admin/", admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),
    path("api/v1/auth/", include("apps.accounts.urls")),
    # path("api/v1/profiles/", include("apps.profiles.urls")),
    
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    
    path(
        "",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    
    path("api/v1/healthcheck/", HealthCheckView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
