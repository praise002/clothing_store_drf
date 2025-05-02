from django.core.files.base import ContentFile
from celery import shared_task
import requests, logging, uuid

from apps.accounts.models import User
from apps.profiles.models import Profile


logger = logging.getLogger(__name__)


@shared_task
def download_and_upload_avatar(url: str, user_id: str):
    """
    Download Google profile picture and upload to Cloudinary

    Args:
        url (str): Google profile picture URL
        user_id (str): UUID of the user
    """
    extension_map = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
    try:
        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)
        response = requests.get(url)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        print(f"Content Type: {content_type}")
        ext = extension_map.get(content_type, ".jpg")
        image_name = f"{user.full_name}_{uuid.uuid4()}{ext}"
        print(f"Image name: {image_name}")
        image_content = ContentFile(response.content, name=image_name)
        print(f"Image content: {image_content}")
        
        profile.avatar = image_content
        profile.save(update_fields=["avatar"])
        logger.info(f"Successfully uploaded profile picture for user {user.full_name}")
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
        raise
    except requests.RequestException as e:
        logger.error(f"Error downloading image: {e}")
        raise
