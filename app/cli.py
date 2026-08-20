import click
from flask import Flask

from app.constants import ROLE_LAWYER
from app.extensions import db
from app.models import User


def register_cli(app: Flask) -> None:
    @app.cli.group("lawyer")
    def lawyer_cli():
        """Approve or reject lawyer registrations."""

    @lawyer_cli.command("approve")
    @click.argument("email")
    def approve(email: str):
        record = _lawyer_for_email(email)
        if record is None:
            raise click.ClickException(f"No lawyer account found for {email}.")
        user, profile = record
        profile.approve()
        db.session.commit()
        click.echo(f"Approved {user.email} ({profile.full_name}).")

    @lawyer_cli.command("reject")
    @click.argument("email")
    @click.option("--reason", required=True, help="Reason shown to the lawyer.")
    def reject(email: str, reason: str):
        record = _lawyer_for_email(email)
        if record is None:
            raise click.ClickException(f"No lawyer account found for {email}.")
        user, profile = record
        profile.reject(reason)
        db.session.commit()
        click.echo(f"Rejected {user.email} ({profile.full_name}).")


def _lawyer_for_email(email: str):
    user = User.query.filter_by(email=email.strip().lower(), role=ROLE_LAWYER).first()
    if user is None or user.lawyer is None:
        return None
    return user, user.lawyer
