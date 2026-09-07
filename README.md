# 🏠 RoomMatch — Hostel Roommate Finder (Django MVP)

Rule-based, explainable roommate matching for hostel students.

## Quick start (SQLite, dev)
```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed                 # demo students (password: pass12345)
python manage.py createsuperuser      # for the admin panel
python manage.py runserver
```
Open http://127.0.0.1:8000/ — sign up, or log in as a seeded student (e.g. `ananya` / `pass12345`).
Admin panel: http://127.0.0.1:8000/admin/

## Flow
Register → Profile setup → Questionnaire → Find matches → See "why" → Send request → Accept/Reject → Contact unlocks on mutual accept.

## Switch to PostgreSQL (production)
Uncomment the PostgreSQL block in `roommate_finder/settings.py`, install `psycopg2-binary`, set DB_* env vars, then `migrate`.

## Where things live
- `roommate_finder/settings.py` — config (DB, auth, email)
- `accounts/` — custom User model + auth + profile
- `matching/compatibility.py` — the scoring engine (start here to tune weights)
- `matching/models.py` — Preference, RoommateRequest, Room
- `matching/views.py` — dashboard, find, match detail, request system
- `templates/`, `static/` — UI
