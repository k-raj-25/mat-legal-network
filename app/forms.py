from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import (
    EmailField,
    IntegerField,
    PasswordField,
    SelectMultipleField,
    StringField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    InputRequired,
    Length,
    NumberRange,
    ValidationError,
)

from app.constants import ALLOWED_PHOTO_EXTENSIONS, LANGUAGES, PRACTICE_AREAS
from app.models import Lawyer, User
from app.utils import is_valid_mobile, is_valid_phone, normalize_mobile


PHOTO_MESSAGE = "Please upload a JPG, PNG, or WEBP photo."


class ContactForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(min=2, max=120)],
    )
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=120)],
    )
    message = TextAreaField(
        "Message",
        validators=[DataRequired(), Length(min=10, max=4000)],
    )
    website = StringField("Website", validators=[Length(max=200)])


class LawyerLoginForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=120)],
    )
    password = PasswordField("Password", validators=[DataRequired()])


class LawyerProfileForm(FlaskForm):
    full_name = StringField(
        "Full name",
        validators=[DataRequired(), Length(min=2, max=120)],
    )
    phone = StringField(
        "Phone (office / landline)",
        validators=[DataRequired(), Length(min=8, max=20)],
    )
    mobile = StringField(
        "Mobile number",
        validators=[DataRequired(), Length(min=10, max=15)],
    )
    bar_council_number = StringField(
        "Bar Council registration number",
        validators=[DataRequired(), Length(min=5, max=40)],
    )
    practice_areas = SelectMultipleField(
        "Practice areas",
        choices=[(area, area) for area in PRACTICE_AREAS],
        validators=[DataRequired(message="Select at least one practice area.")],
    )
    years_experience = IntegerField(
        "Years of experience",
        validators=[InputRequired(), NumberRange(min=0, max=70)],
    )
    languages = SelectMultipleField(
        "Languages",
        choices=[(lang, lang) for lang in LANGUAGES],
        validators=[DataRequired(message="Select at least one language.")],
    )
    address = TextAreaField(
        "Address",
        validators=[DataRequired(), Length(min=8, max=500)],
    )
    bio = TextAreaField(
        "About",
        validators=[DataRequired(), Length(min=20, max=4000)],
    )
    photo = FileField(
        "Profile photo",
        validators=[
            FileAllowed(sorted(ALLOWED_PHOTO_EXTENSIONS), PHOTO_MESSAGE),
        ],
    )

    def __init__(self, *args, lawyer_id: int | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.lawyer_id = lawyer_id

    def validate_phone(self, field):
        if not is_valid_phone(field.data):
            raise ValidationError("Enter a valid office or landline number.")

    def validate_mobile(self, field):
        if not is_valid_mobile(field.data):
            raise ValidationError("Enter a valid 10-digit Indian mobile number.")
        field.data = normalize_mobile(field.data)

    def validate_bar_council_number(self, field):
        number = (field.data or "").strip()
        field.data = number
        query = Lawyer.query.filter_by(bar_council_number=number)
        if self.lawyer_id is not None:
            query = query.filter(Lawyer.id != self.lawyer_id)
        if query.first() is not None:
            raise ValidationError(
                "This Bar Council registration number is already registered."
            )


class LawyerRegistrationForm(LawyerProfileForm):
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=120)],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8, max=128)],
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    photo = FileField(
        "Profile photo",
        validators=[
            FileRequired(message="Please upload a profile photo."),
            FileAllowed(sorted(ALLOWED_PHOTO_EXTENSIONS), PHOTO_MESSAGE),
        ],
    )

    def validate_email(self, field):
        email = (field.data or "").strip().lower()
        field.data = email
        if User.query.filter_by(email=email).first() is not None:
            raise ValidationError("An account with this email already exists.")


class LawyerReapplyForm(LawyerProfileForm):
    pass
