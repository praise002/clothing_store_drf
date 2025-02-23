from . import views
from django.urls import path
from .webhooks import flw_payment_webhook as wh

urlpatterns = [
    path("initiate-payment/", views.InitiatePayment.as_view()),
    path("payment/callback/", views.payment_callback, name="payment_callback"),
    path("webhook/", wh),
]

# https://66d7-185-107-57-10.ngrok-free.app/success/?status=successful&tx_ref=f556e708-d829-4de9-9d20-e43f281c3cd3&transaction_id=8335507
