import uuid
from rest_framework.test import APITestCase

from django.core.files.uploadedfile import SimpleUploadedFile


from apps.common.utils import TestUtil
from apps.profiles.models import Profile, ShippingAddress


class TestProfiles(APITestCase):
    profile_url = "/api/v1/profile/"
    avatar_update_url = "/api/v1/profile/avatar/"
    shipping_address_create_url = "/api/v1/shipping-addresses/add/"
    shipping_address_list_url = "/api/v1/shipping-addresses/"

    def setUp(self):
        self.user1 = TestUtil.verified_user()
        self.user2 = TestUtil.other_verified_user()

        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile2 = Profile.objects.get(user=self.user2)

        self.address1 = ShippingAddress.objects.create(
            user=self.profile1,
            phone_number="1234567890",
            state="Lagos",
            postal_code="100001",
            city="Lagos",
            street_address="123 Test Street",
            default=True,
        )

        self.address2 = ShippingAddress.objects.create(
            user=self.profile1,
            phone_number="0987654321",
            state="Abuja",
            postal_code="900001",
            city="Abuja",
            street_address="456 Sample Road",
            default=False,
        )

        self.address3 = ShippingAddress.objects.create(
            user=self.profile2,
            phone_number="5555555555",
            state="Rivers",
            postal_code="500001",
            city="Port Harcourt",
            street_address="789 Example Avenue",
            default=True,
        )

        # Create shipping address detail URL with ID
        self.shipping_address_detail_url = (
            f"/api/v1/shipping-addresses/{self.address1.id}/"
        )
        self.shipping_address_other_user_url = (
            f"/api/v1/shipping-addresses/{self.address3.id}/"
        )
        self.non_existent_address_url = f"/api/v1/shipping-addresses/{uuid.uuid4()}/"

    def test_shipping_address_create(self):
        # Test 201 for authenticated users
        self.client.force_authenticate(user=self.user1)

        valid_data = {
            "phone_number": "8011111111",
            "state": "Ondo",
            "postal_code": "100001",
            "city": "Ondo",
            "street_address": "789 New Address",
            "default": True,
        }

        response = self.client.post(self.shipping_address_create_url, valid_data)
        print(response.data)
        self.assertEqual(response.status_code, 201)

        # get all the shipping address to check the default changes for the previous one
        response = self.client.get(self.shipping_address_list_url)
        print(response.data)

        # Test invalid state choice (422)
        invalid_data = valid_data.copy()
        invalid_data["state"] = "InvalidState"

        response = self.client.post(self.shipping_address_create_url, invalid_data)
        print(response.data)
        self.assertEqual(response.status_code, 422)

        # Test 422(missing field)
        invalid_data = {
            "phone_number": "8011111111",
            "state": "Lagos",
            "postal_code": "100001",
        }
        response = self.client.post(self.shipping_address_create_url, invalid_data)
        print(response.data)
        self.assertEqual(response.status_code, 422)

        # test 401
        self.client.force_authenticate(user=None)

        response = self.client.post(self.shipping_address_create_url, valid_data)
        self.assertEqual(response.status_code, 401)

    def test_shipping_address_list(self):
        # Test 200 for authenticated users
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.shipping_address_list_url)
        self.assertEqual(response.status_code, 200)
        print(response.data)

        # User1 should have 2 addresses
        self.assertEqual(len(response.data["data"]), 2)

        # Test different user sees their own addresses
        self.client.force_authenticate(user=self.user2)

        response = self.client.get(self.shipping_address_list_url)
        self.assertEqual(response.status_code, 200)

        # User2 should have 1 address
        self.assertEqual(len(response.data["data"]), 1)

        # Test 401 for unauthenticated users
        self.client.force_authenticate(user=None)

        response = self.client.get(self.shipping_address_list_url)
        self.assertEqual(response.status_code, 401)

    def test_shipping_address_detail_get(self):
        # Test 200 for authenticated users
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.shipping_address_detail_url)
        self.assertEqual(response.status_code, 200)
        print(response.data)
        self.assertEqual(response.data["data"]["id"], str(self.address1.id))

        # Test you can only retrieve your shipping address
        response = self.client.get(self.shipping_address_other_user_url)
        print(response.data)
        self.assertEqual(response.status_code, 404)

        self.client.force_authenticate(user=None)

        response = self.client.get(self.shipping_address_detail_url)
        self.assertEqual(response.status_code, 401)

        # Test 404 for non-existent address
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.non_existent_address_url)
        self.assertEqual(response.status_code, 404)
        print(response.data)

    def test_shipping_address_detail_patch(self):
        # Test 200 for authenticated users
        self.client.force_authenticate(user=self.user1)

        update_data = {
            "city": "Updated City",
            "street_address": "Updated Street Address",
        }

        response = self.client.patch(self.shipping_address_detail_url, update_data)
        self.assertEqual(response.status_code, 200)
        print(response.data)

        # Verify the update
        self.address1.refresh_from_db()
        self.assertEqual(self.address1.city, "Updated City")
        self.assertEqual(self.address1.street_address, "Updated Street Address")

        # Test update of non-default to default
        update_data = {
            "default": True,
        }
        response = self.client.patch(
            f"/api/v1/shipping-addresses/{self.address2.id}/", update_data
        )
        self.assertEqual(response.status_code, 200)
        print(response.data)

        # get all the shipping address to check the default changes for the previous one
        response = self.client.get(self.shipping_address_list_url)
        print(response.data)

        # Test you can only update your shipping address
        response = self.client.patch(self.shipping_address_other_user_url, update_data)
        self.assertEqual(response.status_code, 404)
        print(response.data)

        # Test 401 for unauthenticated users
        self.client.force_authenticate(user=None)

        response = self.client.patch(self.shipping_address_detail_url, update_data)
        self.assertEqual(response.status_code, 401)

        # Test 404 for non-existent address
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(self.non_existent_address_url, update_data)
        self.assertEqual(response.status_code, 404)
        print(response.data)

    def test_shipping_address_detail_delete(self):
        # Test 204 for authenticated users (non-default address)
        self.client.force_authenticate(user=self.user1)

        # Delete non-default address should succeed
        non_default_url = f"/api/v1/shipping-addresses/{self.address2.id}/"
        response = self.client.delete(non_default_url)
        self.assertEqual(response.status_code, 204)

        # Test 403 for deleting default shipping address
        response = self.client.delete(
            self.shipping_address_detail_url
        )  # This is the default address
        print(self.shipping_address_detail_url)
        print(self.address1)
        self.assertEqual(response.status_code, 403)
        print(response.data)

        # Test you can only delete your shipping address
        response = self.client.delete(self.shipping_address_other_user_url)
        self.assertEqual(response.status_code, 404)
        print(response.data)

        # Test 401 for unauthenticated users
        self.client.force_authenticate(user=None)

        response = self.client.delete(non_default_url)
        self.assertEqual(response.status_code, 401)
        print(response.data)

        # Test 404 for non-existent address
        self.client.force_authenticate(user=self.user1)

        response = self.client.delete(self.non_existent_address_url)
        self.assertEqual(response.status_code, 404)
        print(response.data)

    def test_profile(self):
        # Test successful retrieval for authenticated users
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        print(response.data)
        profile1 = Profile.objects.get(user=response.data["data"]["user"]["id"])
        self.assertEqual(str(profile1.id), str(self.profile1.id))

        # Test you can only retrieve your own profile
        # Switch to user2 and verify they get their own profile
        self.client.force_authenticate(user=self.user2)

        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        print(response.data)
        profile2 = Profile.objects.get(user=response.data["data"]["user"]["id"])
        self.assertEqual(str(profile2.id), str(self.profile2.id))

        # Test 401 for unauthorized user
        self.client.force_authenticate(user=None)

        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 401)

    def test_avatar_update(self):
        # Test success
        self.client.force_authenticate(user=self.user1)

        image_content = b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
        image = SimpleUploadedFile(
            "test_image.gif", image_content, content_type="image/gif"
        )

        response = self.client.patch(
            self.avatar_update_url, {"avatar": image}, format="multipart"
        )

        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.profile1.refresh_from_db()
        self.assertTrue(self.profile1.avatar)

        # Test 401 for unauthenticated users
        self.client.force_authenticate(user=None)

        response = self.client.patch(
            self.avatar_update_url, {"avatar": image}, format="multipart"
        )
        print(response.data)

        self.assertEqual(response.status_code, 401)


# python manage.py test apps.profiles.tests.TestProfiles.test_shipping_address_create
