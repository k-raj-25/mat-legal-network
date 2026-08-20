from app.extensions import mail


def test_contact_form_is_enabled(client):
    response = client.get("/contact")
    assert response.status_code == 200
    assert b"Send message" in response.data
    assert b'name="name"' in response.data
    assert b"disabled" not in response.data
    assert b"Contact form submissions will be enabled soon" not in response.data


def test_contact_sends_email_to_owner(app, client):
    with app.app_context():
        with mail.record_messages() as outbox:
            response = client.post(
                "/contact",
                data={
                    "name": "Priya Sharma",
                    "email": "priya@example.com",
                    "message": "I need help finding a family lawyer in Mumbai.",
                },
                follow_redirects=True,
            )

            assert response.status_code == 200
            assert b"your message has been sent" in response.data
            assert len(outbox) == 1
            assert outbox[0].recipients == ["rajput.kamal25@gmail.com"]
            assert "priya@example.com" in str(outbox[0].reply_to)
            assert "Priya Sharma" in outbox[0].subject
            assert "priya@example.com" in outbox[0].body
            assert "family lawyer" in outbox[0].body


def test_contact_rejects_short_message(app, client):
    with app.app_context():
        with mail.record_messages() as outbox:
            response = client.post(
                "/contact",
                data={
                    "name": "Priya Sharma",
                    "email": "priya@example.com",
                    "message": "Hi",
                },
            )

            assert response.status_code == 200
            assert outbox == []
            assert b"your message has been sent" not in response.data


def test_contact_honeypot_does_not_send(app, client):
    with app.app_context():
        with mail.record_messages() as outbox:
            response = client.post(
                "/contact",
                data={
                    "name": "Spam Bot",
                    "email": "spam@example.com",
                    "message": "Buy this amazing product today.",
                    "website": "https://spam.example",
                },
                follow_redirects=True,
            )

            assert response.status_code == 200
            assert b"your message has been sent" in response.data
            assert outbox == []
