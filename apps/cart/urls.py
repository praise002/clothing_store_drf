from django.urls import path
from .import views

urlpatterns = [
    path('', views.CartDetailView.as_view()),
    path('add/', views.CartAddView.as_view()),
    path('remove/<str:product_id>/', views.CartRemoveView.as_view()),
]