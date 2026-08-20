from flask import abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from app.constants import (
    DEMO_LAWYERS,
    EXPERIENCE_RANGES,
    INDIAN_STATES,
    LANGUAGES,
    POPULAR_CITIES,
    PRACTICE_AREAS,
    ROLE_LAWYER,
    STATE_CITIES,
    STATUS_REJECTED,
)
from app.extensions import db
from app.email import send_contact_message
from app.forms import (
    ContactForm,
    LawyerLoginForm,
    LawyerReapplyForm,
    LawyerRegistrationForm,
)
from app.lawyers import create_lawyer_account, update_lawyer_reapplication
from app.models import Lawyer, LawyerLocation, LawyerPracticeArea, User
from app.utils import parse_locations


def _lawyer_card_data(lawyer: Lawyer) -> dict:
    return {
        "id": lawyer.id,
        "full_name": lawyer.full_name,
        "slug": lawyer.slug,
        "practice_area": lawyer.practice_area,
        "practice_areas": lawyer.practice_area_names,
        "city": lawyer.city,
        "state": lawyer.state,
        "years_experience": lawyer.years_experience,
        "photo_url": lawyer.photo_url,
        "is_verified": lawyer.is_verified,
        "initials": lawyer.initials,
        "location_label": lawyer.location_label,
        "locations": [
            {"city": loc.city, "state": loc.state} for loc in lawyer.locations
        ],
        "languages": lawyer.language_names,
        "languages_label": lawyer.languages_label,
        "bio": lawyer.bio,
        "address": lawyer.address,
        "phone": lawyer.phone,
        "mobile": lawyer.mobile,
        "is_demo": False,
    }


def _approved_lawyer_query():
    return Lawyer.query.filter_by(is_approved=True).options(
        selectinload(Lawyer.practice_areas),
        selectinload(Lawyer.locations),
        selectinload(Lawyer.languages),
    )


def get_featured_lawyers(limit: int = 8) -> list[dict]:
    """Return approved lawyers from the DB, or demo cards if none exist."""
    try:
        lawyers = (
            _approved_lawyer_query()
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
        query = _approved_lawyer_query()
        if practice_area:
            query = query.filter(
                Lawyer.practice_areas.any(LawyerPracticeArea.name == practice_area)
            )
        if state:
            query = query.filter(Lawyer.locations.any(LawyerLocation.state == state))
        if city:
            query = query.filter(Lawyer.locations.any(LawyerLocation.city == city))
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
        lawyer = _approved_lawyer_query().filter_by(slug=slug).first()
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
    form = ContactForm()
    if form.validate_on_submit():
        if form.website.data:
            flash(
                "Thanks, your message has been sent. We will get back to you soon.",
                "success",
            )
            return redirect(url_for("main.contact"))
        try:
            send_contact_message(
                name=form.name.data.strip(),
                email=form.email.data.strip(),
                body=form.message.data.strip(),
            )
        except Exception:
            current_app.logger.exception("Failed to send contact form email")
            flash(
                "We could not send your message right now. Please email hello@matlegal.in or try again.",
                "error",
            )
        else:
            flash(
                "Thanks, your message has been sent. We will get back to you soon.",
                "success",
            )
            return redirect(url_for("main.contact"))
    return render_template("contact.html", form=form)


def _current_lawyer() -> Lawyer | None:
    if not current_user.is_authenticated:
        return None
    if getattr(current_user, "role", None) != ROLE_LAWYER:
        return None
    return getattr(current_user, "lawyer", None)


def _redirect_registered_lawyer(lawyer: Lawyer):
    if lawyer.approval_status == STATUS_REJECTED:
        return redirect(url_for("main.reapply"))
    return redirect(url_for("main.account"))


def _form_locations(lawyer: Lawyer | None = None):
    if request.method == "POST":
        states = request.form.getlist("states")
        cities = request.form.getlist("cities")
        locations, errors = parse_locations(states, cities)
        return locations, errors, states, cities

    if lawyer is not None:
        states = [loc.state for loc in lawyer.locations]
        cities = [f"{loc.state}|{loc.city}" for loc in lawyer.locations]
        return [(loc.state, loc.city) for loc in lawyer.locations], [], states, cities
    return [], [], [], []


def _submitted_form_is_valid(form) -> bool:
    try:
        return form.validate_on_submit()
    except SQLAlchemyError:
        db.session.rollback()
        flash(
            "We could not reach the database. Please try again in a moment.",
            "error",
        )
        return False


def login():
    if current_user.is_authenticated and _current_lawyer() is not None:
        return _redirect_registered_lawyer(_current_lawyer())

    form = LawyerLoginForm()
    if _submitted_form_is_valid(form):
        email = form.email.data.strip().lower()
        try:
            user = User.query.filter_by(email=email).first()
        except SQLAlchemyError:
            db.session.rollback()
            flash(
                "We could not reach the database. Please try again in a moment.",
                "error",
            )
            return render_template("auth/login.html", form=form)
        if (
            user is None
            or user.role != ROLE_LAWYER
            or user.lawyer is None
            or not user.check_password(form.password.data)
        ):
            flash("Invalid email or password.", "error")
        else:
            login_user(user)
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            return redirect(url_for("main.account"))

    return render_template("auth/login.html", form=form)


def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.index"))


def signup():
    return redirect(url_for("main.register_lawyer"))


def register_lawyer():
    lawyer = _current_lawyer()
    if lawyer is not None:
        return _redirect_registered_lawyer(lawyer)

    form = LawyerRegistrationForm()
    locations, location_errors, selected_states, selected_cities = _form_locations()
    if _submitted_form_is_valid(form) and not location_errors:
        try:
            user = create_lawyer_account(form, locations)
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "error")
        except SQLAlchemyError:
            db.session.rollback()
            flash("We could not complete your registration. Please try again.", "error")
        else:
            login_user(user)
            flash(
                "Your registration was submitted and is pending admin approval.",
                "success",
            )
            return redirect(url_for("main.account"))

    return render_template(
        "auth/register_lawyer.html",
        form=form,
        location_errors=location_errors,
        selected_states=selected_states,
        selected_cities=selected_cities,
        practice_areas=PRACTICE_AREAS,
        languages=LANGUAGES,
        states=INDIAN_STATES,
        state_cities=STATE_CITIES,
        is_reapply=False,
    )


@login_required
def account():
    lawyer = _current_lawyer()
    if lawyer is None:
        abort(403)
    return render_template("auth/account.html", lawyer=lawyer)


@login_required
def reapply():
    lawyer = _current_lawyer()
    if lawyer is None:
        abort(403)
    if lawyer.approval_status != STATUS_REJECTED:
        return redirect(url_for("main.account"))

    form = LawyerReapplyForm(lawyer_id=lawyer.id)
    locations, location_errors, selected_states, selected_cities = _form_locations(
        lawyer
    )
    if request.method == "GET":
        form.full_name.data = lawyer.full_name
        form.phone.data = lawyer.phone
        form.mobile.data = lawyer.mobile
        form.bar_council_number.data = lawyer.bar_council_number
        form.practice_areas.data = lawyer.practice_area_names
        form.years_experience.data = lawyer.years_experience
        form.languages.data = lawyer.language_names
        form.address.data = lawyer.address
        form.bio.data = lawyer.bio

    if _submitted_form_is_valid(form) and not location_errors:
        try:
            update_lawyer_reapplication(lawyer, form, locations)
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "error")
        except SQLAlchemyError:
            db.session.rollback()
            flash("We could not submit your application. Please try again.", "error")
        else:
            flash(
                "Your application was resubmitted and is pending admin approval.",
                "success",
            )
            return redirect(url_for("main.account"))

    return render_template(
        "auth/register_lawyer.html",
        form=form,
        location_errors=location_errors,
        selected_states=selected_states,
        selected_cities=selected_cities,
        practice_areas=PRACTICE_AREAS,
        languages=LANGUAGES,
        states=INDIAN_STATES,
        state_cities=STATE_CITIES,
        is_reapply=True,
        lawyer=lawyer,
    )


def privacy():
    return render_template("legal/privacy.html")


def terms():
    return render_template("legal/terms.html")
