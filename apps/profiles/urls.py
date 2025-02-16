from django.urls import path
from . import views

urlpatterns = [
    # path("account/", views.MyProfileView.as_view()),
    path("account/", views.MyProfileViewGeneric.as_view()),
    # Create a new shipping address
    path(
        "shipping-addresses/add/",
        views.ShippingAddressCreateView.as_view(),
        name="shipping-address-create",
    ),
    # List all shipping addresses for the authenticated user
    path(
        "shipping-addresses/",
        views.ShippingAddressListView.as_view(),
        name="shipping-address-list",
    ),
    # Retrieve, update, or delete a specific shipping address
    path(
        "shipping-addresses/<str:pk>/",
        views.ShippingAddressDetailView.as_view(),
        name="shipping-address-detail",
    ),
]
