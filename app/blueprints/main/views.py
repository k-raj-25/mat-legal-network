from flask import render_template, request
from sqlalchemy.exc import SQLAlchemyError

from app.constants import (
    DEMO_LAWYERS,
    EXPERIENCE_RANGES,
    INDIAN_STATES,
    POPULAR_CITIES,
    PRACTICE_AREAS,
    STATE_CITIES,
)
from app.extensions import db
from app.models import Lawyer


def _lawyer_card_data(lawyer: Lawyer) -> dict:
    return {
        "id": lawyer.id,
        "full_name": lawyer.full_name,
        "slug": lawyer.slug,
        "practice_area": lawyer.practice_area,
        "city": lawyer.city,
        "state": lawyer.state,
        "years_experience": lawyer.years_experience,
        "photo_url": lawyer.photo_url,
        "is_verified": lawyer.is_verified,
        "initials": lawyer.initials,
        "location_label": lawyer.location_label,
        "is_demo": False,
    }


def get_featured_lawyers(limit: int = 4) -> list[dict]:
    """Return approved lawyers from the DB, or demo cards if none exist."""
    try:
        lawyers = (
            Lawyer.query.filter_by(is_approved=True)
            .order_by(
                Lawyer.is_featured.desc(),
                Lawyer.is_verified.desc(),
                Lawyer.years_experience.desc(),
            )
            .limit(limit)
            .all()
        )
        if lawyers:
            return [_lawyer_card_data(lawyer) for lawyer in lawyers]
    except SQLAlchemyError:
        db.session.rollback()

    return DEMO_LAWYERS[:limit]


def index():
    return render_template(
        "home.html",
        featured_lawyers=get_featured_lawyers(),
        practice_areas=PRACTICE_AREAS,
        experience_ranges=EXPERIENCE_RANGES,
        states=INDIAN_STATES,
        state_cities=STATE_CITIES,
        cities=POPULAR_CITIES,
    )


def find_lawyers():
    practice_area = request.args.get("practice_area", "").strip()
    state = request.args.get("state", "").strip()
    city = request.args.get("city", "").strip()
    # Legacy single-location param from older links.
    location = request.args.get("location", "").strip()
    experience = request.args.get("experience", "").strip()

    if location and not city and not state:
        if location in INDIAN_STATES:
            state = location
        else:
            city = location

    lawyers: list[dict] = []
    try:
        query = Lawyer.query.filter_by(is_approved=True)
        if practice_area:
            query = query.filter(Lawyer.practice_area.ilike(practice_area))
        if state:
            query = query.filter(Lawyer.state.ilike(state))
        if city:
            query = query.filter(Lawyer.city.ilike(city))
        if experience == "0-5":
            query = query.filter(Lawyer.years_experience < 5)
        elif experience == "5-10":
            query = query.filter(
                Lawyer.years_experience >= 5,
                Lawyer.years_experience < 10,
            )
        elif experience == "10-15":
            query = query.filter(
                Lawyer.years_experience >= 10,
                Lawyer.years_experience < 15,
            )
        elif experience == "15+":
            query = query.filter(Lawyer.years_experience >= 15)

        lawyers = [
            _lawyer_card_data(lawyer)
            for lawyer in query.order_by(Lawyer.years_experience.desc()).limit(24).all()
        ]
    except SQLAlchemyError:
        db.session.rollback()

    if not lawyers and not (practice_area or state or city or experience):
        lawyers = DEMO_LAWYERS

    return render_template(
        "find_lawyers.html",
        lawyers=lawyers,
        practice_areas=PRACTICE_AREAS,
        experience_ranges=EXPERIENCE_RANGES,
        states=INDIAN_STATES,
        state_cities=STATE_CITIES,
        cities=POPULAR_CITIES,
        selected_practice_area=practice_area,
        selected_state=state,
        selected_city=city,
        selected_experience=experience,
    )


def lawyer_profile(slug: str):
    lawyer = None
    try:
        lawyer = Lawyer.query.filter_by(slug=slug, is_approved=True).first()
    except SQLAlchemyError:
        db.session.rollback()

    if lawyer is None:
        demo = next((item for item in DEMO_LAWYERS if item["slug"] == slug), None)
        if demo is None:
            return render_template("errors/404.html"), 404
        return render_template("lawyer_profile.html", lawyer=demo)

    return render_template("lawyer_profile.html", lawyer=_lawyer_card_data(lawyer))


def about():
    return render_template("about.html")


def contact():
    return render_template("contact.html")


def login():
    return render_template("auth/login.html")


def signup():
    return render_template("auth/signup.html")


def register_lawyer():
    return render_template("auth/register_lawyer.html")


def privacy():
    return render_template("legal/privacy.html")


def terms():
    return render_template("legal/terms.html")
