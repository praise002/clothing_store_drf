from rest_framework.test import APITestCase

from apps.common.utils import TestUtil


class TestCart(APITestCase):
    cart_detail_url = "/api/v1/carts/"
    cart_add_update_url = "/api/v1/carts/add/"

    def setUp(self):
        self.user1 = TestUtil.verified_user()
        self.user2 = TestUtil.other_verified_user()

    def test_cart_detail(self):
        # Test success
        # Test 401
        # Test that product price in cart updates when price is updated by admin
        # Test that product price in cart updates when discount is applied or updated by admin
        pass

    def test_add_update_product_in_cart(self):
        # Test success
        # Test 401
        # Test 404(product does not exist)
        # Test 400 or 422
        pass

    def test_remove_product_cart(self):
        # Test success(204)
        # Test 401
        # Test 404(product does not exist)
        pass
