from django.urls import path

from . import views
from .webhooks import flw_payment_webhook as fwh
from .webhooks import paystack_webhook as pwh

urlpatterns = [
    path("flw/initiate-payment/", views.InitiatePaymentFLW.as_view()),
    path("flw/payment-callback/", views.PaymentCallbackFlw.as_view(), name="payment_callback"),
    path("flw-webhook/", fwh),
    path("paystack/initialize-transaction/", views.InitiatePaymentPaystack.as_view()),
    path("paystack-webhook/", pwh),
]

