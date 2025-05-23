from django.urls import path
from . import views

urlpatterns = [
    # path("profile/", views.MyProfileView.as_view()),
    path("profile/", views.MyProfileViewGeneric.as_view()),
    path("profile/avatar/", views.AvatarUpdateView.as_view()),
    # Create a new shipping address
    path(
        "shipping-addresses/add/",
        views.ShippingAddressCreateView.as_view(),
    ),
    # List all shipping addresses for the authenticated user
    path(
        "shipping-addresses/",
        views.ShippingAddressListGenericView.as_view(),
    ),
    # Retrieve, update, or delete a specific shipping address
    path(
        "shipping-addresses/<uuid:pk>/",
        views.ShippingAddressDetailGenericView.as_view(),
    ),
    # path(
    #     "shipping-addresses/<uuid:pk>/",
    #     views.ShippingAddressDetailView.as_view(),
    # ),
]
