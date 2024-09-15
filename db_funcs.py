from tinydb import TinyDB, Query
from datetime import datetime
import os

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
    
    tables = ['user', 'orders']
    # user : uid, name, passwd, rank
    # orders : oid, f_uid, order, extra, date
    
    for t in tables:
        db.table(t).all()
        
    initialize_user()
    db.close()

def add_user(alias, name, passwd, rank):
    """Fügt einen neuen Benutzer hinzu."""
    db = TinyDB(DB_PATH)
    user_table = db.table('user')

    uid = 1
    if len(user_table) > 0:
        users = user_table.all()
        uid = int(max([user['uid'] for user in users])) + 1
        
    user_table.insert({
        'uid': uid,
        'alias': alias,
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
    return user if user else None

def get_user(alias):
    """Ruft einen Benutzer basierend auf der UID ab."""
    db = TinyDB(DB_PATH)
    user_table = db.table('user')
    
    UserQuery = Query()
    user = user_table.search(UserQuery.alias == alias)
    
    db.close()
    return user if user else None

def add_order(f_uid, order, extra):
    """Fügt eine neue Bestellung hinzu."""
    db = TinyDB(DB_PATH)
    orders_table = db.table('orders')
    
    oid = 1
    if len(orders_table) > 0:
        orders = orders_table.all()
        uid = int(max([order['oid'] for order in orders])) + 1
        
    orders_table.insert({
        'oid': oid,
        'f_uid': f_uid,  # Fremdschlüssel zur Benutzer-ID
        'order': order,
        'extra': extra,
        'date': datetime.now().strftime('%d.%m.%Y - %H:%M:%S')
    })
    
    db.close()

def get_order(oid):
    """Ruft eine Bestellung basierend auf der OID ab."""
    db = TinyDB(DB_PATH)
    orders_table = db.table('orders')
    
    OrderQuery = Query()
    order = orders_table.search(OrderQuery.oid == oid)
    
    db.close()
    return order if order else None

def get_orders():
    """Ruft alle Bestellungen aus der 'orders'-Tabelle ab."""
    db = TinyDB(DB_PATH)
    orders_table = db.table('orders')
    
    # Abrufen aller Bestellungen
    orders = orders_table.all()
    
    db.close()
    return orders if orders else None


def delete_order(oid):
    """Löscht eine Bestellung basierend auf der OID."""
    db = TinyDB(DB_PATH)
    orders_table = db.table('orders')
    
    OrderQuery = Query()
    orders_table.remove(OrderQuery.oid == oid)
    
    db.close()
    
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
    
    db.close()

def initialize_user():
    users = {
        'admin@admin.test': {'password': 'admin', 'name': 'Administrator', 'rank': 0},
        'test@test.test': {'password': 'test', 'name': 'Testuser', 'rank': 2},
        'markus.schaetzle@bpex.de': {'password': 'password', 'name': 'Markus Schätzle', 'rank': 1},
        
    }
    
    if not get_user(list(users.keys())[0]):
        for key, item in users.items():
            add_user(key, item["name"], item["password"], item["rank"])
        
        
        