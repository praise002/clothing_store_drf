
from apps.profiles.models import ShippingAddress, ShippingFee


class TestProfileUtil:
    def shipping_address(profile1, profile2):
        ShippingFee.objects.create(state="Lagos", fee=5000)
        address1, _ = ShippingAddress.objects.get_or_create(
            user=profile1,
            phone_number="1234567890",
            state="Lagos",
            postal_code="100001",
            city="Lagos",
            street_address="123 Test Street",
            default=True,
        )
        
        address2, _ = ShippingAddress.objects.get_or_create(
            user=profile1,
            phone_number="0987654321",
            state="Abuja",
            postal_code="900001",
            city="Abuja",
            street_address="456 Sample Road",
            default=False,
        )
        
        address3, _ = ShippingAddress.objects.get_or_create(
            user=profile2,
            phone_number="5555555555",
            state="Rivers",
            postal_code="500001",
            city="Port Harcourt",
            street_address="789 Example Avenue",
            default=True,
        )
        
        return address1, address2, address3