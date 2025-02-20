from django.forms import ValidationError
from cloudinary.models import CloudinaryResource
from uuid import UUID


def validate_uuid(uuid_string):
    try:
        UUID(uuid_string)
        return True
    except ValueError:
        return False


# def validate_file_size(file):
#     max_size_kb = 90

#     if file.size > max_size_kb * 1024:
#         raise ValidationError(f"Files cannot be larger than {max_size_kb}KB!")


def validate_file_size(file):
    """
    Validate file size for Cloudinary uploads
    Max size: 2MB (2097152 bytes)
    """
    max_size_mb = 2
    max_size_bytes = max_size_mb * 1024 * 1024

    if hasattr(file, "size"):
        # Regular file upload
        if file.size > max_size_bytes:
            raise ValidationError(f"File size cannot exceed {max_size_mb}MB")
    elif isinstance(file, CloudinaryResource):
        # Cloudinary file
        if hasattr(file, "metadata"):
            file_size = file.metadata.get("bytes", 0)
            if file_size > max_size_bytes:
                raise ValidationError(f"File size cannot exceed {max_size_mb}MB")
    else:
        # If we can't determine size, assume it's valid
        # You might want to modify this behavior based on your requirements
        pass

# TODO: FIX LATER