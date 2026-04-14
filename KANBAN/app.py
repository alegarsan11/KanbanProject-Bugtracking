from flask import Flask, render_template
from services.trac_tickets import get_all_tickets_trac
from services.mantis_tickets import get_tickets_scraping
from services.glpi_tickets import get_all_tickets_glpi
from utils.normalizer import normalize_all, group_by_status

from apscheduler.schedulers.background import BackgroundScheduler
import threading

app = Flask(__name__)

# =========================
# GLOBAL CACHE
# =========================
tickets_cache = {
    "New": [],
    "In-Progress": [],
    "Done": [],
    "On-Hold": []
}

lock = threading.Lock()


# =========================
# FETCH RAW TICKETS
# =========================
def get_all_tickets():
    all_tickets = []

    # TRAC
    try:
        all_tickets.extend(get_all_tickets_trac())
    except Exception as e:
        print("Trac error:", e)

    # MANTIS SCRAPING
    try:
        all_tickets.extend(get_tickets_scraping())
    except Exception as e:
        print("Scraping error:", e)

    # GLPI
    try:
        all_tickets.extend(get_all_tickets_glpi())
    except Exception as e:
        print("GLPI error:", e)
    
    return all_tickets


# =========================
# REFRESH CACHE 
# =========================
def refresh_cache():
    global tickets_cache

    print("Refreshing tickets cache...")

    raw_tickets = get_all_tickets()

    normalized = normalize_all(raw_tickets)

    grouped = group_by_status(normalized)

    with lock:
        tickets_cache = grouped

    print(f"Cache updated: {sum(len(v) for v in grouped.values())} tickets")


# =========================
# ROUTE
# =========================
@app.route("/")
def kanban():
    with lock:
        tickets = tickets_cache

    return render_template("index.html", tickets=tickets)


# =========================
# SCHEDULER
# =========================
scheduler = BackgroundScheduler()

scheduler.add_job(
    func=refresh_cache,
    trigger="interval",
    minutes=5  
)

scheduler.start()

# initial load
refresh_cache()


# =========================
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)