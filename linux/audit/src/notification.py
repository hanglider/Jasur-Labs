import smtplib
from email.mime.text import MIMEText
from config import config

class Notification:
    def send_email(self, to_email, subject, message):
        from_email = "st117263@student.spbu.ru"
        password = config.password

        
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        
        try:
            with smtplib.SMTP("smtp.example.com", 587) as server:
                server.starttls()
                server.login(from_email, password)
                server.sendmail(from_email, to_email, msg.as_string())
        except Exception as e:
            print(f"Failed to send email: {e}")
