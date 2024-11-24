import os
import smtplib
from pathlib import Path
from dotenv import load_dotenv
from email.message import EmailMessage
from email.utils import formataddr

# Email server details


PORT = 587
SMTP_SERVER = 'smtp.gmail.com'

# Trying to get the current directory to load the environment variables
# The script below works for both file-based or interactive python sessions like REPL
current_dir = Path(__file__).resolve().parent if '__file__' in locals() else Path.cwd()
env_directory = current_dir / '.env'

# Now let's load the environment variables to get the email credentials
# we pass the absolute path to the .env file to the load_dotenv function
load_dotenv(env_directory)

# Now we have all the environment variables
sender_email = os.getenv('SENDER_EMAIL')
password_email = os.getenv('EMAIL_PASSWORD')
receiver = os.getenv('RECEIVER_EMAIL')

print(f'email-address: {sender_email} password: {password_email}')


# Now writing the function for sending emails
def send_email_expired_contract(subject, receiver_email, expiry_date, contract_name, vendor_name):
    # initialize the EmailMessage object
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = formataddr(('Contract Expiry Notification', f'{sender_email}'))
    msg['To'] = receiver_email

    # msg.set_content(
    #     f"""\
    #     Hello,
    #     I hope you are well.
    #     This is to inform you that the contract for {contract_name} with {vendor_name} will expire on {expiry_date}.
    #     Please take the necessary steps to renew the contract.
    #     Thank you.
    #     """
    # )

    msg.add_alternative(
        f"""\
        <html>
            <body>
                <p>Hello,</p>
                
                <p>I hope you are well.</p>
                <p>This is to inform you that the contract for <strong>{contract_name}</strong> with <strong>{vendor_name}</strong> will expire on <strong>{expiry_date}</strong>.</p>
                <p>Please take the necessary steps to renew the contract.</p>
            
                <p>Thank you.</p>
                <p>Best Regards,</p>
                <p>Contract Management System</p>
                <p><strong>Vulavu Tech</strong></p>
            </body>
        </html>
        """,
        subtype='html'
    )

    with smtplib.SMTP(SMTP_SERVER, PORT) as server:
        server.starttls()
        server.login(sender_email, password_email)
        # server.send_message(msg)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print('Email sent successfully')


if __name__ == '__main__':
    send_email_expired_contract(
        'Contract Expiry Notification',
        receiver,
        "2021-09-30",
        'Rodl Advocates',
        'Rodl Advocates',
    )
