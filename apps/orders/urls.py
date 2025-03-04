from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.OrderCreateView.as_view()),
    path("history/", views.OrderHistoryView.as_view()),
    path("<uuid:order_id>/cancel/", views.CancelOrderAPIView.as_view()),
]
