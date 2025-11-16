from django.core.management.base import BaseCommand
from apps.common.management.commands.data_script import CreateData


def init():
    CreateData()


class Command(BaseCommand):
    help = "Populate the database with fake data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating initial data...")
        init()
        self.stdout.write(self.style.SUCCESS("Initial data created"))
