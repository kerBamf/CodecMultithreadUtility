import smtplib, ssl
import mimetypes
import os
from email.message import EmailMessage
from email.policy import Policy
from dotenv import load_dotenv


# Importing environment variables
load_dotenv()

TEST_PATH = os.environ.get("OUTPUT_FILES_PATH")


def email_utility(email_from, email_to, email_subject, email_text, file_path=None):

    msg = EmailMessage()
    msg["From"] = email_from
    msg["To"] = email_to
    msg["Subject"] = email_subject
    msg.set_content(email_text)

    server = "exchange2007.mskcc.org"
    port = 25
    if file_path != None:
        file_data = open(file_path, "rb").read()
        msg.add_attachment(
            file_data,
            maintype="application",
            subtype="xlsx",
            filename=(file_path.split("/").pop()),
        )
    smtp = smtplib.SMTP(server, port)
    smtp.send_message(msg)
    smtp.quit()


if __name__ == "__main__":
    email_utility(
        "reboot_report_noreply@mskcc.org",
        "pedigoz@mskcc.org",
        "Yup, another test email",
        "Hey Zach,\r\n\r\nHere's the results of this week's automated reboot. Do good, you.\r\n\r\nZach the Robot",
        TEST_PATH + "automated_reboot-08-07.xlsx",
    )
