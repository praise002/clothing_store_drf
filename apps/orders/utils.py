def generate_tracking_number():
    """
    Generate a unique tracking number in the format: NGYYYYMMDDXXXXXX
    """
    from django.utils.timezone import now
    import uuid

    timestamp = now().strftime("%Y%m%d")  # Current date in YYYYMMDD format
    random_uuid = uuid.uuid4().hex[:6].upper()
    tracking_number = f"NG{timestamp}{random_uuid}"
    return tracking_number
