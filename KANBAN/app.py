from flask import Flask, render_template, url_for
from services.trac_tickets import get_all_tickets_trac

app = Flask(__name__)
@app.route("/")
def kanban():
    tickets = get_all_tickets()
    print('los coges')
    return render_template('index.html', tickets=tickets)

def get_all_tickets():
    trac_tickets = get_all_tickets_trac()

    return [trac_tickets]

