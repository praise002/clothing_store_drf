import logging
import os
from pathlib import Path

from cloudinary_storage.storage import MediaCloudinaryStorage
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from apps.accounts.models import User
from apps.common.management.commands.data import TEAM_MEMBERS_DATA
from apps.general.models import TEAM_MEMBER_FOLDER, Message, Social, TeamMember
from apps.orders.models.order import Order
from apps.shop.models import Category, Product

logger = logging.getLogger(__name__)

CURRENT_DIR = Path(__file__).resolve().parent

test_images_directory = os.path.join(CURRENT_DIR, "images")


class CreateData:
    def __init__(self):
        with transaction.atomic():
            self.create_superuser()
            self.create_user_groups()
            self.create_team_members()

    def get_image(self, images_list, substring):
        return next((s for s in images_list if s.startswith(substring)), None)

    def create_superuser(self) -> User:
        user_dict = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": settings.SUPERUSER_EMAIL,
            "password": settings.SUPERUSER_PASSWORD,
            "is_email_verified": True,
        }
        superuser = User.objects.get_or_none(email=user_dict["email"])

        if not superuser:
            superuser = User.objects.create_superuser(**user_dict)

        return superuser

    def create_user_groups(self) -> Group:
        """Create user groups and assign permissions."""
        store_managers, created = Group.objects.get_or_create(name="Store Managers")
        if created:
            logger.info("Created 'Store Managers' group")

        content_editors, created = Group.objects.get_or_create(name="Content Editors")
        if created:
            logger.info("Created 'Content Editors' group")

        customer_support, created = Group.objects.get_or_create(name="Customer Support")
        if created:
            logger.info("Created 'Customer Support' group")

        # Assign permissions to Store Managers
        product_content_type = ContentType.objects.get_for_model(Product)
        # print(product_content_type)  # returns Shop | product
        category_content_type = ContentType.objects.get_for_model(Category)

        # Get all permissions for Product and Category models
        product_permissions = Permission.objects.filter(
            content_type=product_content_type
        )
        # returns <QuerySet [<Permission: Shop | product | Can add product>, <Permission: Shop | product | Can change product>, <Permission: Shop | product | Can delete product>, <Permission: Shop | product | Can view product>]>
        # print(product_permissions)
        category_permissions = Permission.objects.filter(
            content_type=category_content_type
        )

        # Add permissions to Store Managers
        store_managers.permissions.add(*product_permissions)
        store_managers.permissions.add(*category_permissions)

        # Assign permissions to Content Editors
        # Allow them to view and change products but not delete
        content_editors.permissions.add(
            *Permission.objects.filter(
                content_type=product_content_type,
                codename__in=["view_product", "change_product"],
            )
        )

        # Customer Support can view orders and messages but not modify them
        order_content_type = ContentType.objects.get_for_model(Order)
        message_content_type = ContentType.objects.get_for_model(Message)

        order_permissions = Permission.objects.filter(
            content_type=order_content_type, codename="view_order"
        )
        message_permissions = Permission.objects.filter(
            content_type=message_content_type, codename="view_message"
        )
        customer_support.permissions.add(*order_permissions)
        customer_support.permissions.add(*message_permissions)

        # Create test users and assign to groups
        if not User.objects.filter(email="manager@example.com").exists():
            manager = User.objects.create_user(
                first_name="Store",
                last_name="Manager",
                email=settings.STORE_MANAGER_EMAIL,
                password=settings.STORE_MANAGER_PASSWORD,
                is_staff=True,
                is_email_verified=True,
            )
            manager.groups.add(store_managers)
            logger.info(
                f"Created user 'Store Manager' and added to 'Store Managers' group"
            )

        if not User.objects.filter(email="editor@example.com").exists():
            editor = User.objects.create_user(
                first_name="Content",
                last_name="Editor",
                email=settings.CONTENT_EDITOR_EMAIL,
                password=settings.CONTENT_EDITOR_PASSWORD,
                is_staff=True,
                is_email_verified=True,
            )
            editor.groups.add(content_editors)
            logger.info(
                f"Created user 'Content Editor' and added to 'Content Editors' group"
            )

        if not User.objects.filter(email="support@example.com").exists():
            support = User.objects.create_user(
                first_name="Customer",
                last_name="Support",
                email=settings.CUSTOMER_SUPPORT_EMAIL,
                password=settings.CUSTOMER_SUPPORT_PASSWORD,
                is_staff=True,
                is_email_verified=True,
            )
            support.groups.add(customer_support)
            logger.info(
                f"Created user 'Customer Support' and added to 'Customer Support' group"
            )

    def create_team_members(self) -> TeamMember:
        created_count = 0
        skipped_count = 0
        team_members_to_create = []

        for member_data in TEAM_MEMBERS_DATA:
            # Check if a team member with this name already exists
            if TeamMember.objects.filter(name=member_data["name"]).exists():
                logger.debug(
                    f"Team member '{member_data['name']}' already exists. Skipping."
                )
                skipped_count += 1
                continue

            try:

                # Create the social links first
                social_data = member_data.pop("social")
                social = Social.objects.create(**social_data)

                images = os.listdir(test_images_directory)
                # FIXME
                image_file_name = self.get_image(images, "team")
                image_path = os.path.join(test_images_directory, image_file_name)

                with open(image_path, "rb") as image_file:
                    file_storage = MediaCloudinaryStorage()
                    file_path = file_storage.save(
                        f"{TEAM_MEMBER_FOLDER}{image_file_name}", image_file
                    )
                    team_member = TeamMember(
                        name=member_data["name"],
                        role=member_data["role"],
                        description=member_data["description"],
                        social_links=social,
                        avatar=file_path,
                    )
                    team_members_to_create.append(team_member)
                    created_count += 1
                    logger.debug(f"Created team member: {team_member.name}")

            except Exception as e:
                logger.error(
                    f"Error creating team member '{member_data['name']}': {str(e)}"
                )

        if team_members_to_create:
            try:
                team_members = TeamMember.objects.bulk_create(team_members_to_create)
                logger.info(
                    f"Successfully created {created_count} team members, skipped {skipped_count}."
                )

                return team_members
            except Exception as e:
                logger.error(f"Error during bulk creation: {str(e)}")

        return []
