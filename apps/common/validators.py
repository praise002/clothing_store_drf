from django.forms import ValidationError
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


def validate_uuid(uuid_string):
    try:
        UUID(uuid_string)
        return True
    except ValueError:
        return False


def validate_file_size(file):
    """
    Validate file size for Cloudinary uploads
    Max size: 2MB (2097152 bytes)
    """
    max_size_mb = 2
    max_size_bytes = max_size_mb * 1024 * 1024

    logger.debug(f"Validating file size for file type: {type(file).__name__}")

    # Only validate if it's a file with size attribute (during upload)
    if hasattr(file, "size"):
        logger.info(f"File has size attribute. Size: {file.size} bytes")
        if file.size > max_size_bytes:
            logger.warning(f"File size ({file.size} bytes) exceeds limit of {max_size_bytes} bytes")
            raise ValidationError(f"File size cannot exceed {max_size_mb}MB")
        else:
            logger.info(f"File size validation passed: {file.size} bytes")
    else:
        # Don't validate CloudinaryResource objects (existing files)
        logger.info(f"File doesn't have size attribute, skipping validation. File type: {type(file).__name__}")
        return True
