import uuid
from rest_framework.test import APITestCase

from datetime import timedelta
from django.utils import timezone

from apps.common.utils import TestUtil
from apps.discount.models import Coupon, Discount
from apps.orders.models.order import Order, OrderItem

from apps.shop.test_utils import TestShopUtil


class TestDiscount(APITestCase):
    cart_add_url = "/api/v1/cart/add/"
    order_create_url = "/api/v1/orders/create/"

    def setUp(self):
        self.user1 = TestUtil.verified_user()
        self.user2 = TestUtil.other_verified_user()

        # Create test products
        self.product1, self.product2, self.product3 = TestShopUtil.product(self.user1)

        self.order = Order.objects.create(
            customer=self.user1.profile,
        )

        self.other_order = Order.objects.create(
            customer=self.user1.profile,
        )

        self.paid_order = Order.objects.create(
            customer=self.user1.profile, payment_status="successful"
        )
        self.delivered_order = Order.objects.create(
            customer=self.user1.profile,
            payment_status="successful",
            shipping_status="delivered",
        )

        OrderItem.objects.create(
            order=self.order,
            product=self.product1,
            quantity=2,
            price=self.product1.price,
        )

        OrderItem.objects.create(
            order=self.other_order,
            product=self.product1,
            quantity=1,
            price=self.product1.price,
        )

        self.discount = Discount.objects.create(
            name="Test Discount",
            discount_type="fixed_amount",
            value=1000,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=10),
        )

        self.active_coupon = Coupon.objects.create(
            code="TESTCOUPON", discount=self.discount, usage_limit=10
        )

        self.expired_coupon = Coupon.objects.create(
            code="EXPIRED", discount=self.discount, usage_limit=10, used_count=10
        )

        self.apply_coupon_order_url = f"/api/v1/orders/{self.order.id}/coupons/"
        self.apply_coupon_other_order_url = (
            f"/api/v1/orders/{self.other_order.id}/coupons/"
        )
        self.paid_order_url = f"/api/v1/orders/{self.paid_order.id}/coupons/"
        self.delivered_order_url = f"/api/v1/orders/{self.delivered_order.id}/coupons/"
        self.non_existent_order_url = f"/api/v1/orders/{uuid.uuid4()}/coupons/"

    def test_apply_coupon(self):
        self.client.force_authenticate(user=self.user1)

        # Test expired coupon
        coupon_data = {"code": self.expired_coupon}
        response = self.client.post(self.apply_coupon_order_url, coupon_data)
        self.assertEqual(response.status_code, 422)

        # Test coupon does not exist
        coupon_data = {"code": "NONEXISTENT"}
        response = self.client.post(self.apply_coupon_order_url, coupon_data)
        self.assertEqual(response.status_code, 422)

        coupon_data = {"code": self.active_coupon}

        # Test order id does not exist(404)
        response = self.client.post(self.non_existent_order_url, coupon_data)
        self.assertEqual(response.status_code, 404)

        # Test success(200)
        response = self.client.post(self.apply_coupon_order_url, coupon_data)
        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()
        self.assertEqual(self.order.discounted_total, 1000)

        # Test coupon already applied to order
        response = self.client.post(self.apply_coupon_order_url, coupon_data)
        self.assertEqual(response.status_code, 422)

        # Test order has been paid for
        response = self.client.post(self.paid_order_url, coupon_data)
        self.assertEqual(response.status_code, 422)

        # Test delivered order
        response = self.client.post(self.delivered_order_url, coupon_data)
        self.assertEqual(response.status_code, 422)

        # Test if order total is 0, no payment
        response = self.client.post(self.apply_coupon_other_order_url, coupon_data)
        self.order.refresh_from_db()
        self.assertEqual(response.data["data"]["final_total"], 0)

        # Test 401
        self.client.force_authenticate(user=None)
        response = self.client.post(self.apply_coupon_order_url, coupon_data)
        self.assertEqual(response.status_code, 401)


# python manage.py test apps.discount.tests.TestDiscount.test_apply_coupon
