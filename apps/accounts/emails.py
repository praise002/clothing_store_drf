import random
import threading
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .models import Otp


def generate_otp(user):
    otp = random.randint(100000, 999999)
    # Save the OTP to the Otp model
    Otp.objects.create(user=user, otp=otp)
    return otp


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class SendEmail:

    @staticmethod
    def send_email(request, user):
        otp = generate_otp(user)
        subject = "Verify your email"
        email = user.email
        context = {
            "frontend_url": settings.FRONTEND_URL,
            "name": user.full_name,
            "email": email,
            "otp": otp,
        }
        message = render_to_string("verify_email_request.html", context)
        email_message = EmailMessage(subject=subject, body=message, to=[email])
        email_message.content_subtype = "html"
        EmailThread(email_message).start()

    @staticmethod
    def welcome(request, user):
        subject = "Account Verified"
        context = {
            "frontend_url": settings.FRONTEND_URL,
            "name": user.full_name,
        }
        message = render_to_string("welcome_message.html", context)
        email_message = EmailMessage(subject=subject, body=message, to=[user.email])
        email_message.content_subtype = "html"
        EmailThread(email_message).start()

    @staticmethod
    def send_password_reset_email(request, user):
        otp = generate_otp(user)
        subject = "Your Password Reset OTP"
        email = user.email
        context = {
            "frontend_url": settings.FRONTEND_URL,
            "name": user.full_name,
            "email": email,
            "otp": otp,
        }
        message = render_to_string("password_reset_email.html", context)
        email_message = EmailMessage(subject=subject, body=message, to=[email])
        email_message.content_subtype = "html"
        EmailThread(email_message).start()

    @staticmethod
    def password_reset_success(request, user):
        subject = "Password Reset Successful"
        context = {
            "frontend_url": settings.FRONTEND_URL,
            "name": user.full_name,
        }
        message = render_to_string("password_reset_success.html", context)
        email_message = EmailMessage(subject=subject, body=message, to=[user.email])
        email_message.content_subtype = "html"
        EmailThread(email_message).start()
