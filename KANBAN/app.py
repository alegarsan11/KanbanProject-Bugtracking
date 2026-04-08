from flask import Flask, render_template, url_for
from services.trac_tickets import get_all_tickets_trac
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
@app.route("/")
def kanban():
    tickets  = get_all_tickets()

    return render_template('index.html', tickets=tickets)

def get_all_tickets():
    ticketsTrac  = get_all_tickets_trac()
    tickets = {'New':[],
    'In-Progress':[],
    'Done':[],
    'On-HOLD':[]}    
    for i in ticketsTrac:
        print(i[0])
        if i[3]['status'] == 'new':
            tickets['New'].append(i)
        elif i[3]['status'] == 'accepted':
            tickets['In-Progress'].append(i)
        else:
            tickets['Done'].append(i)
    return tickets

scheduler = BackgroundScheduler()
scheduler.add_job(func=get_all_tickets, trigger="interval", seconds=300) # Recargamos por nuevos tickets cada 5 minutos
scheduler.start()