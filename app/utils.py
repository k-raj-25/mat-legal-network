import os
import re
import uuid

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.constants import ALLOWED_PHOTO_EXTENSIONS, STATE_CITIES
from app.models import Lawyer


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return slug or "lawyer"


def unique_lawyer_slug(full_name: str, exclude_id: int | None = None) -> str:
    base = slugify(full_name)
    slug = base
    suffix = 2
    while True:
        query = Lawyer.query.filter_by(slug=slug)
        if exclude_id is not None:
            query = query.filter(Lawyer.id != exclude_id)
        if query.first() is None:
            return slug
        slug = f"{base}-{suffix}"
        suffix += 1


def normalize_mobile(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    return digits


def is_valid_mobile(value: str) -> bool:
    return bool(re.fullmatch(r"[6-9]\d{9}", normalize_mobile(value)))


def is_valid_phone(value: str) -> bool:
    compact = re.sub(r"[\s\-()]", "", value or "")
    return bool(re.fullmatch(r"\+?\d{8,15}", compact))


def parse_locations(
    states: list[str], city_values: list[str]
) -> tuple[list[tuple[str, str]], list[str]]:
    """Validate that each selected state has at least one matching city.

    City values are encoded as ``State|City``.
    """
    errors: list[str] = []
    selected_states = [state for state in states if state]
    if not selected_states:
        return [], ["Select at least one state."]

    cities_by_state: dict[str, list[str]] = {}
    for raw in city_values:
        if "|" not in raw:
            continue
        state, city = raw.split("|", 1)
        if state and city:
            cities_by_state.setdefault(state, []).append(city)

    locations: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for state in selected_states:
        allowed_cities = STATE_CITIES.get(state)
        if not allowed_cities:
            errors.append(f"{state} is not a supported state.")
            continue
        chosen = cities_by_state.get(state, [])
        if not chosen:
            errors.append(f"Select at least one city in {state}.")
            continue
        for city in chosen:
            if city not in allowed_cities:
                errors.append(f"{city} is not a valid city in {state}.")
                continue
            pair = (state, city)
            if pair not in seen:
                seen.add(pair)
                locations.append(pair)

    return locations, errors


def photo_extension(filename: str) -> str | None:
    if not filename or "." not in filename:
        return None
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_PHOTO_EXTENSIONS:
        return None
    return ext


def save_lawyer_photo(file_storage: FileStorage) -> str:
    filename = secure_filename(file_storage.filename or "")
    ext = photo_extension(filename)
    if ext is None:
        raise ValueError("Please upload a JPG, PNG, or WEBP photo.")
    stored_name = f"{uuid.uuid4().hex}.{ext}"
    dest = os.path.join(current_app.config["UPLOAD_FOLDER"], stored_name)
    os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
    file_storage.save(dest)
    return f"uploads/lawyers/{stored_name}"


def delete_lawyer_photo(photo_url: str | None) -> None:
    if not photo_url or photo_url.startswith(("http://", "https://")):
        return
    if not photo_url.startswith("uploads/lawyers/"):
        return
    filename = os.path.basename(photo_url)
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    try:
        if os.path.isfile(path):
            os.remove(path)
    except OSError:
        pass


def file_has_name(file_storage) -> bool:
    return bool(file_storage and getattr(file_storage, "filename", ""))
