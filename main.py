from gui import start_gui
from db_funcs import initialize_db

def main():
    # Initialisiere die Datenbank
    initialize_db()
    
    # Starte die GUI
    start_gui()

if __name__ == "__main__":
    main()
