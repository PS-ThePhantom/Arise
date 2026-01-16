import ssl, smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from .db.crud import error_log

def send_email(email_recipient, message):
    try:
        smtp_server = os.getenv("EMAIL_SMTP")
        smtp_port = int(os.getenv("EMAIL_PORT", 465))
        smtp_password = os.getenv("EMAIL_PASSWORD")
        email_sender = os.getenv("EMAIL")

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(email_sender, smtp_password)
            server.sendmail(email_sender, email_recipient, message)
        return None
    
    except Exception as e:
        error_log(f"Failed to send email to {email_recipient}: {str(e)}", None)
        return {"error": "Error sending email. Please try again later, make sure the email address is correct."}
    
def create_email(email_recipient, subject, body, attachments=None):

    msg = MIMEMultipart()
    msg['From'] = os.getenv("EMAIL")
    msg['To'] = email_recipient
    msg['Subject'] = subject

    # Add body to email
    msg.attach(MIMEText(body, 'plain'))

    # Add attachments if provided
    if attachments:
        for file in attachments:
            with open(file['file'], "rb") as f:
                attach = MIMEApplication(f.read())
                attach.add_header('Content-Disposition', 'attachment', filename=file['name'])
                msg.attach(attach)

    return send_email(email_recipient, msg.as_string())