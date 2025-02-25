from . import views
from django.urls import path
from .webhooks import flw_payment_webhook as wh

urlpatterns = [
    path("flw/initiate-payment/", views.InitiatePaymentFLW.as_view()),
    path("flw/payment/callback/", views.payment_callback_flw),
    path("flw-webhook/", wh),
    path("paystack/initialize-transaction/", views.InitiatePaymentPaystack.as_view()),
]

# https://66d7-185-107-57-10.ngrok-free.app/success/?status=successful&tx_ref=f556e708-d829-4de9-9d20-e43f281c3cd3&transaction_id=8335507
