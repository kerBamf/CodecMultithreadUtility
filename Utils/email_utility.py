import smtplib, ssl
import mimetypes
from email.message import EmailMessage
from email.policy import Policy


def email_utility(subject, content, send_to, send_from, file_path=None, file_name=None):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg.set_content(content)
    msg["To"] = send_to
    msg["From"] = send_from
    if file_path != None:
        with open(file_path, "rb") as fp:
            msg.add_attachment(
                fp.read(),
                maintype="application",
                subype="xlsx",
                filename=file_name,
            )
    with smtplib.SMTP("exchange2007.mskcc.org", 25) as s:
        s.send_message(msg)


if __name__ == "__main__":
    email_utility(
        "Test Email",
        "Hopefully this ish works alright",
        "pedigoz@mkscc.com",
        "reboot_report_donotreply@mskcc.org",
    )
