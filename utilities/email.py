from fastapi import HTTPException
from ..config import settings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ..config import settings
from itsdangerous import URLSafeTimedSerializer



serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


SMTP_SERVER = settings.SMTP_SERVER
SMTP_PORT = settings.SMTP_PORT
SMTP_USER = settings.SMTP_USER
SMTP_PASSWORD = settings.SMTP_PASSWORD
SECRET_KEY = settings.SECRET_KEY
FROM_EMAIL = settings.FROM_EMAIL

# Function to send email using smtp
def send_verification_email(to_email: str, body):

    
    
    subject = "Please verify your email"


    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Establish SMTP connection
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Start TLS encryption
        server.login(SMTP_USER, SMTP_PASSWORD)  # Log in to the SMTP server

        # Send the email
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        server.quit()

        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="Error sending verification email")