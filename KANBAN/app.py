from flask import Flask, render_template
from services.trac_tickets import get_all_tickets_trac
from services.mantis_tickets import get_tickets_scraping
from services.glpi_tickets import get_all_tickets_glpi
from utils.normalizer import normalize_all, group_by_status
import os
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
# NAVIGATION (DYNAMIC URLS)
# =========================
@app.context_processor
def inject_nav_links():
    TRAC_BASE = os.getenv("TRAC_BASE")

    TRAC_PROJECTS = os.getenv("TRAC_PROJECTS", "").split(",")
    trac_projects = os.getenv("TRAC_PROJECTS", "").split(",")

    trac_menu = []

    for p in trac_projects:
        trac_menu.append({
            "name": f"{p} - Ver tickets",
            "url": f"{TRAC_BASE}/{p}/report"
        })
        trac_menu.append({
            "name": f"{p} - Crear ticket",
            "url": f"{TRAC_BASE}/{p}/newticket"
        })

    return dict(nav_links=[
        {"name": "Tablero", "url": "/"},

        {
            "name": "Trac",
            "url": "#",
            "children": trac_menu
        },
        {
            "name": "Mantis",
            "url": "#",
            "children": [
                {"name": "Ver tickets", "url": "http://localhost:8989/view_all_bug_page.php"},
                {"name": "Crear ticket", "url": "http://localhost:8989/bug_report_page.php"}
            ]
        },
        {
            "name": "GLPI",
            "url": "#",
            "children": [
                {"name": "Ver tickets", "url": "http://localhost:8070/front/ticket.php"},
                {"name": "Crear ticket", "url": "http://localhost:8070/front/helpdesk.public.php"}
            ]
        }
    ])

# =========================
# FETCH RAW TICKETS
# =========================
def get_all_tickets():
    all_tickets = []

    try:
        trac = get_all_tickets_trac()
        all_tickets.extend(trac)
        print(f"Trac tickets: {len(trac)}")
    except Exception as e:
        print("Trac error:", e)

    try:
        mantis = get_tickets_scraping()
        all_tickets.extend(mantis)
        print(f"Mantis tickets: {len(mantis)}")
    except Exception as e:
        print("Mantis error:", e)

    try:
        glpi = get_all_tickets_glpi()
        all_tickets.extend(glpi)
        print(f"GLPI tickets: {len(glpi)}")
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

    total = sum(len(v) for v in grouped.values())
    print(f"Cache updated: {total} tickets")


# =========================
# ROUTE
# =========================
@app.route("/")
def kanban():
    with lock:
        tickets = tickets_cache.copy()

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
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)