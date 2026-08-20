from app.constants import ROLE_LAWYER
from app.extensions import db
from app.models import (
    Lawyer,
    LawyerLanguage,
    LawyerLocation,
    LawyerPracticeArea,
    User,
)
from app.utils import (
    delete_lawyer_photo,
    file_has_name,
    save_lawyer_photo,
    unique_lawyer_slug,
)


def replace_practice_areas(lawyer: Lawyer, names: list[str]) -> None:
    if lawyer.id is not None:
        LawyerPracticeArea.query.filter_by(lawyer_id=lawyer.id).delete()
        db.session.flush()
        db.session.expire(lawyer, ["practice_areas"])
    else:
        lawyer.practice_areas.clear()
    seen: set[str] = set()
    for name in names:
        if name and name not in seen:
            seen.add(name)
            lawyer.practice_areas.append(LawyerPracticeArea(name=name))


def replace_languages(lawyer: Lawyer, names: list[str]) -> None:
    if lawyer.id is not None:
        LawyerLanguage.query.filter_by(lawyer_id=lawyer.id).delete()
        db.session.flush()
        db.session.expire(lawyer, ["languages"])
    else:
        lawyer.languages.clear()
    seen: set[str] = set()
    for name in names:
        if name and name not in seen:
            seen.add(name)
            lawyer.languages.append(LawyerLanguage(name=name))


def replace_locations(lawyer: Lawyer, locations: list[tuple[str, str]]) -> None:
    if lawyer.id is not None:
        LawyerLocation.query.filter_by(lawyer_id=lawyer.id).delete()
        db.session.flush()
        db.session.expire(lawyer, ["locations"])
    else:
        lawyer.locations.clear()
    seen: set[tuple[str, str]] = set()
    for state, city in locations:
        pair = (state, city)
        if pair not in seen:
            seen.add(pair)
            lawyer.locations.append(LawyerLocation(state=state, city=city))


def apply_profile_fields(lawyer: Lawyer, form, locations: list[tuple[str, str]]) -> None:
    lawyer.full_name = form.full_name.data.strip()
    lawyer.slug = unique_lawyer_slug(lawyer.full_name, exclude_id=lawyer.id)
    lawyer.bar_council_number = form.bar_council_number.data.strip()
    lawyer.years_experience = int(form.years_experience.data)
    lawyer.address = form.address.data.strip()
    lawyer.bio = form.bio.data.strip()
    lawyer.phone = form.phone.data.strip()
    lawyer.mobile = form.mobile.data
    replace_practice_areas(lawyer, form.practice_areas.data or [])
    replace_languages(lawyer, form.languages.data or [])
    replace_locations(lawyer, locations)


def create_lawyer_account(form, locations: list[tuple[str, str]]) -> User:
    user = User(email=form.email.data.strip().lower(), role=ROLE_LAWYER)
    user.set_password(form.password.data)
    lawyer = Lawyer(
        full_name=form.full_name.data.strip(),
        slug=unique_lawyer_slug(form.full_name.data),
    )
    lawyer.mark_pending()
    user.lawyer = lawyer
    apply_profile_fields(lawyer, form, locations)
    db.session.add(user)
    db.session.flush()
    lawyer.photo_url = save_lawyer_photo(form.photo.data)
    db.session.commit()
    return user


def update_lawyer_reapplication(lawyer: Lawyer, form, locations: list[tuple[str, str]]) -> None:
    apply_profile_fields(lawyer, form, locations)
    if file_has_name(form.photo.data):
        previous = lawyer.photo_url
        lawyer.photo_url = save_lawyer_photo(form.photo.data)
        if previous != lawyer.photo_url:
            delete_lawyer_photo(previous)
    lawyer.mark_pending()
    db.session.commit()
