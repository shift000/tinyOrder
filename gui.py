import csv
from io import StringIO
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_session import Session
from db_funcs import debug_print_all, add_user, get_user_by_email, get_user_by_id, add_order, get_order, get_orders, get_orders_by_today, delete_order, get_item_name, get_items, hash_password, verify_password

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fetch_data_secret'
app.config['SESSION_TYPE'] = 'filesystem'  # Oder eine andere Methode zur Speicherung der Sessions
Session(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

def get_current_user():
    return get_user_by_email(current_user.id)

is_admin = lambda : get_current_user()['rank'] == 0
is_owner = lambda id : int(get_current_user()['uid']) == int(id)
curr_user_name = lambda : get_current_user()['name']
curr_user_uid = lambda : get_current_user()['uid']
user_by_id = lambda uid : get_user_by_id(uid)
        
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
@login_required
def index():
    if not get_current_user():
        return render_template('login.html', error="Bitte anmelden!")
    orders = get_orders()
    if not orders:
        orders = []
    else:
        temp = []
        for o in orders:
            #print(o["order"])
            temp.append({
                "id": o["oid"],
                "name": get_user_by_id(o["f_uid"])["name"],
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
        
        userdata = get_user_by_email(username)
        if userdata and verify_password(userdata["passwd"], password):
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        password2 = request.form['password2']

        # Überprüfen, ob die Passwörter übereinstimmen
        if password != password2:
            return render_template('register.html', error="Passwörter stimmen nicht überein.")
        
        # Überprüfen, ob die E-Mail bereits verwendet wird
        if get_user_by_email(email):
            return render_template('register.html', error="E-Mail ist bereits registriert.")
        
        # Neuen Benutzer erstellen
        add_user(email, name, hash_password(password), rank=2) # Standard-user-Rank = 2
        return redirect(url_for('login'))  # Nach erfolgreicher Registrierung zum Login umleiten

    return render_template('register.html')


@app.route('/order')
@login_required
def order():
    notification = "Bitte bis 11 Uhr bestellen!"
    
    entries = get_items()
    print(entries)
    
    return render_template('order.html', username=get_current_user()['name'], notification=notification, entries=entries)

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

@app.route('/make_order', methods=['GET', 'POST'])
@login_required
def make_order():
    if request.method == 'POST':
        anzahl = request.form.getlist('anzahl[]')
        ware = request.form.getlist('ware[]')
        extra = request.form['extra']
    
        # TODO : Zusammenzählen
        order = ""
        for i, a in enumerate(anzahl):
            line = f"{a}x {get_item_name(ware[i])['name']}, "
            order += line
        order = order[:-2]
    
        ret = add_order(curr_user_uid(), order, extra)
        if ret["sucess"]:
            flash(f'Bestellung {ret["id"]} erfolgreich', 'success')
            return redirect(url_for('index'))
        else:
            flash(f'Bestellung fehlgeschlagen. Es existiert bereits eine für heute!', 'failure')
            return redirect(url_for('index'))
    return render_template('order.html')

@app.route('/save_config')
@login_required
def save_config():
    return(index())

@app.route('/remove_order', methods=['POST'])
@login_required
def remove_order():
    if request.method == 'POST':
        data = request.get_json()
        order = get_order(data["id"])
        
        if is_owner(order["f_uid"]) or is_admin():
            if delete_order(order["oid"]):
                flash('Bestellung entfernt', 'sucess')
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'Fehler beim Entfernen der Bestellung'}), 666
        else:
            flash('Keine Berechtigung Bestellungen zu entfernen', 'error')
            return jsonify({'success': False, 'error': 'Fehler beim Entfernen der Bestellung'}), 403
    return jsonify({'success': False, 'error': 'Fehler..'}), 666
        

@app.route('/export_list')
def export_list():
    entries = get_orders_by_today()

    if not entries:
        flash(f'Export fehlgeschlagen. Es existiert noch keine Bestellung!', 'failure')
        return redirect(url_for('index'))
    # Gesamtübersicht der Bestellungen
    total_orders = {}
    user_orders = {}

    # Verarbeite alle Bestellungen
    for entry in entries:
        order_items = entry.get('order').split(', ')
        
        # Summiere die Bestellungen für die Gesamtübersicht
        for item in order_items:
            count, item_name = item.split('x ')
            count = int(count.strip())
            total_orders[item_name] = total_orders.get(item_name, 0) + count
        
        # Bestellungen nach Benutzer (f_uid) gruppieren
        f_uid = entry.get('f_uid')
        if f_uid not in user_orders:
            user_orders[f_uid] = []
        user_orders[f_uid].append(entry.get('order'))

    # Erstelle den Inhalt der Textdatei
    output = StringIO()

    # Schreibe die Gesamtübersicht in die Datei
    output.write("=== Gesamtbestellungen ===\n")
    for item_name, count in total_orders.items():
        output.write(f"{count}x {item_name}\n")

    # Schreibe die Bestellungen pro Benutzer in die Datei
    output.write("\n\n=== Bestellungen nach Benutzer ===\n")
    for f_uid, orders in user_orders.items():
        output.write(f"\nBenutzer {user_by_id(f_uid)['name']}:\n")
        for order in orders:
            output.write(f"- {order}\n")

    # Erstelle den Dateinamen basierend auf dem Datum der ersten Bestellung
    filename = entries[0].get('date').split(' ')[0].replace('.', '-') if entries else 'bestellungen'
    filename = f'bestellungen-{filename}.txt'

    # Setze den Stream-Zeiger auf den Anfang der Datei
    output.seek(0)

    # Gebe die Datei als Download zurück
    return Response(
        output.getvalue(),
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

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
    app.run(port=5001, debug=True)
