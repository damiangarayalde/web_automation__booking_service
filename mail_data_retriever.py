# Importing libraries
import imaplib
import email
import os
from dotenv import load_dotenv

load_dotenv()

email_address = os.environ.get('GMAIL_USER')
password = os.environ.get('GMAIL_PASSWORD')
imap_url = 'imap.gmail.com'
mailbox = "inbox"  # You can change this to the desired mailbox
from_address = os.environ.get('FROM_ADDRESS')

print(password)


# Connect to Gmail IMAP server
mail = imaplib.IMAP4_SSL(imap_url)
mail.login(email_address, password)
mail.select(mailbox)

# Search for all emails in the selected mailbox received from the specified address
status, list_of_mails = mail.search(None, 'FROM', '"{}"'.format(from_address))
# status, list_of_mails = mail.search(None, 'FROM', '"{}"'.format('noreply-prenotami@esteri.it'))

msgs = []  # all the email data are pushed inside an array

email_ids = list_of_mails[0].split()

# Fetch the latest email (you can change the index if needed)
latest_email_id = email_ids[-1]

status, msg_data = mail.fetch(latest_email_id, "(RFC822)")


# Parse the email content
raw_email = msg_data[0][1]
msg = email.message_from_bytes(raw_email)

# Extract text content from the email
if msg.is_multipart():
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            email_body = part.get_payload(decode=True)
            email_text = email_body.decode("utf-8")
            print(email_text)
else:
    email_body = msg.get_payload(decode=True)
    email_text = email_body.decode("utf-8")
    print(email_text)

OTP_code = email_text.split(":")[1]
print(OTP_code)


# Logout from the server
mail.logout()
