from apps.accounts.models import User
from apps.profiles.models import Profile


class TestUtil:
    def new_user():
        user_dict = {
            "first_name": "Test",
            "last_name": "Name",
            "email": "test@example.com",
            "password": "Testpassword2008@",
        }
        user, _ = User.objects.get_or_create(**user_dict)
        return user

    def verified_user():
        user_dict = {
            "first_name": "Test",
            "last_name": "Verified",
            "email": "testverifieduser@example.com",
            "is_email_verified": True,
            "password": "Verified2001#",
        }
        user, _ = User.objects.get_or_create(**user_dict)
        return user

    def other_verified_user():
        user_dict = {
            "first_name": "Test",
            "last_name": "Otherisgood*5%",
            "email": "testotheruser@example.com",
            "is_email_verified": True,
            "password": "testpassword",
        }
        user, _ = User.objects.get_or_create(**user_dict)
        return user

    @staticmethod
    def delete_all_profiles():
        try:
            User.objects.all().delete()
        except Exception as e:
            print(f"Unexpected error occurred while deleting profiles: {e}")

    def get_profile(user):
        return Profile.objects.get(user=user)
