from django.urls import path

from . import views

urlpatterns = [
    path("site-detail/", views.SiteDetailView.as_view()),
    path("teams/", views.TeamMemberListView.as_view()),
    path("contact/", views.MessageCreateView.as_view()),
]
