import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from utils.helpers import read_creds


class SetEmail:
    def __init__(self, to_emails, subject, status, error=None, extra_info=None):
        """
        Initializes the email client and stores all content.
        Arguments:
            to_emails (list): list of recipients
            subject (str): subject line
            status (str): 'Success' or 'Failure'
            error (str, optional): error message for failure
        """
        creds = read_creds('gmail')
            
        self.FROM = creds['username']
        self.TO = to_emails
        self.PASSWORD = creds['password']
        self.subject = f"{subject} | {status}"
        self.body = self._format_body(status, error, extra_info)

    def _format_body(self, status, error=None, extra_info=None):
        if status == "Success":
            body = "✅ Automation ran successfully."
            if extra_info:
                for k, v in extra_info.items():
                    body += f"\n{str(k).capitalize()}: {v}"
            return body
        else:
            return f"❌ Automation failed.\n\nError:\n{error}"

    def send(self):
        # SMTP setup
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.FROM, self.PASSWORD)

        msg = MIMEMultipart()
        msg['From'] = self.FROM
        msg['To'] = ",".join(self.TO)
        msg['Subject'] = self.subject
        msg.attach(MIMEText(self.body, 'plain'))

        server.sendmail(self.FROM, self.TO, msg.as_string())
        server.quit()

        print("📨 Email sent to:", self.TO)
