from datetime import timedelta
from django.utils import timezone
import uuid
from rest_framework.test import APITestCase

from apps.common.utils import TestUtil
from apps.discount.models import Discount, TieredDiscount
from apps.orders.models.order import Order
from apps.profiles.models import ShippingAddress, ShippingFee
from apps.shop.test_utils import TestShopUtil


class TestOrders(APITestCase):
    order_create_url = "/api/v1/orders/create/"
    order_history_url = "/api/v1/orders/history/"
    cart_add_url = "/api/v1/cart/add/"

    def setUp(self):
        self.user1 = TestUtil.verified_user()
        self.user2 = TestUtil.other_verified_user()

        # Create test products
        self.product1, self.product2, self.product3 = TestShopUtil.product()

        # Create shipping address for the user
        ShippingFee.objects.create(state="Lagos", fee=5000)
        self.shipping_address1 = ShippingAddress.objects.create(
            user=self.user1.profile,
            phone_number="1234567890",
            state="Lagos",
            postal_code="100001",
            city="Lagos",
            street_address="123 Test Street",
            default=True,
        )

        self.shipping_address2 = ShippingAddress.objects.create(
            user=self.user2.profile,
            phone_number="12345678",
            state="Ondo",
            postal_code="100001",
            city="Ondo",
            street_address="123 Test Street",
            default=True,
        )

        self.client.force_authenticate(user=self.user1)

        # Add product1 to cart
        cart_data = {
            "product_id": str(self.product1.id),
            "quantity": 2,
        }
        self.client.post(self.cart_add_url, cart_data)

    def test_order_create(self):
        # Test success(201)
        # No need to auth again since it is in setup

        order_data = {"shipping_id": str(self.shipping_address1.id)}
        order_data_invalid = {"shipping_id": str(uuid.uuid4())}
        order_data_invalid2 = {"shipping_id": str(self.shipping_address2.id)}

        response = self.client.post(self.order_create_url, order_data)
        self.assertEqual(response.status_code, 201)

        # Verify order was created
        self.assertTrue(Order.objects.filter(customer=self.user1.profile).exists())

        # Test 422(shipping id does not exist)
        response = self.client.post(self.order_create_url, order_data_invalid)
        self.assertEqual(response.status_code, 422)

        # Test 422(shipping id does not exist for user)
        response = self.client.post(self.order_create_url, order_data_invalid2)
        self.assertEqual(response.status_code, 422)

        # Test validation on stock availability
        # Add product2 to cart(out of stock)
        cart_data = {
            "product_id": str(self.product2.id),
            "quantity": 1,
        }
        self.client.post(self.cart_add_url, cart_data)

        response = self.client.post(self.order_create_url, order_data)
        self.assertEqual(response.status_code, 422)

        # Test validation on cart empty
        self.client.post(self.cart_add_url, None)
        response = self.client.post(self.order_create_url, order_data)
        self.assertEqual(response.status_code, 422)

        # Test 401
        self.client.force_authenticate(user=None)
        response = self.client.post(self.order_create_url, order_data)
        self.assertEqual(response.status_code, 401)

    def test_order_create_discount(self):
        order_data = {"shipping_id": str(self.shipping_address1.id)}

        # Test tiered order discount
        discount = Discount.objects.create(
            name="Test Discount",
            discount_type="tiered",
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=10),
        )
        TieredDiscount.objects.create(
            discount=discount, min_amount=1000, discount_percentage=50
        )

        response = self.client.post(self.order_create_url, order_data)

        self.assertEqual(response.status_code, 201)
        self.assertIn("Discount", response.data["data"]["discount_info"]["message"])

        # Test tiered order discount(free shipping)
        # TieredDiscount.objects.create(
        #     discount=discount, min_amount=1000, free_shipping=True
        # )

        # response = self.client.post(self.order_create_url, order_data)
        #
        # self.assertEqual(response.status_code, 201)
        # self.assertIn("Free shipping", response.data["data"]["discount_info"]["message"])
        # print(response.data["data"]["discount_info"])

    def test_order_history(self):
        # Test success(empty order)

        response = self.client.get(self.order_history_url)
        self.assertEqual(response.status_code, 200)

        self.assertIn("No orders found", response.data["message"])

        # Test success(200)
        order_data = {
            "shipping_id": str(self.shipping_address1.id),
        }

        self.client.post(self.order_create_url, order_data)
        response = self.client.get(self.order_history_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["data"][0]["items"]), 1)

        # Test 401
        self.client.force_authenticate(user=None)
        response = self.client.get(self.order_history_url)
        self.assertEqual(response.status_code, 401)


# python manage.py test apps.orders.tests.TestOrders.test_order_create
