from rest_framework.test import APITestCase

from apps.common.utils import TestUtil

class TestShop(APITestCase):
    product_list_url = "/api/v1/products/"
    category_list_url = "/api/v1/categories/"
    wishlist_url = "/api/v1/wishlist/"
    review_create = "/api/v1/reviews/create/"
    
    def setUp(self):
        self.user1 = TestUtil.verified_user()
        self.user2 = TestUtil.other_verified_user()
    
    def test_product_list(self):
        # Test success
        pass
    
    def test_product_retrieve(self):
        # Test success
        # Test 404(out od stuck or doesn't exist)
        pass
    
    def test_product_reviews_retrieve(self):
        # Test success
        # Test 404(out od stuck or doesn't exist)
        pass
    
    def test_review_create(self):
        # Test success
        # Test 400 0r 422
        # Test 401
        pass
    
    def test_review_update(self):
        # Test success
        # Test 400 0r 422
        # Test 401
        # Test 403(update someone review)
        pass
    
    def test_category_list(self):
        # Test success
        pass
    
    def test_category_product_list(self):
        # Test success
        # Test 404(non-existent category)
        pass
    
    def test_wishlist_get(self):
        # Test success
        # Test 401
        pass
    
    def test_add_to_wishlist(self):
        # Test success
        # Test you can only add to your wishlist
        # Test 401
        # Test 404(product_id does not exist)
        # Test 400 or 422
        # Test 409(products exists in wishlist)
        pass
    
    def test_remove_product_from_wishlist(self):
        # Test success
        # Test 401
        # Test 404(product_id not in wishlist)
        # Test 422
        pass
    
# python manage.py test apps.profiles.tests.TestProfiles.test_shipping_address_create
