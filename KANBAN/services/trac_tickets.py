import xmlrpc.client

# Configura tus datos
USER = "admin"
PASS = "admin"
URL = f"http://{USER}:{PASS}@localhost:8080/proyectotrac/login/xmlrpc"

server = xmlrpc.client.ServerProxy(URL)
def get_all_tickets_trac():
    # 1. Obtener la lista de todos los IDs de tickets
    ticket_ids = server.ticket.query("max=0") # 0 significa todos
    
    print(f"Se han encontrado {len(ticket_ids)} tickets.\n")
    acum = []
    # 2. Obtener los detalles de cada ticket
    for t_id in ticket_ids:
        # Retorna: [id, time_created, time_changed, attributes]
        t_data = server.ticket.get(t_id)
        attributes = t_data[3]
        acum.append(t_data)
        print(f"ID: {t_id}")
        print(f"Resumen: {attributes['summary']}")
        print(f"Estado: {attributes['status']}")
        print(f"Descripción: {attributes['description']}")
        print("-" * 30)

    return acum