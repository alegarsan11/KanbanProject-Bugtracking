import xmlrpc.client

# Configura tus datos
USER = "admin"
PASS = "admin"

def get_all_tickets_by_project(project):
    URL = f"http://{USER}:{PASS}@localhost:8080/{project}/login/xmlrpc"
    server = xmlrpc.client.ServerProxy(URL)

    ticket_ids = server.ticket.query("max=0")

    acum = []

    for t_id in ticket_ids:
        t_data = server.ticket.get(t_id)
        attributes = t_data[3]

        ticket = {
            "id": str(t_id),
            "summary": attributes.get("summary", ""),
            "status": attributes.get("status", ""),
            "description": attributes.get("description", ""),
            "project": project,
            "source": "trac"
        }

        acum.append(ticket)

    return acum


def get_all_tickets_trac():
    projects = ['otro_proyect', 'proyectotrac']
    accum = []

    for p in projects:
        accum.extend(get_all_tickets_by_project(p))

    return accum