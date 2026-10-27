# TechTectonics backend (SQLite + Flask)
Run: `pip install -r requirements.txt` then `python app.py`, open http://127.0.0.1:5000
- `GET /api/events?year_from=&year_to=&hazard_type=&district=`  events (null = not stated)
- `GET /api/summary`  per-district counts and stated-figure sums
- `POST /api/events`  add an event; needs `ADMIN_TOKEN` env var and header `Authorization: Bearer <token>`
The site loads `/api/events` when served by this app and falls back to its embedded copy otherwise.
This API is read-mostly and has no user accounts; do not expose POST publicly without HTTPS and a strong token.
