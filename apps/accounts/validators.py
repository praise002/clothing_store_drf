from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()-+]).{8,}$', password):
            raise ValidationError(
                _("This password must contain at least 8 characters, one uppercase letter, one lowercase letter, one digit and one symbol.")
            )
        
    def get_help_text(self):
        return _(
            "Your password must contain at least 8 characters, one uppercase letter, one lowercase letter, one digit and one symbol."
        )