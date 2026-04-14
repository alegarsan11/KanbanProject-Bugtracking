STATUS_MAP = {
    # NEW
    "new": "New",
    "open": "New",
    "reported": "New",
    "1": "New",
    # IN PROGRESS
    "2": "In-Progress",
    "3": "In-Progress",
    "assigned": "In-Progress",
    "in progress": "In-Progress",
    "acknowledged": "In-Progress",
    "accepted": "In-Progress",
    # DONE
    "resolved": "Done",
    "closed": "Done",
    "5": "Done",
    "6": "Done",

    # OTHER
    "3": "On-Hold",
    "10": "On-Hold",
    "feedback": "On-Hold",
}


def normalize_ticket(ticket):
    """
    Normaliza estructura + estado
    """

    status_raw = ticket.get("status", "").lower()

    return {
        "id": str(ticket.get("id", "")),
        "summary": ticket.get("summary", ""),
        "description": ticket.get("description", ""),
        "project": ticket.get("project", "unknown"),
        "source": ticket.get("source", "unknown"),
        "status_raw": status_raw,
        "status": STATUS_MAP.get(status_raw, "On-Hold")
    }


def normalize_all(tickets):
    return [normalize_ticket(t) for t in tickets]


def group_by_status(tickets):
    grouped = {
        "New": [],
        "In-Progress": [],
        "Done": [],
        "On-Hold": []
    }

    for t in tickets:
        grouped[t["status"]].append(t)

    return grouped