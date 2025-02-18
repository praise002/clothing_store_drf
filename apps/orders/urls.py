from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.OrderCreateView.as_view()),
    path("history/", views.OrderHistoryView.as_view()),
]
