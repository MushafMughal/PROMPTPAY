from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


class CustomAPIException(APIException):
    def __init__(self, status, data, message, status_code):
        self.status_code = status_code
        self.detail = {  # ✅ This ensures Django treats it as a dictionary response
            "status": status,
            "data": data,
            "message": message
        }
    
    def __str__(self):
        return str(self.detail)  # ✅ Prevents Django from turning it into a string


def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))


# Alert generation to development team and reporting department
def send_email(to_email, subject, body):
    """Helper function to send an email."""

    # Common email credentials
    from_email = 'devteamxti@gmail.com'
    from_name = "PromptPay OTP System"
    password = "rssw yhtl mths kgpa"

    try:
        # SMTP server configuration
        host = "smtp.gmail.com"
        port = 587

        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach the body
        msg.attach(MIMEText(body, 'html'))

        # Connect to SMTP server
        with smtplib.SMTP(host, port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(from_email, password)
            smtp.sendmail(from_email, to_email, msg.as_string())

            return {"status": True, "message": "Email sent successfully"}
        
    except smtplib.SMTPException as e:
        return {"status": False, "message": "Failed to send email"}          
    except Exception as e:
        return {"status": False, "message": "Failed to send email: {e}"}

def send_user_registration_emails(to_email, otp):
    """Function to send user OTP emails to different recipients."""

    subject = "Your Secure OTP for PromptPay Banking System"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <p>Dear User,</p>
            <p>Your One-Time Password (OTP) is: <strong style="color: #d9534f; font-size: 18px;">{otp}</strong></p>
            <p>Please use this OTP to proceed with your process. This OTP is valid for <strong>5 minutes</strong>.</p>
            <p>If you did not request this OTP, please ignore this email.</p>
            <br>
            <p>Regards,<br><strong>PromptPay Banking System</strong></p>
            <hr>
            <p style="font-size: 12px; color: #888;">This is a system-generated email. Please do not reply.</p>
        </body>
    </html>
    """

    return send_email(to_email, subject, body)


