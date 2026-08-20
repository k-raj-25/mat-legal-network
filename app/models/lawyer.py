from datetime import datetime, timezone

from app.constants import STATUS_APPROVED, STATUS_PENDING, STATUS_REJECTED
from app.extensions import db


class Lawyer(db.Model):
    """Lawyer profile linked to a login account. Public only when approved."""

    __tablename__ = "lawyers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=True,
        index=True,
    )
    full_name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(140), unique=True, nullable=False, index=True)
    bar_council_number = db.Column(db.String(40), unique=True, nullable=True, index=True)
    years_experience = db.Column(db.Integer, nullable=False, default=0)
    address = db.Column(db.Text, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(500), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    mobile = db.Column(db.String(20), nullable=True)
    approval_status = db.Column(
        db.String(20),
        nullable=False,
        default=STATUS_PENDING,
        index=True,
    )
    rejection_reason = db.Column(db.Text, nullable=True)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    is_approved = db.Column(db.Boolean, nullable=False, default=False, index=True)
    is_featured = db.Column(db.Boolean, nullable=False, default=False, index=True)
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

    user = db.relationship("User", back_populates="lawyer")
    practice_areas = db.relationship(
        "LawyerPracticeArea",
        back_populates="lawyer",
        cascade="all, delete-orphan",
        order_by="LawyerPracticeArea.name",
    )
    languages = db.relationship(
        "LawyerLanguage",
        back_populates="lawyer",
        cascade="all, delete-orphan",
        order_by="LawyerLanguage.name",
    )
    locations = db.relationship(
        "LawyerLocation",
        back_populates="lawyer",
        cascade="all, delete-orphan",
        order_by="LawyerLocation.state, LawyerLocation.city",
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
    def practice_area(self) -> str:
        names = [item.name for item in self.practice_areas]
        return ", ".join(names)

    @property
    def practice_area_names(self) -> list[str]:
        return [item.name for item in self.practice_areas]

    @property
    def language_names(self) -> list[str]:
        return [item.name for item in self.languages]

    @property
    def languages_label(self) -> str:
        return ", ".join(self.language_names)

    @property
    def city(self) -> str:
        if not self.locations:
            return ""
        return self.locations[0].city

    @property
    def state(self) -> str | None:
        if not self.locations:
            return None
        return self.locations[0].state

    @property
    def location_label(self) -> str:
        labels = []
        for loc in self.locations:
            if loc.state:
                labels.append(f"{loc.city}, {loc.state}")
            else:
                labels.append(loc.city)
        return "; ".join(labels)

    @property
    def is_pending(self) -> bool:
        return self.approval_status == STATUS_PENDING

    @property
    def is_rejected(self) -> bool:
        return self.approval_status == STATUS_REJECTED

    def approve(self) -> None:
        self.approval_status = STATUS_APPROVED
        self.is_approved = True
        self.rejection_reason = None

    def reject(self, reason: str) -> None:
        self.approval_status = STATUS_REJECTED
        self.is_approved = False
        self.rejection_reason = (reason or "").strip() or "Your application was not approved."

    def mark_pending(self) -> None:
        self.approval_status = STATUS_PENDING
        self.is_approved = False
        self.rejection_reason = None


class LawyerPracticeArea(db.Model):
    __tablename__ = "lawyer_practice_areas"
    __table_args__ = (
        db.UniqueConstraint("lawyer_id", "name", name="uq_lawyer_practice_area"),
    )

    id = db.Column(db.Integer, primary_key=True)
    lawyer_id = db.Column(
        db.Integer,
        db.ForeignKey("lawyers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = db.Column(db.String(80), nullable=False)

    lawyer = db.relationship("Lawyer", back_populates="practice_areas")


class LawyerLanguage(db.Model):
    __tablename__ = "lawyer_languages"
    __table_args__ = (
        db.UniqueConstraint("lawyer_id", "name", name="uq_lawyer_language"),
    )

    id = db.Column(db.Integer, primary_key=True)
    lawyer_id = db.Column(
        db.Integer,
        db.ForeignKey("lawyers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = db.Column(db.String(80), nullable=False)

    lawyer = db.relationship("Lawyer", back_populates="languages")


class LawyerLocation(db.Model):
    __tablename__ = "lawyer_locations"
    __table_args__ = (
        db.UniqueConstraint("lawyer_id", "state", "city", name="uq_lawyer_location"),
    )

    id = db.Column(db.Integer, primary_key=True)
    lawyer_id = db.Column(
        db.Integer,
        db.ForeignKey("lawyers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    state = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False, index=True)

    lawyer = db.relationship("Lawyer", back_populates="locations")
