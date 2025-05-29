from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
import uuid
from rest_framework.test import APITestCase


from apps.common.utils import TestUtil
from apps.discount.models import Discount, ProductDiscount
from apps.shop.models import Product
from apps.shop.test_utils import TestShopUtil


class TestCart(APITestCase):
    cart_detail_url = "/api/v1/cart/"
    cart_add_update_url = "/api/v1/cart/add/"

    def setUp(self):
        self.user = TestUtil.verified_user()
        self.user2 = TestUtil.other_verified_user()

        # Create test products
        self.product1, self.product2, self.product3 = TestShopUtil.product()

        # Set up URLs with parameters
        self.cart_remove_url = f"/api/v1/cart/remove/{self.product1.id}/"
        self.nonexistent_product_remove_url = f"/api/v1/cart/remove/{uuid.uuid4()}/"

    def test_cart_detail(self):
        # Test success authenticated
        self.client.force_authenticate(user=self.user)

        # Test empty cart
        response = self.client.get(self.cart_detail_url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data["data"]["items"], [])

        # Add item to cart first
        cart_data = {
            "product_id": str(self.product1.id),
            "quantity": 2,
        }
        self.client.post(self.cart_add_update_url, cart_data)

        # Test cart with items
        response = self.client.get(self.cart_detail_url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data["data"]["items"]), 1)

        # Get initial cart response to check price

        initial_price = Decimal(response.data["data"]["items"][0]["price"])

        initial_total = response.data["data"]["total_price"]

        # Switch to second user
        self.client.force_authenticate(user=self.user2)

        # Second user's cart should be empty
        response = self.client.get(self.cart_detail_url)
        self.assertEqual(len(response.data["data"]["items"]), 0)

        # Test that product price in cart updates when price is updated by admin
        self.client.force_authenticate(user=self.user)
        original_price = self.product1.price
        Product.objects.filter(id=self.product1.id).update(price=original_price * 5)
        product = Product.objects.get(id=self.product1.id)

        response = self.client.get(self.cart_detail_url)
        self.assertEqual(response.status_code, 200)

        updated_price = Decimal(response.data["data"]["items"][0]["price"])
        updated_total = response.data["data"]["total_price"]

        # Verify prices were updated correctly
        self.assertEqual(updated_price, initial_price * 5)
        self.assertEqual(updated_total, initial_total * 5)

        # Test that product price in cart updates when discount is applied or updated by admin
        discount = Discount.objects.create(
            name="Test Discount",
            discount_type="percentage",
            value=10,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=10),
        )
        ProductDiscount.objects.create(discount=discount, product=self.product1)

        response = self.client.get(self.cart_detail_url)
        self.assertEqual(response.status_code, 200)

        # Test 401
        self.client.force_authenticate(user=None)
        response = self.client.get(self.cart_detail_url)
        self.assertEqual(response.status_code, 401)

    def test_add_update_product_in_cart(self):
        # Test success - add new product
        self.client.force_authenticate(user=self.user)

        cart_data = {"product_id": str(self.product1.id), "quantity": 2}
        response = self.client.post(self.cart_add_update_url, cart_data)
        self.assertEqual(response.status_code, 200)

        # Verify cart has the item
        response = self.client.get(self.cart_detail_url)
        self.assertEqual(len(response.data["data"]["items"]), 1)

        # Test success - update existing product (increase quantity)
        cart_data = {
            "product_id": str(self.product1.id),
            "quantity": 3,
            "override": True,
        }
        response = self.client.post(self.cart_add_update_url, cart_data)
        self.assertEqual(response.status_code, 200)

        # Verify quantity was updated
        response = self.client.get(self.cart_detail_url)
        cart_item = response.data["data"]["items"][0]
        self.assertEqual(cart_item["quantity"], 3)

        # Test 404 - product does not exist
        cart_data = {"product_id": str(uuid.uuid4()), "quantity": 1}
        response = self.client.post(self.cart_add_update_url, cart_data)
        self.assertEqual(response.status_code, 404)

        # Test 400 - insufficient stock (assuming product2 has stock=0)
        cart_data = {"product_id": str(self.product2.id), "quantity": 1}
        response = self.client.post(self.cart_add_update_url, cart_data)
        self.assertEqual(response.status_code, 404)

        # Test validation error - negative quantity
        cart_data = {"product_id": str(self.product1.id), "quantity": -1}
        response = self.client.post(self.cart_add_update_url, cart_data)
        self.assertEqual(response.status_code, 422)

        # Test 401 for unauthenticated
        self.client.force_authenticate(user=None)
        response = self.client.post(self.cart_add_update_url, cart_data)
        self.assertEqual(response.status_code, 401)

    def test_remove_product_cart(self):
        # Add product to cart first
        self.client.force_authenticate(user=self.user)
        cart_data = {"product_id": str(self.product1.id), "quantity": 2}
        self.client.post(self.cart_add_update_url, cart_data)

        # Test success - 204 No Content
        response = self.client.delete(self.cart_remove_url)
        self.assertEqual(response.status_code, 204)

        # Verify product was removed
        response = self.client.get(self.cart_detail_url)
        self.assertEqual(len(response.data["data"]["items"]), 0)

        response = self.client.delete(self.nonexistent_product_remove_url)
        self.assertEqual(response.status_code, 404)

        # Test 401 for unauthenticated
        self.client.force_authenticate(user=None)
        response = self.client.delete(self.cart_remove_url)
        self.assertEqual(response.status_code, 401)


# python manage.py test apps.cart.tests.TestCart.test_cart_detail
