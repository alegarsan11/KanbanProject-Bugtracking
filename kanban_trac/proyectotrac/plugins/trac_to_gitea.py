import requests
from trac.core import *
from trac.ticket.api import ITicketChangeListener

class TracToGiteaSync(Component):
    implements(ITicketChangeListener)

    def __init__(self):
        # Configuración de tu Gitea
        self.gitea_url = "http://localhost:3000/api/v1/repos/alejandro/prueba/issues"
        self.gitea_token = "79597f2d9ddeeefc741e4bcacdb840375fd4c98b"

    def _build_payload(self, ticket):
        """Método auxiliar para construir el cuerpo y título de la issue."""
        body_content = f"""> Incidencia sincronizada automáticamente desde **Trac** (Entorno de Gobernanza).

---

###  Información del Ticket
- **ID en Trac:** `#{ticket.id}`
- **Tipo:** `{ticket['type']}`
- **Estado:** `{ticket['status']}`


---

###  Descripción Original
{ticket['description']}

---

###  Enlaces y Referencias
- **Enlace directo al Ticket en Trac:** [Ver en Trac](http://127.0.0.1:8080/proyectotrac/ticket/{ticket.id})
"""
        return {
            "title": f"[Trac #{ticket.id}] {ticket['summary']}",
            "body": body_content
        }

    def _find_gitea_issue_number(self, ticket_id, headers):
        """Busca en Gitea si ya existe una issue que contenga el ID del ticket de Trac en el título."""
        try:
            # Buscamos issues que coincidan con el patrón [Trac #ID]
            search_url = f"{self.gitea_url}?q=Trac #{ticket_id}&state=all"
            response = requests.get(search_url, headers=headers, timeout=5)
            if response.status_code == 200:
                issues = response.json()
                for issue in issues:
                    if f"[Trac #{ticket_id}]" in issue['title']:
                        return issue['number']
        except Exception as e:
            self.log.error(f"Error buscando issue existente en Gitea: {str(e)}")
        return None

    def ticket_created(self, ticket):
        # Solo sincronizar si es de tipo DCR (puedes añadir más tipos separados por comas)
        if ticket['type'] in ['DCR']:
            headers = {
                "Authorization": f"token {self.gitea_token}",
                "Content-Type": "application/json"
            }
            payload = self._build_payload(ticket)

            try:
                print("ANTES DEL TRY (CREATE)")
                response = requests.post(self.gitea_url, json=payload, headers=headers, timeout=5)
                print(response)
                if response.status_code == 201:
                    self.log.info(f"Issue creada en Gitea para el ticket Trac #{ticket.id}")
                    print("HAS HECHO EL TRY (CREATE)")
                else:
                    self.log.error(f"Error al crear en Gitea: {response.text}")
            except Exception as e:
                self.log.error(f"Excepción conectando con Gitea (Create): {str(e)}")

    def ticket_changed(self, ticket, comment, author, old_values):
        # Se ejecuta cuando se modifica un ticket existente
        if ticket['type'] in ['DCR']:
            headers = {
                "Authorization": f"token {self.gitea_token}",
                "Content-Type": "application/json"
            }
            
            # 1. Buscamos si la issue ya existe en Gitea para ese ticket de Trac
            issue_number = self._find_gitea_issue_number(ticket.id, headers)
            payload = self._build_payload(ticket)

            try:
                print("ANTES DEL TRY (UPDATE)")
                if issue_number:
                    # Si ya existe, hacemos un PATCH para actualizarla
                    update_url = f"{self.gitea_url}/{issue_number}"
                    response = requests.patch(update_url, json=payload, headers=headers, timeout=5)
                    if response.status_code == 200:
                        self.log.info(f"Issue #{issue_number} actualizada en Gitea para el ticket Trac #{ticket.id}")
                        print("HAS HECHO EL TRY (UPDATE - EDITADA)")
                    else:
                        self.log.error(f"Error al actualizar issue en Gitea: {response.text}")
                else:
                    # Si por lo que sea no existía previa, la creamos al vuelo
                    response = requests.post(self.gitea_url, json=payload, headers=headers, timeout=5)
                    if response.status_code == 201:
                        self.log.info(f"Issue creada (desde update) en Gitea para el ticket Trac #{ticket.id}")
                        print("HAS HECHO EL TRY (UPDATE - NUEVA)")
            except Exception as e:
                self.log.error(fec=f"Excepción conectando con Gitea (Update): {str(e)}")

    def ticket_deleted(self, ticket):
        pass