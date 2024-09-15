import csv
from io import StringIO
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_session import Session
from db_funcs import debug_print_all, add_user, get_user, get_user_by_id, add_order, get_order, get_orders, delete_order

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Wähle einen sicheren Schlüssel
app.config['SESSION_TYPE'] = 'filesystem'  # Oder eine andere Methode zur Speicherung der Sessions
Session(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

def get_current_user():
    return get_user(current_user.id)[0]

is_admin = lambda : get_current_user()['rank'] == 0
is_owner = lambda id : get_current_user()['uid'] == id
        
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route('/')
@login_required
def index():
    #debug_print_all()
    entries = [
        {'name': 'Max Mustermann', 'bestellung': '2x Laugenweck, 1x Körnerweck', 'anmerkung': 'Hallo bitte mit Soße'},
        {'name': 'Erika Mustermann', 'bestellung': '3x Brötchen', 'anmerkung': 'Ohne Butter'}
    ]
    orders = get_orders()
    if not orders:
        orders = []
    else:
        temp = []
        for o in orders:
            temp.append({
                "name": get_user_by_id(o["f_uid"])[0]["name"],
                "order": o["order"],
                "extra": o["extra"]
            })
        orders = temp
        
    return render_template('index.html', entries=orders, username=get_current_user()['name'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        userdata = get_user(username)
        if userdata and userdata[0]["passwd"] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        return render_template('login.html', error="Falsches Passwort/Username")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/order')
@login_required
def order():
    return render_template('order.html', username=get_current_user()['name'])

@app.route('/config')
@login_required
def config():
    if not is_admin():
        flash('Keine Berechtigung die Einstellungen zu sehen', 'error')
        return redirect(url_for('index'))
    else:
        return render_template('config.html', username=get_current_user()['name'])

@app.route('/configure_items')
@login_required
def configure_items():
    if not is_admin():
        flash('Keine Berechtigung etwas zu konfigurieren', 'error')
        return redirect(url_for('index'))
    else:
        return render_template('configure_items.html', username=get_current_user()['name'])

@app.route('/make_order')
@login_required
def make_order():
    user = get_current_user()['uid']
    order = ""
    extra = "xx"
    
    anzahl = request.form.getlist('anzahl[]')
    ware = request.form.getlist('ware[]')
    extra = request.form.get('extra')
    
    print(anzahl, ware, extra)
    
    add_order(user, order, extra)
    flash('Bestellung erfolgreich', 'success')
    return redirect(url_for('index'))

@app.route('/save_config')
@login_required
def save_config():
    return(index())

@app.route('/remove_order', methods=['POST'])
@login_required
def remove_order():
    data = request.get_json()
    print(">> ", data)
    
    if is_owner(0) or is_admin():
        
        #row_id = data.get('id')
        
        # Hier solltest du Logik hinzufügen, um die Bestellung basierend auf der ID zu entfernen.
        # Zum Beispiel:
        # success = remove_order_from_database(row_id)
        
        # Dummy-Response zur Veranschaulichung
        success = True  # Setze dies auf False, wenn die Löschung fehlschlägt
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Fehler beim Entfernen der Bestellung'}), 666
    else:
        flash('Keine Berechtigung Bestellungen zu entfernen', 'error')
        return jsonify({'success': False, 'error': 'Fehler beim Entfernen der Bestellung'}), 403
        

@app.route('/export_list')
def export_list():
    """entries = get_time_entries()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Aufgabe', 'Projekt', 'Dauer', 'Startzeit', 'Endzeit', 'Datum'])

    filename = ''
    
    for entry in entries:
        writer.writerow([
            entry.get('task'),
            entry.get('project'),
            entry.get('duration'),
            entry.get('start_time'),
            entry.get('end_time'),
            entry.get('date')
        ])
        if not filename:
            filename = entry.get('date')
            filename = f'tasklist-{filename.replace(".", "-")}.csv'
    
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )"""
    return(index())

@app.route('/get_entry', methods=['GET'])
def get_entry():
    # Beispiel: Datum als Parameter abrufen
    date = request.args.get('date')
    # Hier würdest du die Logik für das Abrufen der Tagesinformationen einfügen.
    # Dies ist nur ein Beispiel-Response.
    entry_info = {
        'date': date,
        'title': 'Beispiel Eintrag',
        'description': 'Dies sind die Details für den ausgewählten Tag.',
        # Weitere Informationen können hier hinzugefügt werden
    }
    return jsonify(entry_info)

def start_gui():
    app.run(debug=True)
