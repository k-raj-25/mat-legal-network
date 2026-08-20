from flask import current_app
from flask_mail import Message

from app.extensions import mail


def send_contact_message(*, name: str, email: str, body: str) -> None:
    """Send a contact-form enquiry to the configured inbox."""
    recipient = current_app.config["CONTACT_RECIPIENT"]
    message = Message(
        subject=f"MAT Legal Network enquiry from {name}",
        recipients=[recipient],
        reply_to=email,
        body=(
            "New enquiry from the MAT Legal Network contact form.\n\n"
            f"Name: {name}\n"
            f"Email: {email}\n\n"
            f"{body}\n"
        ),
    )
    mail.send(message)
