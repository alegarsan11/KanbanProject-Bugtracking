from flask import Flask, render_template, url_for

app = Flask(__name__)
@app.route("/")
def kanban():
    return render_template('index.html')

def populate_mantis():

    return 
