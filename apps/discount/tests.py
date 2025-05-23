from rest_framework.test import APITestCase

from apps.common.utils import TestUtil


class TestDiscount(APITestCase):

    def setUp(self):
        self.user1 = TestUtil.verified_user()
        self.user2 = TestUtil.other_verified_user()
        
    def test_apply_coupon(self):
        # Test success(200)
        # Test 400 or 422
        # Test expired or invalid coupon
        # Test coupon already applied to order
        # Test order id does not exist(404)
        # Test order has been paid for
        # Test if order total is 0, no payment
        pass
