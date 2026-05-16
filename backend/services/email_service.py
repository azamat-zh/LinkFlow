import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to_address: str, subject: str, body: str) -> dict:
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER", "")
    password = os.environ.get("SMTP_PASSWORD", "")
    sender = os.environ.get("SMTP_FROM", user)

    if not user or not password:
        return {"sent": False, "reason": "SMTP credentials not configured"}

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(sender, to_address, msg.as_string())
        return {"sent": True}
    except Exception as e:
        return {"sent": False, "reason": str(e)}


def send_match_notifications(
    actor_a_email: str | None,
    actor_a_name: str,
    message_to_a: str,
    actor_b_email: str | None,
    actor_b_name: str,
    message_to_b: str,
) -> dict:
    results = {}

    if actor_a_email:
        results["actor_a"] = send_email(
            to_address=actor_a_email,
            subject=f"LinkFlow: You have a new match!",
            body=message_to_a,
        )
    else:
        results["actor_a"] = {"sent": False, "reason": f"No email on file for {actor_a_name}"}

    if actor_b_email:
        results["actor_b"] = send_email(
            to_address=actor_b_email,
            subject=f"LinkFlow: You have a new match!",
            body=message_to_b,
        )
    else:
        results["actor_b"] = {"sent": False, "reason": f"No email on file for {actor_b_name}"}

    return results
