"""Import models here so Flask-Migrate and the app can discover them."""

from app.models.lawyer import (  # noqa: F401
    Lawyer,
    LawyerLanguage,
    LawyerLocation,
    LawyerPracticeArea,
)
from app.models.user import User  # noqa: F401
