from rest_framework.test import APITestCase


class TestGeneral(APITestCase):
    site_detail_url = "/api/v1/site-detail/"
    teams_url = "/api/v1/teams/"
    contact_url = "/api/v1/contact/"

    def test_site_detail(self):
        # Test successful retrieval of site detail
        response = self.client.get(self.site_detail_url)
        print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_team_member_list(self):
        # Test successful retrieval of team members
        response = self.client.get(self.teams_url)
        print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_message_create(self):
        # Test successful creation
        valid_data = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "This is a test subject",
            "text": "This is a test message",
        }
        response = self.client.post(self.contact_url, valid_data)
        self.assertEqual(response.status_code, 201)

        # Test 422 response for missing required field
        invalid_data = {"name": "Test User", "email": "test@example.com"}
        response = self.client.post(self.contact_url, invalid_data)
        self.assertEqual(response.status_code, 422)

        # Test 422 response for invalid email format
        invalid_email_data = {
            "name": "Test User",
            "email": "not-an-email",
            "subject": "This is a test subject",
            "text": "This is a test message",
        }
        response = self.client.post(self.contact_url, invalid_email_data)
        self.assertEqual(response.status_code, 422)

# python manage.py test apps.general.tests.TestGeneral.test_message_create