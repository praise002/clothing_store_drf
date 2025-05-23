from rest_framework.test import APITestCase

from apps.common.utils import TestUtil


class TestOrders(APITestCase):
    order_create_url = "/api/v1/create/"
    order_history_url = "/api/v1/history/"

    def setUp(self):
        self.user1 = TestUtil.verified_user()
        self.user2 = TestUtil.other_verified_user()

    def test_order_create(self):
        # Test success(201)
        # Test 400 or 422
        # Test 401
        # Test if shipping address does not exist it raises error
        # Test validation on cart empty
        # Test validation on stock availability
        # Test tiered order discount
        pass

    def test_order_history(self):
        # Test success(200)
        # Test 401
        pass
