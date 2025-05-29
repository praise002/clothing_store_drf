import uuid
from rest_framework.test import APITestCase

from apps.common.utils import TestUtil
from apps.orders.models.order import Order, OrderItem
from apps.shop.test_utils import TestShopUtil


class TestPayments(APITestCase):
    initiate_payment_flw_url = "/api/v1/payments/flw/initiate-payment/"
    initiate_payment_paystack_url = "/api/v1/payments/paystack/initialize-transaction/"

    def setUp(self):
        self.user = TestUtil.verified_user()

        # Create test products
        self.product1, self.product2, self.product3 = TestShopUtil.product()

        self.order = Order.objects.create(
            customer=self.user.profile,
        )

        self.paid_order = Order.objects.create(
            customer=self.user.profile, payment_status="successful"
        )

        OrderItem.objects.create(
            order=self.order,
            product=self.product1,
            quantity=2,
            price=self.product1.price,
        )

    def test_flw(self):
        self.client.force_authenticate(user=self.user)

        # Test 422(order_id does not exist)
        payment_data = {"order_id": uuid.uuid4(), "payment_method": "flutterwave"}
        response = self.client.post(self.initiate_payment_flw_url, payment_data)

        self.assertEqual(response.status_code, 422)

        # Test 400 or 422
        invalid_payment_data = {"order_id": self.order.id, "payment_method": ""}
        response = self.client.post(self.initiate_payment_flw_url, invalid_payment_data)

        self.assertEqual(response.status_code, 422)

        payment_data = {"order_id": self.order.id, "payment_method": "flutterwave"}

        # Test success(200)
        response = self.client.post(self.initiate_payment_flw_url, payment_data)

        self.assertEqual(response.status_code, 200)

        # Test payment status if paid
        payment_paid_data = {
            "order_id": self.paid_order.id,
            "payment_method": "flutterwave",
        }
        response = self.client.post(self.initiate_payment_flw_url, payment_paid_data)

        # Test 401
        self.client.force_authenticate(user=None)
        response = self.client.post(self.initiate_payment_flw_url, payment_data)

    def test_paystack(self):
        self.client.force_authenticate(user=self.user)

        # Test 422(order_id does not exist)
        payment_data = {"order_id": uuid.uuid4(), "payment_method": "paystack"}
        response = self.client.post(self.initiate_payment_paystack_url, payment_data)

        self.assertEqual(response.status_code, 422)

        # Test 400 or 422
        invalid_payment_data = {"order_id": self.order.id, "payment_method": "flw"}
        response = self.client.post(
            self.initiate_payment_paystack_url, invalid_payment_data
        )

        self.assertEqual(response.status_code, 422)

        payment_data = {"order_id": self.order.id, "payment_method": "paystack"}

        # Test success(200)
        response = self.client.post(self.initiate_payment_paystack_url, payment_data)

        self.assertEqual(response.status_code, 200)

        # Test payment status if paid
        payment_paid_data = {
            "order_id": self.paid_order.id,
            "payment_method": "flutterwave",
        }
        response = self.client.post(
            self.initiate_payment_paystack_url, payment_paid_data
        )

        # Test 401
        self.client.force_authenticate(user=None)
        response = self.client.post(self.initiate_payment_paystack_url, payment_data)


# python manage.py test apps.payments.tests.TestPayments.test_flw
