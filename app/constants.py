"""Shared constants for lawyer discovery filters and categories."""

PRACTICE_AREAS = [
    "Criminal",
    "Family",
    "Divorce",
    "Property",
    "Corporate",
    "Civil",
    "Consumer",
    "Cyber",
]

EXPERIENCE_RANGES = [
    ("0-5", "0–5 years"),
    ("5-10", "5–10 years"),
    ("10-15", "10–15 years"),
    ("15+", "15+ years"),
]

STATE_CITIES = {
    "Delhi": ["Delhi"],
    "Gujarat": ["Ahmedabad"],
    "Karnataka": ["Bengaluru"],
    "Maharashtra": ["Mumbai", "Pune"],
    "Rajasthan": ["Jaipur"],
    "Tamil Nadu": ["Chennai"],
    "Telangana": ["Hyderabad"],
    "Uttar Pradesh": ["Lucknow"],
    "West Bengal": ["Kolkata"],
}

INDIAN_STATES = list(STATE_CITIES.keys())

POPULAR_CITIES = [
    city for cities in STATE_CITIES.values() for city in cities
]

# Used only when the database has no approved lawyers yet.
DEMO_LAWYERS = [
    {
        "id": None,
        "full_name": "Adv. Priya Sharma",
        "slug": "priya-sharma",
        "practice_area": "Family",
        "city": "Mumbai",
        "state": "Maharashtra",
        "years_experience": 12,
        "photo_url": None,
        "is_verified": True,
        "initials": "PS",
        "location_label": "Mumbai, Maharashtra",
        "is_demo": True,
    },
    {
        "id": None,
        "full_name": "Adv. Arjun Mehta",
        "slug": "arjun-mehta",
        "practice_area": "Criminal",
        "city": "Delhi",
        "state": "Delhi",
        "years_experience": 18,
        "photo_url": None,
        "is_verified": True,
        "initials": "AM",
        "location_label": "Delhi, Delhi",
        "is_demo": True,
    },
    {
        "id": None,
        "full_name": "Adv. Sneha Iyer",
        "slug": "sneha-iyer",
        "practice_area": "Corporate",
        "city": "Bengaluru",
        "state": "Karnataka",
        "years_experience": 9,
        "photo_url": None,
        "is_verified": True,
        "initials": "SI",
        "location_label": "Bengaluru, Karnataka",
        "is_demo": True,
    },
    {
        "id": None,
        "full_name": "Adv. Rohan Kapoor",
        "slug": "rohan-kapoor",
        "practice_area": "Property",
        "city": "Pune",
        "state": "Maharashtra",
        "years_experience": 14,
        "photo_url": None,
        "is_verified": True,
        "initials": "RK",
        "location_label": "Pune, Maharashtra",
        "is_demo": True,
    },
]
