from datetime import datetime, timezone

from app.extensions import db


class Lawyer(db.Model):
    """Approved lawyer profiles shown on the discovery platform."""

    __tablename__ = "lawyers"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(140), unique=True, nullable=False, index=True)
    practice_area = db.Column(db.String(80), nullable=False, index=True)
    city = db.Column(db.String(80), nullable=False, index=True)
    state = db.Column(db.String(80), nullable=True)
    years_experience = db.Column(db.Integer, nullable=False, default=0)
    photo_url = db.Column(db.String(500), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    is_approved = db.Column(db.Boolean, nullable=False, default=False, index=True)
    is_featured = db.Column(db.Boolean, nullable=False, default=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Lawyer {self.full_name!r}>"

    @property
    def initials(self) -> str:
        parts = [p for p in self.full_name.split() if p]
        if not parts:
            return "L"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    @property
    def location_label(self) -> str:
        if self.state:
            return f"{self.city}, {self.state}"
        return self.city
