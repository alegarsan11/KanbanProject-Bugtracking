import glpi_api 

# =========================
# CONFIG
# =========================
GLPI_URL = "http://localhost:8070/api.php/v1"
APP_TOKEN = "S1iyTsQvCX94r2IX3LLAS9pVyVIgzF9sJPZmjL9o"
USER_TOKEN = "fXnUx99NQ4uvgPzm1Kxuh2SADwH8Zj0PrrEtTAcc"

# =========================
# INTERNAL CONNECTOR
# =========================
def connect_glpi():
    """
    Context manager connection to GLPI API
    """
    return glpi_api.connect(GLPI_URL, APP_TOKEN, USER_TOKEN)


# =========================
# NORMALIZE TICKET
# =========================
def normalize_ticket(t):
    print(t)
    return {
        "id": str(t.get("2")),
        "summary": t.get("1", ""),
        "description": t.get("content", ""),
        "status": str(t.get("12", "1")),
        "project": t.get("entities_id", "glpi"),
        "assigned_to": t.get("users_id_assign"),
        "source": "glpi"
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
# GET BY ENTITY (PROJECT-LIKE)
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
# GROUP BY ASSIGNED USER
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
# ENRICH USER NAME (OPTIONAL)
# =========================
def enrich_user_names():
    """
    Example helper if you want to resolve user IDs to names
    """
    try:
        with connect_glpi() as glpi:
            return glpi.get_all_items("User")
    except glpi_api.GLPIError as err:
        print("GLPI error:", str(err))
        return []