
import csv
from io import StringIO
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_session import Session
from db_funcs import debug_print_all, add_user, get_user_by_email, get_user_by_id, get_users, add_order, get_order, get_orders, get_orders_by_today, delete_order, get_item_name, get_items, hash_password, verify_password, get_db
import config as app_config
import msal
from postbox import Postbox

app = Flask(__name__)
app.config.from_object(app_config.Config)
app.secret_key = app_config.secret_key
Session(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

def get_current_user():
    return get_user_by_email(current_user.id)


SETTINGS = {
    "de":{
    # LINKS & BUTTONS
    "link_index": "Startseite",
    "link_order": "Bestellen",
    "link_profile": "Profil",
    "link_feedback": "Feedback",
    "link_settings": "Einstellungen",
    "link_logout": "Abmelden",
    
    "btn_cancel": "Abbrechen",
    "btn_submit": "Speichern",
    "btn_change_avatar": "Avatar ändern",
    "btn_delete_avatar": "Avatar löschen",
    "btn_change_pwd": "Passwort ändern",
    
    "btn_profile": "Profil",
    "btn_feedback": "Feedback geben",
    "btn_accounts": "Einstellungen",
    "btn_logout": "Abmelden",
    
    "btn_add_row": "+ Zeile hinzufügen",
    "btn_remove_row": "Entfernen",
    
    # ALLGEMEIN
    "last_updates": "Aktuelles",
    "headline": "tinyOrder",
    "notification": "Bitte bis 11 Uhr bestellen!",
    "error": "",
    "success": "",
    
    # SEITE:INDEX
    "ix_title": "Übersicht",
    "ix_remove_row": "Bestellung entfernen",
    "ix_order_proc": "45",
    "ix_order_proc_text": "Bisher haben 6 von 15 bestellt..",
    
    # SEITE:PROFILE
    "my_title": "Kontoeinstellungen",
    "my_img": "026m.jpg",
    "my_account": "Mein Konto",
    "my_orders": "Meine Bestellungen",
    "my_settings": "Einstellungen",
    "my_experience": "Erfahrungen",
    "my_feedback": "Feedback geben",
    "my_account_title": "Mein Konto",
    "my_pwd": "Passwort",
    "my_pwd_noti": "Hier können Sie Ihr Passwort ändern",
    "my_lang_title": "Meine Sprache",
    "my_lang_de": "Deutsch",
    "my_lang_en": "Englisch",
    "accounts": "Kontoeinstellungen",
    "profile_details": "Profileinstellungen",
    
    # SEITE:ORDER
    "od_title": "Bestellung",
    "od_desc": "Bitte wählen Sie Ihre Artikel aus.",
    "od_checkout": "Einkaufsliste",
    "od_checkout_list": "Hier erscheint Ihre Einkaufsliste",
    "od_extra_title": "Anmerkungen",
    "od_extra_placeholder": "Z. B. Extra Soße",
    
    # SEITE:FEEDBACK
    "fb_title": "Feedback",
    "fb_card_title": "Dein Feedback",
    "fb_card_desc": "Hinterlasse uns hier dein Feedback",
    "fb_card_textbox_title": "Nachricht",
    "fb_card_textbox_placeholder": "Deine Nachricht hier eingeben",
    "fb_card_submit": "Absenden",
    
    # COPYRIGHT
    "copy_copy": "Copyright &copy; 2023",
    "copy_author": "shift000",
    "copy_version": "v1.0.0-beta19"
    },
    "en":{
    # LINKS & BUTTONS TODO:
    "link_index": "Home",
    "link_order": "Order",
    "link_profile": "Profile",
    "link_feedback": "Feedback",
    "link_settings": "Settings",
    "link_logout": "Logout",
    
    "btn_cancel": "Cancel",
    "btn_submit": "Save",
    "btn_change_avatar": "Change Avatar",
    "btn_delete_avatar": "Delete Avatar",
    "btn_change_pwd": "Change Password",
    
    "btn_profile": "Profile",
    "btn_feedback": "Give Feedback",
    "btn_accounts": "Settings",
    "btn_logout": "Logout",
    
    "btn_add_row": "+ Add Row",
    "btn_remove_row": "Remove",
    
    # GENERAL
    "last_updates": "Latest Updates",
    "headline": "tinyOrder",
    "notification": "Bitte bis 11 Uhr bestellen!",
    "error": "",
    "success": "",
    
    # PAGE: INDEX
    "ix_title": "Overview",
    "ix_remove_row": "Remove Order",
    "ix_order_proc": "45",
    "ix_order_proc_text": "So far 6 out of 15 have ordered..",
    
    # PAGE: PROFILE
    "settings": "Settings",
    "my_title": "Account Settings",
    "my_img": "026m.jpg",
    "my_account": "My Account",
    "my_orders": "My Orders",
    "my_settings": "Configuration",
    "my_experience": "Experience",
    "my_feedback": "Give Feedback",
    "my_account_title": "My Account",
    "my_pwd": "Password",
    "my_pwd_noti": "You can change your password here",
    "my_lang_title": "My Language",
    "my_lang_de": "German",
    "my_lang_en": "English",
    "accounts": "Account Settings",
    "profile_details": "Profile Settings",
    
    # PAGE: ORDER
    "od_title": "Order",
    "od_desc": "Please select your items.",
    "od_checkout": "Shopping List",
    "od_checkout_list": "Your shopping list will appear here",
    "od_extra_title": "Remarks",
    "od_extra_placeholder": "E.g., extra sauce",
    
    # PAGE: FEEDBACK
    "fb_title": "Feedback",
    "fb_card_title": "Your Feedback",
    "fb_card_desc": "Feel free to leave your feedback here",
    "fb_card_textbox_title": "Message",
    "fb_card_textbox_placeholder": "Enter your message here",
    "fb_card_submit": "Submit",
    
    # COPYRIGHT
    "copy_copy": "Copyright &copy; 2023",
    "copy_author": "shift000",
    "copy_version": "v1.0.0-beta19"
    }
}

LANGUAGE = [
    {
        "lang": "de",
        "act": True
    },
    {
        "lang": "en",
        "act": False
    }
]

is_admin = lambda : get_current_user()['rank'] == 0
is_owner = lambda iid : int(get_current_user()['uid']) == int(iid)
curr_user_name = lambda : get_current_user()['name']
curr_user_uid = lambda : get_current_user()['uid']
curr_language = lambda:[e["lang"] for e in LANGUAGE if e["act"] == True][0]
user_by_id = lambda uid : get_user_by_id(uid)

# === M365 als SingleSignOn ===
def build_msal_app():
    return msal.ConfidentialClientApplication(
        app.config["CLIENT_ID"], authority=app.config["AUTHORITY"],
        client_credential=app.config["CLIENT_SECRET"])


def build_auth_url():
    return build_msal_app().get_authorization_request_url(
        app.config["SCOPE"],
        redirect_uri=url_for("authorized", _external=True))
        
@app.route(app.config["REDIRECT_PATH"])
def authorized():
    if request.args.get('code'):
        result = build_msal_app().acquire_token_by_authorization_code(
            request.args['code'],
            scopes=app.config["SCOPE"],
            redirect_uri=url_for("authorized", _external=True))
        if "access_token" in result:
            session["user"] = result.get("id_token_claims")
    return redirect(url_for("index"))
# ===

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def get_news():
    # news = get_news(user)
    news = [
        {
            "title": "Service-Info",
            "message": "Essen ist da!",
            "status_good": True
        },
        {
            "title": "Nicht erfüllbar",
            "message": "Bestellung 001-23-42 nicht verfügbar",
            "status_bad": True
        },
        {
            "title": "[INFO] System",
            "message": "System-Nachricht",
        },
    ]
    return news

# ==== INDEX
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
            print(o)
            temp.append({
                "id": o["oid"],
                "order_no": o["oid"],
                "name": user_by_id(o["f_uid"])["name"],
                "order": o["order"],
                "extra": o["extra"],
                "timestamp": o["stamp"]
            })
        orders = temp
    
    userUids = [e["uid"] for e in get_users()]
    all_uids = len(userUids)
    for e in orders:
        if e["id"] in userUids:
            userUids.remove(e["id"])
    no_order_uids = len(userUids)
    
    SETTINGS[curr_language()]["ix_order_proc"] = (100/all_uids)*(all_uids-no_order_uids)
    SETTINGS[curr_language()]["ix_order_proc_text"] = f"Bisher haben {all_uids-no_order_uids} von {all_uids} bestellt.."
    
    return render_template('index.html', news=get_news(), config=SETTINGS[curr_language()], orders=orders, email=get_current_user()['email'], username=get_current_user()['name'], rank=get_current_user()['rank'])

# ==== LOGIN / LOGOUT / REGISTER
@app.route('/login', methods=['GET', 'POST'])
def login():
    if not app_config.login_by_sso:
        lang = "de"
        login_data = {
            "de": {
                "headline": "Login",
                "email": "Deine E-Mail",
                "password": "Dein Passwort",
                "forgot": "Passwort vergessen?",
                "email_placeholder": "max@mustermann.de",
                "pass_placeholder": "********",
                "remember": "Angemeldet bleiben",
                "sign_in": "Anmelden",
                "no_account": "Noch kein Konto?",
                "register": "Registrieren"
            },
            "en": {
                "headline": "Login",
                "email": "Your Email",
                "password": "Your Password",
                "forgot": "Forgot Password?",
                "email_placeholder": "john@doe.com",
                "pass_placeholder": "********",
                "remember": "Remember Me",
                "sign_in": "Sign In",
                "no_account": "No account yet?",
                "register": "Register"
            }
        }
    
        if request.method == 'POST':
            data = {
                "email": request.form['email'],
                "password": request.form['password'],
            }
            try:
                data["remember_user"] = request.form['remember']
            except KeyError:
                data["remember_user"] = "off"
            
            userdata = get_user_by_email(data["email"])
            if userdata and verify_password(userdata["passwd"], data["password"]):
                login_user(User(data["email"]))
                return redirect(url_for('index'))
            return render_template('login.html', login=login_data[lang], error="Falsches Passwort/Username")
    
        return render_template('login.html', login=login_data[lang])
    else:
        return redirect(build_auth_url())

@app.route('/logout')
@login_required
def logout():
    if not app_config.login_by_sso:
        logout_user()
        flash('Erfolgreich abgemeldet!', 'success')
        return redirect(url_for('login'))
    else:
        session.clear()
        return redirect(
            app.config["AUTHORITY"] + "/oauth2/v2.0/logout" +
            f"?post_logout_redirect_uri={url_for('index', _external=True)}"
        )

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

# Route für die Konfigurationsseite
@app.route('/conf', methods=['GET', 'POST'])
@login_required
def conf():
    db = get_db()
    items_table = db.table('items')

    # POST-Anfrage: Eintrag hinzufügen, bearbeiten oder löschen
    if request.method == 'POST':
        if 'delete' in request.form:
            item_id = request.form['delete']
            items_table.remove(Query().id == int(item_id))
            flash('Eintrag erfolgreich gelöscht', 'success')
        elif 'edit' in request.form:
            item_id = request.form['edit']
            new_name = request.form.get('name')
            items_table.update({'name': new_name}, Query().id == int(item_id))
            flash('Eintrag erfolgreich geändert', 'success')
        elif 'add' in request.form:
            new_name = request.form.get('name')
            item_id = len(items_table) + 1  # einfache ID-Zuordnung
            items_table.insert({'id': item_id, 'name': new_name})
            flash('Eintrag erfolgreich hinzugefügt', 'success')
        return redirect(url_for('config'))

    # GET-Anfrage: Alle Einträge anzeigen
    items = items_table.all()
    db.close()

    return render_template('conf.html', items=items)

# ==== ORDER / MAKE_ORDER / CONFIGURE_ORDERS / REMOVE_ORDER / EXPORT_ORDERS
@app.route('/order')
@login_required
def order():
    entries = get_items()
    return render_template('order.html', config=SETTINGS[curr_language()], username=get_current_user()['name'], email=get_current_user()['email'], entries=entries)

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
        if ret["success"]:
            SETTINGS[curr_language()]["success"] = f'Bestellung {ret["id"]} erfolgreich'
            return redirect(url_for('index'))
        else:
            SETTINGS[curr_language()]["error"] = f'Bestellung fehlgeschlagen. Es existiert bereits eine für heute!'
            return redirect(url_for('index'))
    return render_template('order.html')

@app.route('/configure_items')
@login_required
def configure_items():
    if not is_admin():
        flash('Keine Berechtigung etwas zu konfigurieren', 'error')
        return redirect(url_for('index'))
    else:
        return render_template('configure_items.html', username=get_current_user()['name'])

@app.route('/remove_order', methods=['POST'])
@login_required
def remove_order():
    if request.method == 'POST':
        data = request.get_json()
        order = get_order(data["id"])
        
        if is_owner(order["f_uid"]) or is_admin():
            if delete_order(order["oid"]):
                SETTINGS[curr_language()]["success"] = 'Bestellung entfernt'
                return jsonify({'success': True})
            else:
                SETTINGS[curr_language()]["error"] = 'Fehler beim Entfernen der Bestellung'
                return jsonify({'success': False, 'error': 'Fehler beim Entfernen der Bestellung'}), 666
        else:
            SETTINGS[curr_language()]["error"] = 'Keine Berechtigung Bestellungen zu entfernen'
            return jsonify({'success': False, 'error': 'Fehler beim Entfernen der Bestellung'}), 403
    return jsonify({'success': False, 'error': 'Fehler..'}), 666

@app.route('/export_list')
def export_list():
    print(debug_print_all())
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
        user_orders[f_uid].append({"order": entry.get('order'), "extra": entry.get('extra')})

    # Erstelle den Inhalt der Textdatei
    output = StringIO()

    # Schreibe die Gesamtübersicht in die Datei
    output.write("=== Gesamtbestellungen ===\n")
    for item_name, count in total_orders.items():
        output.write(f"{count}x {item_name}\n")

    # Schreibe die Bestellungen pro Benutzer in die Datei
    output.write("\n\n=== Bestellungen nach Benutzer ===\n")
    for f_uid, data in user_orders.items():
        output.write(f"\nBenutzer {user_by_id(f_uid)['name']}:\n")
        data = data[0]
        for order in data["order"].split(","):
            output.write(f"- {order.strip()}\n")
        if data["extra"]:
            output.write(f'Anmerkung: {data["extra"]}\n')
        

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

# ==== CONFIG_PROFILE, SEND_FEEDBACK, SAVE_CONFIG, PROFILE, SETTINGS, SAVE_SETTINGS
@app.route('/config')
@login_required
def config():
    if not is_admin():
        flash('Keine Berechtigung die Einstellungen zu sehen', 'error')
        return redirect(url_for('index'))
    else:
        return render_template('config.html', username=get_current_user()['name'])

@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    if request.method == 'POST':
        setts = SETTINGS[curr_language()]
        for k, i in SETTINGS.items():
            setts[k] = i
        
        setts["fb_card_textbox_placeholder"] = request.form['feedback']
        return render_template('feedback.html', config=setts, username=get_current_user()['name'])
    return render_template('feedback.html', config=SETTINGS[curr_language()], username=get_current_user()['name'], email=get_current_user()['email'])
    
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', news=get_news(), config=SETTINGS[curr_language()], username=get_current_user()['name'])
    
@app.route('/save_config', methods=['GET', 'POST'])
@login_required
def save_config():
    if request.method == 'POST':
        # Change Language
        lang = request.form.getlist('lang[]')[0]
        curr = curr_language()
        
        if lang != curr:
            for i, entry in enumerate(LANGUAGE):
                print(i, entry, lang, entry["lang"] == lang)
                if entry["lang"] == curr:
                    LANGUAGE[i]["act"] = False
                    print(LANGUAGE[i]["lang"], "zu False")
                elif entry["lang"] == lang:
                    LANGUAGE[i]["act"] = True
                    print(entry["lang"], "zu True")
                print(i, entry, lang, entry["lang"] == lang)
            print(LANGUAGE)
            
    return render_template('profile.html', config=SETTINGS[curr_language()], username=get_current_user()['name'], language=LANGUAGE)

# ==== EXT
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
    app.run(port=5002, debug=False)
