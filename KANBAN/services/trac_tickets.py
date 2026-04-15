import os
import xmlrpc.client
from dotenv import load_dotenv

# =========================
# LOAD ENV
# =========================
load_dotenv()

TRAC_USER = os.getenv("TRAC_USER")
TRAC_PASS = os.getenv("TRAC_PASS")
TRAC_PROJECTS = os.getenv("TRAC_PROJECTS", "").split(",")


# =========================
# BUILD TRAC SERVER URL
# =========================
def build_server(project):
    base_url = f"http://{TRAC_USER}:{TRAC_PASS}@localhost:8080/{project}"
    return xmlrpc.client.ServerProxy(base_url + "/login/xmlrpc"), base_url


# =========================
# GET TICKETS BY PROJECT
# =========================
def get_tickets_by_project(project):
    server, base_url = build_server(project)

    ticket_ids = server.ticket.query("max=0")
    tickets = []

    for t_id in ticket_ids:
        t_data = server.ticket.get(t_id)
        attributes = t_data[3]

        ticket = {
            "id": str(t_id),
            "summary": attributes.get("summary", ""),
            "status": attributes.get("status", ""),
            "description": attributes.get("description", ""),
            "project": project,
            "source": "trac",
            "url": f"{base_url}/ticket/{t_id}"
        }

        tickets.append(ticket)

    return tickets


# =========================
# GET ALL TRAC TICKETS
# =========================
def get_all_tickets_trac():
    all_tickets = []

    for project in TRAC_PROJECTS:
        try:
            all_tickets.extend(get_tickets_by_project(project))
        except Exception as e:
            print(f"Trac error in {project}: {e}")

    return all_tickets