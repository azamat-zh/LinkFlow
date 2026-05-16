import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def simulate_send(to_name: str, to_email: str | None, subject: str, body: str) -> dict:
    return {
        "simulated": True,
        "sent": True,
        "to_name": to_name,
        "to_email": to_email or f"(no email on file for {to_name})",
        "subject": subject,
        "preview": body[:120] + "…" if len(body) > 120 else body,
    }


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
        return {"sent": True, "simulated": False}
    except Exception as e:
        return {"sent": False, "reason": str(e)}


def send_match_notifications(
    actor_a_name: str,
    message_to_a: str,
    actor_b_name: str,
    message_to_b: str,
    actor_a_email: str | None = None,
    actor_b_email: str | None = None,
) -> dict:
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_password = os.environ.get("SMTP_PASSWORD", "")
    use_real_smtp = bool(smtp_user and smtp_password)

    subject = "LinkFlow: You have a new match!"

    if use_real_smtp and actor_a_email:
        result_a = send_email(actor_a_email, subject, message_to_a)
    else:
        result_a = simulate_send(actor_a_name, actor_a_email, subject, message_to_a)

    if use_real_smtp and actor_b_email:
        result_b = send_email(actor_b_email, subject, message_to_b)
    else:
        result_b = simulate_send(actor_b_name, actor_b_email, subject, message_to_b)

    return {"actor_a": result_a, "actor_b": result_b}
