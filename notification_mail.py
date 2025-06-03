import os
import smtplib
from pathlib import Path
from smtplib import SMTPException

import pymysql.connections
from dotenv import load_dotenv
from email.utils import formataddr
from pymysql.cursors import DictCursor
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText




# Trying to get the current directory to load the environment variables
# The script below works for both file-based or interactive python sessions like REPL
current_dir = Path(__file__).resolve().parent if '__file__' in locals() else Path.cwd()
env_directory = current_dir / '.env'
print(f"Email notification: {env_directory}")

# Now let's load the environment variables to get the email credentials
# we pass the absolute path to the .env file to the load_dotenv function
load_dotenv(env_directory)

# load_dotenv("/home/dev-lyn/Documents/PycharmProjects/backend-kl/.env")
# load_dotenv("/backend-kl/.env")

# Now we have all the environment variables
sender_email = os.getenv('SENDER_EMAIL')
password_email = os.getenv('EMAIL_PASSWORD')
# receiver = os.getenv('RECEIVER_EMAIL')
port = 587
smtp_server = os.getenv('SMTP_SERVER')
user = os.getenv('DB_USER_LOCAL')
localhost = os.getenv('DB_HOST')
password= os.getenv('DB_PASSWORD')
database= os.getenv('DB_DATABASE')

db = pymysql.connect(
    host=localhost,
    user=user,
    password=password,
    database=database,
    cursorclass=DictCursor
)



# Now writing the function for sending emails
def send_email_expired_contract(subject, receiver_email, expiry_date, contract_name, vendor_name, country):
    # initialize the EmailMessage object
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = formataddr(('Contract Expiry Notification', f'{sender_email}'))
    msg['To'] = receiver_email

    msg.add_alternative(
        f"""\
        <html>
            <body>
                <p>Hello,</p>
                
                <p>I hope you are well.</p>
                <p>This is to inform you that the contract for <strong>{contract_name}</strong> with <strong>{vendor_name}</strong> for <strong>{country}</strong> will expire on <strong>{expiry_date}</strong>.</p>
                <p>Please take the necessary steps to renew the contract.</p>
            
                <p>Thank you.</p>
                <br>
                <p>Best Regards,</p>
                <p>VulavuTech Group</p>
                     
                <p>&copy; 2025 VulavuTech Group | Need help? <a href="mailto:info@vulavutech.org">Contact Support</a></p>
            </body>
        </html>
        """

    text = f"""\
    Hello,
    
    This is to inform you that the contract for {contract_name} with {vendor_name} for {country} will expire on {expiry_date}.
    
    Please take the necessary steps to renew the contract.
    
    Thank you.
    
    Best Regards,
    VulavuTech Group
    
    © 2025 VulavuTech Group | Need help? Contact Support: info@vulavutech.org    
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = formataddr(('Vulavu Tech', f'{sender_email}'))
    message["To"] = receiver_email

    # Attach both text and html multipart messages for recipient
    message.attach(MIMEText(html, "html"))
    message.attach(MIMEText(text, "plain"))



    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, password_email)
            # server.send_message(msg)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print('Email sent successfully')
            return True
    except SMTPException as e:
        print(f'Error sending email: {e}, time: {datetime.now()}')
        return False



def get_emails():
    with db.cursor() as cursor:
        try:
            query = """
            SELECT * FROM KlContract.expiry_emails
            """
            cursor.execute(query)
            emails = cursor.fetchall()
            return emails
        except Exception as e:
            print(f'Error fetching emails for expiry notification: {e}, time: {datetime.now()}')
            return None


def get_expiring_contracts_three_months():
    today = datetime.now().date()
    threshold_date = today + timedelta(days=90)
    with db.cursor() as cursor:
        try:
            query = """
               SELECT * FROM KlContract.contracts  WHERE status = 'active' AND end_date <= %s
               """
            cursor.execute(query, threshold_date)
            contracts = cursor.fetchall()
            return contracts
        except Exception as e:
            print(f'Error fetching expiring contracts: {e}, time: {datetime.now()}')
            return None

def mark_email_sent(contract_id:int):
    with db.cursor() as cursor:
        try:
            query = """
            UPDATE KlContract.contracts SET email_sent = 'yes' where id = %s
            """
            cursor.execute(query, contract_id)
            db.commit()
            return True
        except Exception as e:
            print(f'Error marking email sent: {e}')
            db.rollback()
            return False

def expiring_contracts_three_months():
    print("Here in expiry email notification function")
    emails = get_emails()
    if len(emails) > 0:
        contracts = get_expiring_contracts_three_months()
        if len(contracts) > 0:
            for contract in contracts:
                for email in emails:
                    email_sent =  send_email_expired_contract(
                        'Contract Expiry Notification',
                        email['email'],
                        contract['end_date'],
                        contract['contract_name'],
                        contract['vendor_name'],
                        contract['country']
                    )
                    if email_sent:
                        print(f'Email sent successfully time:{datetime.now()} contract: {contract["contract_name"]}')
                        mark_email_sent(contract['id'])
                    else:
                        print(f'Email not sent, time: {datetime.now()} contract: {contract["contract_name"]}')
                # if update_email_sent:
                #     print(f'Email sent updated successfully, time: {datetime.now()}')
                # else:
                #     print(f'Email sent not updated, time: {datetime.now()}')
        else:
            print(f'No contracts expiring in 90 days time: {datetime.now()}')
    else:
        print(f'No emails added yet, time: {datetime.now()}')

#cron job running first day of every month
if __name__ == '__main__':
    expiring_contracts_three_months()
