from flask import jsonify
from sqlalchemy import text

from app.extensions import db


def health():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify(status="ok", database="up"), 200
    except Exception:
        return jsonify(status="degraded", database="down"), 503
