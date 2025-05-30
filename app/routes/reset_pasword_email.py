import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path

import pymysql
from dotenv import load_dotenv

current_dir = Path(__file__).resolve().parent if __file__ in locals() else Path.cwd()
env_directory = current_dir / '.env'
load_dotenv(env_directory)

email_password =  os.getenv('EMAIL_PASSWORD')
sender_email = os.getenv('SENDER_EMAIL')
smtp_server = os.getenv('SMTP_SERVER')
frontend_url = os.getenv('FRONTEND_URL')
port = 587

def send_reset_email(user_name, user_email: str, reset_token: str, db: pymysql.connections.Connection):
    day_of_week = datetime.now().strftime('%A')
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Password Reset'
        msg['From'] = formataddr(('Password reset', f'{sender_email}'))
        msg['To'] = user_email

        msg.add_alternative(
            f"""
            <html>
                <body>
                    <p>Hello <strong>{user_name}</strong>,</p>
                    <br>
                    <p>I hope your {day_of_week} is going on well.</p> 
                    <p>We received a request to reset your password. Please click the link below to reset your password:</p>
                    <a href="{frontend_url}/auth/reset-password/{reset_token}">Reset Password</a>
                    <p>Thank you.</p>
                    <br>                    
                     <p>Best Regards,</p>
                     <p>Vulavutech Group</p>
                     
                     <p>&copy; 2025 Vulavutech Group | Need help? <a href="mailto:linahmuhonjaimbari@gmail.com">Contact Support</a></p>
                </body>
            </html>
            """,
            subtype='html'
        )
        with smtplib.SMTP(smtp_server, port) as server:
            server.connect(smtp_server, port)
            server.starttls()
            server.login(sender_email, email_password)
            server.sendmail(sender_email, user_email, msg.as_string())
            server.quit()
            return True
    except Exception as e:
        print(f'Error sending email {e}')
        return False