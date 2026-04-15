import os
import glpi_api
from dotenv import load_dotenv

# =========================
# LOAD ENV
# =========================
load_dotenv()

GLPI_URL = os.getenv("GLPI_URL")
GLPI_API_URL = GLPI_URL + "/api.php/v1"

APP_TOKEN = os.getenv("GLPI_APP_TOKEN")
USER_TOKEN = os.getenv("GLPI_USER_TOKEN")


# =========================
# CONNECTOR
# =========================
def connect_glpi():
    """
    Context manager connection to GLPI API
    """
    return glpi_api.connect(GLPI_API_URL, APP_TOKEN, USER_TOKEN)


# =========================
# NORMALIZE TICKET
# =========================
def normalize_ticket(t):
    """
    Convert GLPI raw ticket into unified format
    """

    ticket_id = t.get("2") or t.get("id")

    return {
        "id": str(ticket_id),
        "summary": t.get("1", "") or t.get("name", ""),
        "description": t.get("content", "") or t.get("description", ""),
        "status": str(t.get("12", "1")),
        "project": t.get("entities_id", "glpi"),
        "assigned_to": t.get("users_id_assign"),
        "source": "glpi",
        "url": f"{GLPI_URL}/front/ticket.form.php?id={ticket_id}"
    }


# =========================
# GET ALL TICKETS
# =========================
def get_all_tickets_glpi():
    tickets = []

    try:
        with connect_glpi() as glpi:
            raw = glpi.search("Ticket")

            for t in raw:
                tickets.append(normalize_ticket(t))

    except glpi_api.GLPIError as err:
        print("GLPI error:", str(err))

    return tickets


# =========================
# GET BY ENTITY
# =========================
def get_tickets_glpi_by_entity(entity_id):
    tickets = []

    try:
        with connect_glpi() as glpi:
            filters = {
                "criteria": [
                    {
                        "field": "entities_id",
                        "searchtype": "equals",
                        "value": entity_id
                    }
                ]
            }

            raw = glpi.search("Ticket", **filters)

            for t in raw:
                tickets.append(normalize_ticket(t))

    except glpi_api.GLPIError as err:
        print("GLPI error:", str(err))

    return tickets


# =========================
# GET SINGLE TICKET
# =========================
def get_ticket_by_id(ticket_id):
    try:
        with connect_glpi() as glpi:
            t = glpi.get_item("Ticket", ticket_id)
            return normalize_ticket(t)

    except glpi_api.GLPIError as err:
        print("GLPI error:", str(err))
        return None


# =========================
# GROUP BY USER
# =========================
def group_by_assigned_user(tickets):
    grouped = {}

    for t in tickets:
        user = t.get("assigned_to") or "unassigned"

        if user not in grouped:
            grouped[user] = []

        grouped[user].append(t)

    return grouped


# =========================
# OPTIONAL: USERS LIST
# =========================
def get_users():
    try:
        with connect_glpi() as glpi:
            return glpi.get_all_items("User")
    except glpi_api.GLPIError as err:
        print("GLPI error:", str(err))
        return []