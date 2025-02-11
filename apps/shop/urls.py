from django.urls import path
from . import views


urlpatterns = [
    path("products/", views.ProductListGenericView.as_view()),
    path(
        "products/<str:pk>/<slug:slug>/",
        views.ProductRetrieveView.as_view(),
    ),
    path("categories/", views.CategoryListGenericView.as_view()),
    path(
        "categories/<slug:slug>/products/",
        views.CategoryProductsGenericView.as_view(),
    ),
    path("wishlist/", views.WishlistGenericView.as_view()),
    path("wishlist/<str:product_id>/", views.WishlistUpdateDestroyView.as_view()),
]
