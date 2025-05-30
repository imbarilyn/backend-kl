from email.message import EmailMessage
from email.utils import formataddr
import smtplib
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import BackgroundTasks

from app.routes.reset_pasword_email import frontend_url

PORT = 587


current_directory = Path(__file__).resolve().parent if '__file__' in locals()else Path.cwd()
env_directory = current_directory / '.env'

# load env variables
# load_dotenv(env_directory)
load_dotenv("/backend-kl/.env")

sender_email = os.getenv('SENDER_EMAIL')
password_email = os.getenv('EMAIL_PASSWORD')
smtp_server = os.getenv('SMTP_SERVER')
frontend_url = os.getenv('FRONTEND_URL')



def send_reset_password_mail(background_tasks: BackgroundTasks, receiver_mail, username, token):
    msg= EmailMessage()
    msg['Subject'] = 'Reset Password'
    msg['From'] = formataddr(('Password Reset', f'{sender_email}'))
    msg['To'] = receiver_mail
    msg.add_alternative(
        f"""\
        <htm>
            <body>
                <p>Hello,<p>
                <span>{username}</span>
                <p>Please click below to reset your password</p>
                <a href=f"{frontend_url}/auth/reset-password?token={token}">Reset Password</a>
            </body>
        </htm/>
""",
        subtype='html'
    )

    with smtplib.SMTP(smtp_server, PORT)as server:
        server.starttls()
        server.login(sender_email, password_email)
        server.sendmail(sender_email, receiver_mail, msg.as_string())

