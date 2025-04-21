from rest_framework.test import APITestCase
from apps.common.utils import TestUtil
from apps.accounts.models import Otp
from unittest import mock
from datetime import timedelta
from django.utils import timezone


valid_data = {
    "first_name": "Test",
    "last_name": "User",
    "email": "testuser@example.com",
    "password": "Strong_password124$",
}

invalid_data = {
    "first_name": "",
    "last_name": "User",
    "email": "invalid_email",
    "password": "short",
}


class TestAccounts(APITestCase):
    register_url = "/api/v1/auth/register/"
    login_url = "/api/v1/auth/token/"
    token_refresh_url = "/api/v1/auth/token/refresh/"
    logout_url = "/api/v1/auth/logout/"
    logout_all_url = "/api/v1/auth/logout/all/"

    send_email_url = "/api/v1/auth/otp/"
    verify_email_url = "/api/v1/auth/otp/verify/"

    password_change_url = "/api/v1/auth/password-change/"
    password_reset_request_url = "/api/v1/auth/password-reset/otp/"
    password_reset_verify_otp_url = "/api/v1/auth/password-reset/otp/verify/"
    password_reset_done_url = "/api/v1/auth/password-reset/done/"

    def setUp(self):
        self.new_user = TestUtil.new_user()
        self.verified_user = TestUtil.verified_user()

    def test_register(self):
        mock.patch("apps.accounts.emails.SendEmail", new="")

        # Valid Registration
        response = self.client.post(self.register_url, valid_data)
        print(response.json())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "OTP sent for email verification.",
                "data": {"email": valid_data["email"]},
            },
        )

        # Invalid Registration - 422
        response = self.client.post(self.register_url, invalid_data)
        print(response.json())
        self.assertEqual(response.status_code, 422)

    def test_login(self):
        # Valid Login
        print(self.verified_user)
        response = self.client.post(
            self.login_url,
            {
                "email": self.verified_user.email,
                "password": "Verified2001#",
            },
        )
        print(response.json())

        self.assertEqual(response.status_code, 200)

        # Invalid Login - Incorrect Password
        response = self.client.post(
            self.login_url,
            {
                "email": self.verified_user.email,
                "password": "wrongpassword",
            },
        )
        print(response.json())
        self.assertEqual(response.status_code, 401)

        # Invalid Login - empty Password
        response = self.client.post(
            self.login_url,
            {
                "email": self.verified_user.email,
                "password": "",
            },
        )
        print(response.json())
        self.assertEqual(response.status_code, 422)

        # invalid login - email not verified
        response = self.client.post(
            self.login_url,
            {
                "email": self.new_user.email,
                "password": "Testpassword2008@",
            },
        )
        print(response.json())
        self.assertEqual(response.status_code, 403)

    def test_resend_verification_email(self):
        mock.patch("apps.accounts.emails.SendEmail", new="")

        # OTP Sent for Existing User
        response = self.client.post(self.send_email_url, {"email": self.new_user.email})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "OTP sent successfully.",
            },
        )

        # Non-existent User
        response = self.client.post(self.send_email_url, {"email": "user@gmail.com"})
        self.assertEqual(response.status_code, 400)
        print(response.json())
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "message": "No account is associated with this email.",
                "code": "bad_request",
            },
        )

        # Invalid email
        response = self.client.post(self.send_email_url, {"email": "user"})
        print(response.json())
        self.assertEqual(response.status_code, 422)

        # email already verified
        response = self.client.post(
            self.send_email_url, {"email": self.verified_user.email}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "Your email is already verified. No OTP sent.",
            },
        )

    def test_verify_email(self):
        new_user = self.new_user
        otp = "111111"
        mock.patch("apps.accounts.emails.SendEmail", new="")

        # Invalid OTP
        response = self.client.post(
            self.verify_email_url, {"email": new_user.email, "otp": "hgtr"}
        )
        self.assertEqual(response.status_code, 422)

        # OTP does not exist
        response = self.client.post(
            self.verify_email_url, {"email": new_user.email, "otp": int(otp)}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "message": "Invalid OTP provided.",
                "code": "bad_request",
            },
        )

        # Valid OTP Verification
        otp = Otp.objects.create(user_id=new_user.id, otp=int(otp))
        response = self.client.post(
            self.verify_email_url,
            {"email": new_user.email, "otp": otp.otp},
        )
        self.assertEqual(response.status_code, 200)

        # Clear OTP After Verification
        otp_cleared = not Otp.objects.filter(user_id=new_user.id).exists()

        self.assertTrue(otp_cleared, "OTP should be cleared after verification.")
        self.assertEqual(
            response.json(),
            {"status": "success", "message": "Email verified successfully."},
        )

        # Expired OTP
        otp = Otp.objects.create(
            user_id=self.new_user.id,
            otp=int("876547"),
            created_at="2023-10-01T12:00:00Z",
        )
        response = self.client.post(
            self.verify_email_url,
            {"email": new_user.email, "otp": otp.otp},
        )
        self.assertEqual(response.status_code, 498)
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "message": "OTP has expired, please request a new one.",
                "code": "expired",
            },
        )

        # Already Verified User
        otp = Otp.objects.create(user_id=self.verified_user.id, otp=int("876547"))
        response = self.client.post(
            self.verify_email_url,
            {"email": self.verified_user.email, "otp": otp.otp},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "Email address already verified. No OTP sent.",
            },
        )

    def test_logout(self):
        # Successful Logout
        verified_user = self.verified_user
        login_response = self.client.post(
            self.login_url,
            {
                "email": verified_user.email,
                "password": "Verified2001#",
            },
        )

        # Check login response and extract access token
        self.assertEqual(login_response.status_code, 200)
        refresh_token = login_response.json().get("data").get("refresh")
        print(login_response.json())
        self.assertIsNotNone(
            refresh_token, "Refresh token should be provided upon login"
        )

        # Successful Logout using the refresh token
        response = self.client.post(
            self.logout_url,
            {
                "refresh": refresh_token,
            },
        )
        print(response.json())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "success", "message": "Logged out successfully."},
        )

        # Invalid Refresh Token
        response = self.client.post(
            self.logout_url,
            {
                "refresh": f"{refresh_token}_invalid_refresh_token",
            },
        )
        print(response.json())

        self.assertEqual(response.status_code, 401)

        # Missing Refresh Token
        response = self.client.post(
            self.logout_url,
            {
                "refresh": "",
            },
        )
        print(response.json())

        self.assertEqual(response.status_code, 422)

    def test_logout_all(self):
        # Test unauthorized access
        unauthorized_response = self.client.post(self.logout_all_url)
        print(unauthorized_response.json())
        print(unauthorized_response.status_code)
        self.assertEqual(unauthorized_response.status_code, 401)

        # First login to get tokens
        login_response = self.client.post(
            self.login_url,
            {
                "email": self.verified_user.email,
                "password": "Verified2001#",
            },
        )

        self.assertEqual(login_response.status_code, 200)
        access_token = login_response.json()["data"]["access"]

        # Set authorization header for authenticated request
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Make logout all request
        response = self.client.post(self.logout_all_url)
        print(response.json())

        # Assert response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "Successfully logged out from all devices.",
            },
        )

        # Verify tokens are blacklisted by trying to use them
        refresh_token = login_response.json()["data"]["refresh"]
        refresh_response = self.client.post(
            self.token_refresh_url, {"refresh": refresh_token}
        )
        print(refresh_response.json())
        self.assertEqual(refresh_response.status_code, 401)

    def test_password_change(self):
        verified_user = self.verified_user

        # Unauthenticated trying to change password
        response = self.client.post(
            self.password_change_url,
            {"old_password": verified_user.password, "new_password": "Verified2001#"},
        )
        self.assertEqual(response.status_code, 401)

        # Valid Password Change
        # login the user
        login_response = self.client.post(
            self.login_url,
            {"email": verified_user.email, "password": "Verified2001#"},
        )

        # print(login_response.json())
        access_token = login_response.json().get("data").get("access")
        bearer_headers = {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}
        response = self.client.post(
            self.password_change_url,
            {
                "old_password": "Verified2001#",
                "new_password": "Testimony74&",
                "confirm_password": "Testimony74&",
            },
            **bearer_headers,
        )
        print(response.json())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "success", "message": "Password changed successfully."},
        )

        # Incorrect Current Password
        response = self.client.post(
            self.password_change_url,
            {
                "old_password": "testpass",
                "confirm_password": "testimony74",
                "new_password": "testimony74",
            },
            **bearer_headers,
        )
        print(response.json())
        print(response.status_code)

        self.assertEqual(response.status_code, 422)

        # Weak New Password
        response = self.client.post(
            self.password_change_url,
            {
                "old_password": "Verified2001#",
                "confirm_password": "test",
                "new_password": "test",
            },
            **bearer_headers,
        )
        print(response.json())

        self.assertEqual(response.status_code, 422)

    def test_password_reset_request(self):
        verified_user = self.verified_user
        mock.patch("apps.accounts.emails.SendEmail", new="")

        # Send OTP to Registered Email
        response = self.client.post(
            self.password_reset_request_url, {"email": verified_user.email}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"status": "success", "message": "OTP sent successfully."}
        )

        # Non-existent Email
        response = self.client.post(
            self.password_reset_request_url, {"email": "tom@gmail.com"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "message": "User with this email does not exist.",
                "code": "bad_request",
            },
        )

    def test_verify_otp(self):
        verified_user = self.verified_user
        otp = "123456"
        otp_obj = Otp.objects.create(user=verified_user, otp=otp)

        # user does not exist
        response = self.client.post(
            self.password_reset_verify_otp_url,
            {"email": "nonexistentuser@example.com", "otp": int(otp)},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "message": "No account is associated with this email.",
                "code": "bad_request",
            },
        )

        # Otp does not exist
        response = self.client.post(
            self.password_reset_verify_otp_url,
            {"email": verified_user.email, "otp": int("123457")},
        )
        self.assertEqual(response.status_code, 400)
        print(response.json())
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "message": "The OTP could not be found. Please enter a valid OTP or request a new one.",
                "code": "bad_request",
            },
        )

        # otp is expired
        otp_obj.created_at = timezone.now() - timedelta(hours=2)
        otp_obj.save()
        response = self.client.post(
            self.password_reset_verify_otp_url,
            {"email": verified_user.email, "otp": int(otp)},
        )
        print(response.json())
        self.assertEqual(response.status_code, 498)
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "message": "OTP has expired, please request a new one.",
                "code": "expired",
            },
        )

        # otp exists
        otp_obj.created_at = timezone.now()  # Resetting OTP's timestamp to be valid
        otp_obj.save()
        response = self.client.post(
            self.password_reset_verify_otp_url,
            {"email": verified_user.email, "otp": int(otp)},
        )
        self.assertEqual(response.status_code, 200)
        # otp is cleared after verification
        otp_cleared = not Otp.objects.filter(user_id=verified_user.id).exists()
        self.assertTrue(otp_cleared, "OTP should be cleared after password reset.")
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "OTP verified, proceed to set a new password.",
            },
        )

        # otp is a letter or less than min or greater than min value
        response = self.client.post(
            self.password_reset_verify_otp_url,
            {"email": verified_user.email, "otp": "abc123"},
        )
        self.assertEqual(response.status_code, 422)

        response = self.client.post(
            self.password_reset_verify_otp_url,
            {"email": verified_user.email, "otp": int("123456789")},
        )
        self.assertEqual(response.status_code, 422)

    def test_password_reset_done(self):
        verified_user = self.verified_user

        # user does not exist
        response = self.client.post(
            self.password_reset_done_url,
            {
                "email": "nonexistentuser@example.com",
                "new_password": "NewPassword123$",
                "confirm_password": "NewPassword123$",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "message": "No account is associated with this email.",
                "code": "bad_request",
            },
        )

        # Successful Password Reset
        response = self.client.post(
            self.password_reset_done_url,
            {
                "email": verified_user.email,
                "new_password": "NewPassword123#",
                "confirm_password": "NewPassword123#",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "Your password has been reset, proceed to login.",
            },
        )

        # Weak New Password
        response = self.client.post(
            self.password_reset_done_url,
            {"email": verified_user.email, "new_password": "weak"},
        )
        print(response.json())
        self.assertEqual(response.status_code, 422)


# python manage.py test apps.accounts.tests.TestAccounts.test_register
