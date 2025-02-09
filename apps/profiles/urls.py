from django.urls import path
from . import views

urlpatterns = [
    # path("account/", views.MyProfileView.as_view()),
    path("account/", views.MyProfileViewGeneric.as_view()),
]
