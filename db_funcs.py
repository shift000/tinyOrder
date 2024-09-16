from tinydb import TinyDB, Query
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password):
    return generate_password_hash(password)
    
def verify_password(stored_password_hash, provided_password):
    return check_password_hash(stored_password_hash, provided_password)

def out(msg, title=""):
    print(f'{title}:: {msg}')

# Pfad zur TinyDB-Datenbank
DB_PATH = 'data/tinydb.json'

def initialize_db():
    if not os.path.exists('./data'):
        os.mkdir('./data')
    """Initialisiert die TinyDB-Datenbank und erstellt notwendige Tabellen."""
    db = TinyDB(DB_PATH)
    # Hier werden die Tabellen erstellt, wenn sie nicht existieren
    
    tables = ['user', 'orders', 'items']
    # user : uid, name, passwd, rank
    # orders : oid, f_uid, order, extra, date
    # items : iid, name
    
    for t in tables:
        db.table(t).all()
        
    initialize_user()
    initialize_items()
    db.close()

def add_user(email, name, passwd, rank):
    """Fügt einen neuen Benutzer hinzu."""
    db = TinyDB(DB_PATH)
    user_table = db.table('user')

    uid = 1
    if len(user_table) > 0:
        users = user_table.all()
        uid = int(max([user['uid'] for user in users])) + 1
        
    user_table.insert({
        'uid': uid,
        'email': email,
        'name': name,
        'passwd': passwd,
        'rank': rank,
        'date': datetime.now().strftime('%d.%m.%Y - %H:%M:%S')
    })
    
    db.close()

def get_user_by_id(uid):
    """Ruft einen Benutzer basierend auf der UID ab."""
    db = TinyDB(DB_PATH)
    user_table = db.table('user')
    
    UserQuery = Query()
    user = user_table.search(UserQuery.uid == uid)
    
    db.close()
    return user[0] if user else None

def get_user_by_email(email):
    """Ruft einen Benutzer basierend auf der UID ab."""
    db = TinyDB(DB_PATH)
    user_table = db.table('user')
    
    UserQuery = Query()
    user = user_table.search(UserQuery.email == email)
    
    db.close()
    return user[0] if user else None

def add_order(f_uid, order, extra):
    """Fügt eine neue Bestellung hinzu."""
    db = TinyDB(DB_PATH)
    orders_table = db.table('orders')
    
    if not get_orders_by_user_and_date(f_uid, datetime.now().strftime('%d.%m.%Y')):
        oid = 1
        if len(orders_table) > 0:
            orders = orders_table.all()
            oid = int(max([order['oid'] for order in orders])) + 1
            
        orders_table.insert({
            'oid': oid,
            'f_uid': f_uid,  # Fremdschlüssel zur Benutzer-ID
            'order': order,
            'extra': extra,
            'date': datetime.now().strftime('%d.%m.%Y - %H:%M:%S')
        })
        
        db.close()
        return {"success":True, "id": oid}
    return {"success":False}

def get_order(oid):
    """Ruft eine Bestellung basierend auf der OID ab."""
    db = TinyDB(DB_PATH)
    orders_table = db.table('orders')
    
    OrderQuery = Query()
    
    oid = int(oid)
    order = orders_table.search(OrderQuery.oid == oid)
    
    db.close()
    return order[0] if order else None

def get_orders():
    """Ruft alle Bestellungen aus der 'orders'-Tabelle ab."""
    db = TinyDB(DB_PATH)
    orders_table = db.table('orders')
    
    # Abrufen aller Bestellungen
    orders = orders_table.all()
    
    print(orders)
    
    db.close()
    return orders if orders else None

def get_orders_by_user_and_date(f_uid, search_date):
    """
    Ruft alle Bestellungen eines bestimmten Benutzers (f_uid) zu einem bestimmten Datum ab.
    
    :param f_uid: Die Benutzer-ID (fremder Schlüssel)
    :param search_date: Das gesuchte Datum im Format '%d.%m.%Y' (z.B. '15.09.2024')
    :return: Eine Liste von Bestellungen, die die Bedingungen erfüllen
    """
    db = TinyDB(DB_PATH)
    orders_table = db.table('orders')
    
    # Query-Objekt für die Suche
    OrderQuery = Query()
    
    # Suche nach Bestellungen mit passender f_uid und Datum (nur der Datumsteil)
    orders = orders_table.search((OrderQuery.f_uid == f_uid) & (OrderQuery.date.matches(f'^{search_date}')))
    
    db.close()
    
    return orders if orders else None

def get_orders_by_today():
    """
    Ruft alle Bestellungen eines bestimmten Benutzers (f_uid) für das heutige Datum ab.
    
    :param f_uid: Die Benutzer-ID (fremder Schlüssel)
    :return: Eine Liste von Bestellungen, die die Bedingungen erfüllen
    """
    db = TinyDB(DB_PATH)
    orders_table = db.table('orders')

    # Heutiges Datum im Format '%d.%m.%Y'
    today_date = datetime.now().strftime('%d.%m.%Y')
    
    # Query-Objekt für die Suche
    OrderQuery = Query()
    
    # Suche nach Bestellungen mit passender f_uid und dem heutigen Datum (nur der Datumsteil)
    orders = orders_table.search(OrderQuery.date.matches(f'^{today_date}'))
    
    db.close()
    
    return orders if orders else None

def delete_order(oid):
    """Löscht eine Bestellung basierend auf der OID."""
    db = TinyDB(DB_PATH)
    orders_table = db.table('orders')
    
    OrderQuery = Query()
    orders_table.remove(OrderQuery.oid == oid)
    
    db.close()
    return 1
    
def debug_print_all():
    """Gibt den gesamten Inhalt der Tabellen 'user' und 'orders' für Debug-Zwecke aus."""
    db = TinyDB(DB_PATH)
    
    # Inhalte der 'user'-Tabelle ausgeben
    user_table = db.table('user')
    users = user_table.all()
    print("User Table Contents:")
    if users:
        for user in users:
            print(user)
    else:
        print("No users found.")
    
    # Inhalte der 'orders'-Tabelle ausgeben
    orders_table = db.table('orders')
    orders = orders_table.all()
    print("\nOrders Table Contents:")
    if orders:
        for order in orders:
            print(order)
    else:
        print("No orders found.")
        
    # Inhalte der 'orders'-Tabelle ausgeben
    items_table = db.table('items')
    items = items_table.all()
    print("\nItems Table Contents:")
    if items:
        for item in items:
            print(item)
    else:
        print("No items found.")
    
    db.close()

def add_item(name):
    """Fügt einen neuen Benutzer hinzu."""
    db = TinyDB(DB_PATH)
    items_table = db.table('items')

    iid = 1
    if len(items_table) > 0:
        items = items_table.all()
        iid = int(max([item['iid'] for item in items])) + 1
        
    items_table.insert({
        'iid': iid,
        'name': name,
    })
    
    db.close()
    
def get_item(name):
    db = TinyDB(DB_PATH)
    items_table = db.table('items')
    
    # Query-Objekt für die Suche
    OrderQuery = Query()
    
    # Suche nach Bestellungen mit passender f_uid und dem heutigen Datum (nur der Datumsteil)
    item = items_table.search(OrderQuery.name == name)
    
    db.close()
    
    return item[0] if item else None

def get_items():
    """Ruft alle Einträge aus der 'items'-Tabelle ab."""
    db = TinyDB(DB_PATH)
    items_table = db.table('items')
    
    # Abrufen aller Bestellungen
    items = items_table.all()
    
    db.close()
    return items if items else None

def get_item_name(iid):
    db = TinyDB(DB_PATH)
    items_table = db.table('items')
    
    # Query-Objekt für die Suche
    OrderQuery = Query()
    
    # Suche nach Bestellungen mit passender f_uid und dem heutigen Datum (nur der Datumsteil)
    item = items_table.search(OrderQuery.iid == int(iid))
    
    db.close()
    
    return item[0] if item else None
    
def initialize_user():
    users = {
        'admin@test.de': {'password': 'admin', 'name': 'Administrator', 'rank': 0},
        'test@test.de': {'password': 'test', 'name': 'Testuser', 'rank': 2},
        'zusatz01@test.de': {'password': 'z01', 'name': 'Zusatz01', 'rank': 2},
        'zusatz02@test.de': {'password': 'z02', 'name': 'Zusatz02', 'rank': 2},
        'zusatz03@test.de': {'password': 'z03', 'name': 'Zusatz03', 'rank': 2},
        'zusatz04@test.de': {'password': 'z04', 'name': 'Zusatz04', 'rank': 2},
        'zusatz05@test.de': {'password': 'z05', 'name': 'Zusatz05', 'rank': 2},
    }
    
    if not get_user_by_email(list(users.keys())[0]):
        for key, item in users.items():
            add_user(key, item["name"], hash_password(item["password"]), item["rank"])

def initialize_items():
    items = ["Brezel", "Vollkornbrötchen", "Laugenecke", "Laugenweck", "Laugenstange", "Spitzweck", "Baguettebrötchen", "Miniwaldi", "Körnerbrötchen", "Kürbiskernbrötchen"]
    items.sort()
    
    for item in items:
        if not get_item(item):
            add_item(item)
        
        
        
        