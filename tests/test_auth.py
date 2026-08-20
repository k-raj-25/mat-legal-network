from io import BytesIO

from app.constants import ROLE_ADMIN, STATUS_PENDING
from app.extensions import db
from app.models import Lawyer, User


PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _photo():
    return (BytesIO(PNG_1X1), "photo.png")


def registration_data(**overrides):
    data = {
        "full_name": "Adv Test Lawyer",
        "email": "lawyer@example.com",
        "password": "password12",
        "confirm_password": "password12",
        "phone": "02212345678",
        "mobile": "9876543210",
        "bar_council_number": "MAH12345",
        "practice_areas": ["Criminal", "Civil"],
        "years_experience": "8",
        "languages": ["English", "Hindi"],
        "states": ["Maharashtra"],
        "cities": ["Maharashtra|Mumbai"],
        "address": "1 Marine Drive, Mumbai 400001",
        "bio": "Practising criminal and civil law before the Bombay High Court.",
        "photo": _photo(),
    }
    data.update(overrides)
    return data


def test_logged_in_lawyer_cannot_register_again(client):
    client.post(
        "/register-lawyer",
        data=registration_data(),
        content_type="multipart/form-data",
    )
    response = client.get("/register-lawyer")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/account")


def test_signup_redirects_to_register(client):
    response = client.get("/signup")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/register-lawyer")


def test_register_creates_pending_lawyer(client, app):
    response = client.post(
        "/register-lawyer",
        data=registration_data(),
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Pending admin approval" in response.data
    assert b"full_name" not in response.data

    with app.app_context():
        lawyer = Lawyer.query.filter_by(bar_council_number="MAH12345").one()
        assert lawyer.approval_status == STATUS_PENDING
        assert lawyer.is_approved is False
        assert lawyer.user.email == "lawyer@example.com"
        assert lawyer.city == "Mumbai"
        assert "Criminal" in lawyer.practice_area


def test_pending_lawyer_is_not_public(client):
    client.post(
        "/register-lawyer",
        data=registration_data(),
        content_type="multipart/form-data",
    )
    listing = client.get("/find-lawyers")
    assert listing.status_code == 200
    assert b"Adv Test Lawyer" not in listing.data

    profile = client.get("/lawyers/adv-test-lawyer")
    assert profile.status_code == 404


def test_pending_lawyer_can_login(client):
    client.post(
        "/register-lawyer",
        data=registration_data(),
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    client.post("/logout")
    response = client.post(
        "/login",
        data={"email": "lawyer@example.com", "password": "password12"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Pending admin approval" in response.data
    assert b"You cannot edit your details" in response.data


def test_state_without_city_is_rejected(client, app):
    data = registration_data(cities=[])
    response = client.post(
        "/register-lawyer",
        data=data,
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert b"Select at least one city in Maharashtra." in response.data
    with app.app_context():
        assert Lawyer.query.count() == 0


def test_approved_lawyer_appears_in_directory(client, app):
    client.post(
        "/register-lawyer",
        data=registration_data(),
        content_type="multipart/form-data",
    )
    with app.app_context():
        lawyer = Lawyer.query.one()
        lawyer.approve()
        db.session.commit()

    listing = client.get("/find-lawyers")
    assert b"Adv Test Lawyer" in listing.data
    profile = client.get("/lawyers/adv-test-lawyer")
    assert profile.status_code == 200
    assert b"Practising criminal and civil law" in profile.data
    assert b"Hindi" in profile.data


def test_reject_and_reapply(client, app):
    client.post(
        "/register-lawyer",
        data=registration_data(),
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    runner = app.test_cli_runner()
    result = runner.invoke(
        args=["lawyer", "reject", "lawyer@example.com", "--reason", "Bar details incomplete."]
    )
    assert result.exit_code == 0

    account = client.get("/account")
    assert b"Application not approved" in account.data
    assert b"Bar details incomplete." in account.data

    reapply = client.post(
        "/account/reapply",
        data=registration_data(
            full_name="Adv Test Lawyer",
            bio="Updated profile with complete Bar Council details for review.",
            photo=_photo(),
        ),
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert reapply.status_code == 200
    assert b"Pending admin approval" in reapply.data
    with app.app_context():
        lawyer = Lawyer.query.one()
        assert lawyer.approval_status == STATUS_PENDING
        assert lawyer.rejection_reason is None
        assert lawyer.is_approved is False


def test_login_rejects_admin_role(client, app):
    with app.app_context():
        admin = User(email="admin@example.com", role=ROLE_ADMIN)
        admin.set_password("password12")
        db.session.add(admin)
        db.session.commit()

    response = client.post(
        "/login",
        data={"email": "admin@example.com", "password": "password12"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid email or password." in response.data
    assert b"Lawyer login" in response.data


def test_cli_approve(app):
    with app.app_context():
        user = User(email="cli@example.com", role="lawyer")
        user.set_password("password12")
        lawyer = Lawyer(full_name="CLI Lawyer", slug="cli-lawyer")
        lawyer.mark_pending()
        lawyer.bar_council_number = "CLI999"
        user.lawyer = lawyer
        db.session.add(user)
        db.session.commit()

    runner = app.test_cli_runner()
    result = runner.invoke(args=["lawyer", "approve", "cli@example.com"])
    assert result.exit_code == 0
    with app.app_context():
        lawyer = Lawyer.query.filter_by(slug="cli-lawyer").one()
        assert lawyer.is_approved is True
        assert lawyer.approval_status == "approved"
