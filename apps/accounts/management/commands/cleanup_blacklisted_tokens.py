from django.core.management.base import BaseCommand
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

class Command(BaseCommand):
    help = "Deletes expired blacklisted tokens and outstanding tokens from the database."

    def handle(self, *args, **kwargs):
        # Delete expired outstanding tokens
        outstanding_deleted_count = OutstandingToken.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()

        # Delete expired blacklisted tokens
        blacklisted_deleted_count, _ = BlacklistedToken.objects.filter(
            token__expires_at__lt=timezone.now()
        ).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully deleted {outstanding_deleted_count} expired outstanding tokens "
                f"and {blacklisted_deleted_count} expired blacklisted tokens."
            )
        )