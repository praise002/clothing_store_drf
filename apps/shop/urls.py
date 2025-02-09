from django.urls import path

# from django.utils.translation import gettext_lazy as _
from . import views

app_name = "shop"

urlpatterns = [
    path("products/", views.ProductListView.as_view()),
    path(
        "products/<str:pk>/<slug:slug>/",
        views.ProductRetrieveView.as_view(),
    ),
    path("categories/", views.CategoryListView.as_view()),
    path(
        "categories/<slug:slug>/products/",
        views.CategoryProductsView.as_view(),
    ),
    path("wishlist/", views.WishlistView.as_view()),
    path("wishlist/<str:product_id>/", views.WishlistUpdateDestroyView.as_view()),
]
