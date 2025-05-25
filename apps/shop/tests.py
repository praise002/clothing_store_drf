import uuid
from rest_framework.test import APITestCase

from apps.common.utils import TestUtil

from apps.shop.models import Wishlist
from apps.shop.test_utils import TestShopUtil


class TestShop(APITestCase):
    product_list_url = "/api/v1/products/"
    category_list_url = "/api/v1/categories/"
    wishlist_url = "/api/v1/wishlist/"
    review_create_url = "/api/v1/reviews/create/"

    def setUp(self):
        self.user1 = TestUtil.verified_user()
        self.user2 = TestUtil.other_verified_user()
        self.product1, self.product2, self.product3 = TestShopUtil.product()
        self.review = TestShopUtil.review()
        self.wishlist, _ = Wishlist.objects.get_or_create(profile=self.user1.profile)
        self.wishlist.products.add(self.product2)

        self.product_detail_url = (
            f"/api/v1/products/{self.product1.pk}/{self.product1.slug}/"
        )
        self.out_of_stock_product_url = (
            f"/api/v1/products/{self.product2.pk}/{self.product2.slug}/"
        )
        self.nonexistent_product_url = (
            f"/api/v1/products/{self.product1.pk}/non-existent-slug/"
        )
        self.product_reviews_url = (
            f"/api/v1/products/{self.product3.pk}/{self.product3.slug}/reviews/"
        )

        self.review_update_url = f"/api/v1/reviews/{self.review.pk}/"
        self.nonexistent_review_url = f"/api/v1/reviews/{uuid.uuid4()}/"

        # Create an order with a delivered product for testing reviews
        self.order_item = TestShopUtil.order_item_for_review(
            product=self.product1, customer=self.user1.profile
        )

        self.category1_url = (
            f"/api/v1/categories/{self.product1.category.slug}/products/"
        )
        self.nonexistent_category_url = f"/api/v1/categories/non-existent/products/"

        self.add_to_wishlist_url = f"/api/v1/wishlist/{self.product3.id}/"
        self.remove_from_wishlist_url = f"/api/v1/wishlist/{self.product2.id}/"
        self.nonexistent_product_wishlist_url = f"/api/v1/wishlist/{uuid.uuid4()}/"

    def test_product_list(self):
        # Test success
        response = self.client.get(self.product_list_url)
        print(response.json())
        print(len(response.json()))
        print(response.data["data"]["results"])
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data["data"])

    def test_product_retrieve(self):
        # Test success
        response = self.client.get(self.product_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["name"], "Test Product 1")
        print(response.json())

        # Test 404 for non-existent product
        response = self.client.get(self.nonexistent_product_url)
        self.assertEqual(response.status_code, 404)

        # Test 404(out of stuck or doesn't exist)
        response = self.client.get(self.out_of_stock_product_url)
        self.assertEqual(response.status_code, 404)

    def test_product_reviews_retrieve(self):
        # Test success
        response = self.client.get(self.product_reviews_url)
        self.assertEqual(response.status_code, 200)
        print(response.json())

        print(len(response.json()))

        # Test 404 for non-existent product
        nonexistent_product_reviews_url = (
            f"/api/v1/products/{self.product3.pk}/non-existent-slug/reviews/"
        )
        response = self.client.get(nonexistent_product_reviews_url)
        self.assertEqual(response.status_code, 404)

    def test_review_create(self):
        # Test success for authenticated user who purchased the product
        self.client.force_authenticate(user=self.user1)

        review_data = {
            "product": str(self.product1.id),
            "text": "This is a great product!",
            "rating": 5,
        }

        response = self.client.post(self.review_create_url, review_data)
        self.assertEqual(response.status_code, 201)
        print(response.json())

        # Test 422 for has reviewed
        response = self.client.post(self.review_create_url, review_data)
        self.assertEqual(response.status_code, 422)
        print(response.json())

        # Test 422 for invalid rating
        invalid_data = {
            "product": str(self.product1.id),
            "text": "This is a great product!",
            "rating": 6,  # Invalid rating
        }

        response = self.client.post(self.review_create_url, invalid_data)
        self.assertEqual(response.status_code, 422)

        # Test 401 for unauthenticated user
        self.client.force_authenticate(user=None)

        response = self.client.post(self.review_create_url, review_data)
        self.assertEqual(response.status_code, 401)

        # Test 422 for user who hasn't purchased the product
        self.client.force_authenticate(user=self.user2)

        response = self.client.post(self.review_create_url, review_data)
        self.assertEqual(response.status_code, 422)

    def test_review_update(self):
        # Test success for review owner
        self.client.force_authenticate(user=self.user1)

        update_data = {"text": "Updated review text", "rating": 4}

        response = self.client.patch(self.review_update_url, update_data)
        self.assertEqual(response.status_code, 200)
        print(response.json())

        # Test 422 for invalid rating
        invalid_update = {"rating": 6}  # Invalid rating

        response = self.client.patch(self.review_update_url, invalid_update)
        self.assertEqual(response.status_code, 422)

        # Test 401 for unauthenticated user
        self.client.force_authenticate(user=None)

        response = self.client.patch(self.review_update_url, update_data)
        self.assertEqual(response.status_code, 401)

        # Test 403 for user trying to update someone else's review
        self.client.force_authenticate(user=self.user2)

        response = self.client.patch(self.review_update_url, update_data)
        self.assertEqual(response.status_code, 403)

        # Test 404 for non-existent review
        self.client.force_authenticate(user=self.user1)

        response = self.client.patch(self.nonexistent_review_url, update_data)
        self.assertEqual(response.status_code, 404)

    def test_category_list(self):
        # Test success
        response = self.client.get(self.category_list_url)
        self.assertEqual(response.status_code, 200)
        print(response.json())

    def test_category_product_list(self):
        # Test success
        response = self.client.get(self.category1_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.data)
        print(response.json())

        # Test 404 for non-existent category
        response = self.client.get(self.nonexistent_category_url)
        self.assertEqual(response.status_code, 404)

    def test_wishlist_get(self):
        # Test success for authenticated user
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.wishlist_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("products", response.data["data"])
        print(response.json())

        # Test 401 for unauthenticated user
        self.client.force_authenticate(user=None)

        response = self.client.get(self.wishlist_url)
        self.assertEqual(response.status_code, 401)

    def test_add_to_wishlist(self):
        # Test success for authenticated user
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(self.add_to_wishlist_url)
        self.assertEqual(response.status_code, 200)
        print(response.json())

        # Verify product was added to wishlist
        wishlist = Wishlist.objects.get(profile=self.user1.profile)
        self.assertTrue(wishlist.products.filter(id=self.product3.id).exists())

        # Test 409 for product already in wishlist
        response = self.client.post(self.add_to_wishlist_url)
        self.assertEqual(response.status_code, 409)

        # Test 404 for non-existent product
        response = self.client.post(self.nonexistent_product_wishlist_url)
        self.assertEqual(response.status_code, 404)

        # Test 401 for unauthenticated user
        self.client.force_authenticate(user=None)

        response = self.client.post(self.add_to_wishlist_url)
        self.assertEqual(response.status_code, 401)

    def test_remove_product_from_wishlist(self):
        # Test success for authenticated user
        self.client.force_authenticate(user=self.user1)
        print(self.wishlist)
        
        response = self.client.delete(self.remove_from_wishlist_url)
        self.assertEqual(response.status_code, 200)
        print(response.json())
        
        # Verify product was removed from wishlist
        wishlist = Wishlist.objects.get(profile=self.user1.profile)
        self.assertFalse(wishlist.products.filter(id=self.product2.id).exists())
        
        # Test 404 for product not in wishlist
        response = self.client.delete(self.add_to_wishlist_url)
        self.assertEqual(response.status_code, 422)
        print(response.json())
        
        # Test 401 for unauthenticated user
        self.client.force_authenticate(user=None)
        
        response = self.client.delete(self.remove_from_wishlist_url)
        self.assertEqual(response.status_code, 401)


# python manage.py test apps.shop.tests.TestShop.test_product_list
