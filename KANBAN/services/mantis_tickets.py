import os
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from zeep import Client
from dotenv import load_dotenv

# =========================
# LOAD ENV
# =========================
load_dotenv()

BASE_URL = os.getenv("MANTIS_URL")
USERNAME = os.getenv("MANTIS_USER")
PASSWORD = os.getenv("MANTIS_PASS")


# =========================
# 1. SOAP API
# =========================
def get_tickets_soap():
    print("\n--- SOAP API ---")

    wsdl = f"{BASE_URL}/api/soap/mantisconnect.php?wsdl"
    client = Client(wsdl=wsdl)

    issues = client.service.mc_project_get_issues(
        USERNAME,
        PASSWORD,
        1,      # project_id
        1,      # page
        50      # per_page
    )

    tickets = []

    for issue in issues:
        ticket = {
            "id": str(issue.id),
            "summary": issue.summary,
            "status": issue.status.name,
            "description": getattr(issue, "description", ""),
            "project": "mantis_project_1",
            "source": "mantis_soap",
            "url": f"{BASE_URL}/view.php?id={issue.id}"
        }
        tickets.append(ticket)

    return tickets


# =========================
# 2. REST API
# =========================
def get_tickets_rest():
    print("\n--- REST API ---")

    url = f"{BASE_URL}/api/rest/issues"
    response = requests.get(
        url,
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        headers={"Accept": "application/json"}
    )

    if response.status_code != 200:
        raise Exception(f"REST error: {response.status_code} - {response.text}")

    data = response.json()
    tickets = []

    for issue in data.get("issues", []):
        ticket = {
            "id": str(issue["id"]),
            "summary": issue["summary"],
            "status": issue["status"]["name"] if isinstance(issue["status"], dict) else issue["status"],
            "description": issue.get("description", ""),
            "project": "mantis_project_1",
            "source": "mantis_rest",
            "url": f"{BASE_URL}/view.php?id={issue['id']}"
        }
        tickets.append(ticket)

    return tickets


# =========================
# 3. WEB SCRAPING
# =========================
def get_tickets_scraping():
    print("\n--- SCRAPING ---")

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

        bug_id = cols[3].text.strip()

        ticket = {
            "id": bug_id,
            "summary": cols[10].text.strip(),
            "status": cols[8].text.strip(),
            "description": "",
            "project": "mantis_scraped",
            "source": "mantis_scraping",
            "url": f"{BASE_URL}/view.php?id={bug_id}"
        }

        tickets.append(ticket)

    return tickets


# =========================
# MAIN
# =========================
if __name__ == "__main__":

    try:
        soap = get_tickets_soap()
        print(f"SOAP tickets: {len(soap)}")
    except Exception as e:
        print("SOAP error:", e)

    try:
        rest = get_tickets_rest()
        print(f"REST tickets: {len(rest)}")
    except Exception as e:
        print("REST error:", e)

    try:
        scraped = get_tickets_scraping()
        print(f"SCRAPED tickets: {len(scraped)}")
    except Exception as e:
        print("Scraping error:", e)