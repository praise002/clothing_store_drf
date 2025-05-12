from django.urls import path
from . import views

urlpatterns = [
    path('orders/<uuid:order_id>/coupons/', views.ApplyCouponView.as_view()),
]