import random
import threading
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .models import Otp  

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

class OTPService:
    @staticmethod
    def generate_otp():
        """Generates a 6-digit OTP"""
        return random.randint(100000, 999999)
        
    @staticmethod
    def store_otp(user, otp):
        """Stores the OTP in the database"""
        otp = Otp.objects.create(user=user, otp=otp)
        return otp

    @staticmethod
    def send_otp_email(request, user):
        """Sends OTP email to the user"""
        domain = f"{request.scheme}://{request.get_host()}" # http www.example.com
        subject = "Your OTP Verification Code"
        otp = OTPService.store_otp(user, OTPService.generate_otp())
        context = {
            "domain": domain,
            "name": user.full_name,
            "otp": otp,
        }
        message = render_to_string("accounts/emails/email_verification_code.html", context)
        email_message = EmailMessage(subject=subject, body=message, to=[user.email])
        email_message.content_subtype = "html"
        EmailThread(email_message).start()
        
    @staticmethod
    def welcome(request, user):
        domain = f"{request.scheme}://{request.get_host()}"  
        subject = "Account Verified"
        context = {
            "domain": domain,
            "name": user.full_name,
        }
        message = render_to_string("accounts/emails/welcome_message.html", context)
        email_message = EmailMessage(subject=subject, body=message, to=[user.email])
        email_message.content_subtype = "html"
        EmailThread(email_message).start()
        
    @staticmethod
    def send_password_reset_otp(request, user):
        domain = f"{request.scheme}://{request.get_host()}"  # http www.example.com
        otp = OTPService.store_otp(user, OTPService.generate_otp())
        subject = "Your Password Reset OTP"
        email = user.email
        context = {
            "domain": domain,
            "name": user.full_name,
            "email": email,
            "otp": otp,
        }
        message = render_to_string("accounts/emails/password_reset_html_email.html", context)
        email_message = EmailMessage(subject=subject, body=message, to=[email])
        email_message.content_subtype = "html"
        EmailThread(email_message).start()

    @staticmethod
    def password_reset_success(request, user):
        domain = f"{request.scheme}://{request.get_host()}"
        subject = "Password Reset Successful"
        context = {
            "domain": domain,
            "name": user.full_name,
        }
        message = render_to_string("accounts/password_reset_success.html", context)
        email_message = EmailMessage(subject=subject, body=message, to=[user.email])
        email_message.content_subtype = "html"
        EmailThread(email_message).start()




