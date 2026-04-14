import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from zeep import Client

BASE_URL = "http://localhost:8989"
USERNAME = "administrator"
PASSWORD = "root"   # change this

# =========================
# 1. SOAP API (xmlrpc/soap)
# =========================
def get_tickets_soap():
    print("\n--- SOAP API ---")

    wsdl = f"{BASE_URL}/api/soap/mantisconnect.php?wsdl"
    client = Client(wsdl=wsdl)

    # Get issues (project_id = 1, adjust if needed)
    issues = client.service.mc_project_get_issues(
        USERNAME,
        PASSWORD,
        1,      # project_id
        1,      # page
        50      # per_page
    )

    for issue in issues:
        print(f"ID: {issue.id}")
        print(f"Summary: {issue.summary}")
        print(f"Status: {issue.status.name}")
        print("-" * 30)

    return issues


# =========================
# 2. REST API
# =========================
def get_tickets_soap():
    wsdl = f"{BASE_URL}/api/soap/mantisconnect.php?wsdl"
    client = Client(wsdl=wsdl)

    issues = client.service.mc_project_get_issues(
        USERNAME, PASSWORD, 1, 1, 50
    )

    tickets = []

    for issue in issues:
        ticket = {
            "id": str(issue.id),
            "summary": issue.summary,
            "status": issue.status.name,
            "description": getattr(issue, "description", ""),
            "project": "mantis_project_1",
            "source": "mantis_soap"
        }

        tickets.append(ticket)

    return tickets

# =========================
# 3. Web Scraping
# =========================
def get_tickets_scraping():
    session = requests.Session()

    login_url = f"{BASE_URL}/login.php"
    session.post(login_url, data={
        "username": USERNAME,
        "password": PASSWORD
    })

    issues_url = f"{BASE_URL}/view_all_bug_page.php"
    response = session.get(issues_url)

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("table tbody tr")

    tickets = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 11:
            continue

        ticket = {
            "id": cols[3].text.strip(),
            "summary": cols[10].text.strip(),
            "status": cols[8].text.strip(),
            "description": "",  # not available here
            "project": "mantis_scraped",
            "source": "mantis_scraping"
        }

        tickets.append(ticket)

    return tickets


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    try:
        get_tickets_soap()
    except Exception as e:
        print("SOAP error:", e)

    try:
        get_tickets_rest()
    except Exception as e:
        print("REST error:", e)

    try:
        get_tickets_scraping()
    except Exception as e:
        print("Scraping error:", e)