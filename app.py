"""TechTectonics backend: serves the site and a small JSON API over sikkim_disasters.sqlite.
Run:  pip install -r requirements.txt && python app.py   ->  http://127.0.0.1:5000
Adding events over the API needs an admin token:  set ADMIN_TOKEN=your-secret  (unset = writes disabled)."""
import hmac, os, sqlite3
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

HERE = Path(__file__).parent
DB = HERE / "sikkim_disasters.sqlite"
SITE = HERE.parent  # folder holding index.html
app = Flask(__name__)

HAZARDS = {"Landslide", "Earthquake", "GLOF / Flash flood", "Avalanche", "Snowfall / stranding"}
DISTRICTS = {"Gangtok", "Pakyong", "Mangan", "Namchi", "Soreng", "Gyalshing", "Statewide", "Multiple", "Unknown"}
BASIS = {"location in source", "inferred from place name", "not stated in source"}
FIELDS = ["event_id", "date_text", "year", "event", "hazard_type", "location_text", "district_primary",
          "districts_other", "district_basis", "deaths", "missing", "people_affected", "notes", "source"]

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def rows(sql, args=()):
    with conn() as c:
        return [dict(r) for r in c.execute(sql, args).fetchall()]

@app.get("/api/health")
def health():
    return jsonify(status="ok", events=rows("SELECT COUNT(*) n FROM disaster_events")[0]["n"])

@app.get("/api/events")
def events():
    where, args = [], []
    if (v := request.args.get("year_from", type=int)) is not None: where.append("year >= ?"); args.append(v)
    if (v := request.args.get("year_to", type=int)) is not None: where.append("year <= ?"); args.append(v)
    if v := request.args.get("hazard_type"): where.append("hazard_type = ?"); args.append(v)
    if v := request.args.get("district"): where.append("district_primary = ?"); args.append(v)
    sql = "SELECT * FROM disaster_events" + (" WHERE " + " AND ".join(where) if where else "") + " ORDER BY year DESC, event_id"
    return jsonify(rows(sql, args))  # NULL stays null = "not stated", never 0

@app.get("/api/summary")
def summary():
    # reported_* are sums of STATED figures only; *_stated says how many events gave a figure
    return jsonify(rows("""SELECT district_primary AS district, COUNT(*) AS events,
        SUM(deaths) AS deaths_reported, COUNT(deaths) AS deaths_stated,
        SUM(missing) AS missing_reported, COUNT(missing) AS missing_stated
        FROM disaster_events GROUP BY district_primary ORDER BY events DESC"""))

def _int_or_none(v):
    if v in (None, ""): return None
    if isinstance(v, bool) or not isinstance(v, int) or v < 0: raise ValueError("numbers must be whole and >= 0, or null")
    return v

@app.post("/api/events")
def add_event():
    token = os.environ.get("ADMIN_TOKEN", "")
    given = request.headers.get("Authorization", "").removeprefix("Bearer ")
    if not token or not hmac.compare_digest(given, token):
        return jsonify(error="Not authorised (ADMIN_TOKEN not set or wrong)"), 401
    d = request.get_json(silent=True) or {}
    try:
        e = {k: d.get(k) for k in FIELDS if k != "event_id"}
        if not isinstance(e["year"], int) or not 1900 <= e["year"] <= 2100: raise ValueError("year must be a whole year")
        if not str(e["event"] or "").strip(): raise ValueError("event is required")
        if e["hazard_type"] not in HAZARDS: raise ValueError("hazard_type must be one of " + ", ".join(sorted(HAZARDS)))
        if e["district_primary"] not in DISTRICTS: raise ValueError("district_primary must be one of " + ", ".join(sorted(DISTRICTS)))
        if e["district_basis"] not in BASIS: raise ValueError("district_basis must be one of " + ", ".join(sorted(BASIS)))
        for k in ("deaths", "missing", "people_affected"): e[k] = _int_or_none(e[k])
    except ValueError as err:
        return jsonify(error=str(err)), 400
    cols = list(e)
    with conn() as c:
        cur = c.execute(f"INSERT INTO disaster_events ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})", [e[k] for k in cols])
    return jsonify(event_id=cur.lastrowid), 201

@app.get("/")
def site():
    return send_from_directory(SITE, "index.html")

if __name__ == "__main__":
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]; s.close()
    except Exception:
        ip = "your-computer-ip"
    print("\nOn this computer:  http://127.0.0.1:5000")
    print("On your phone (same Wi-Fi):  http://%s:5000\n" % ip)
    app.run(host="0.0.0.0", port=5000, debug=False)
