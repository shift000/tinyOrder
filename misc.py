from datetime import datetime

def format_time(timestamp):
    """Formatiert einen Zeitstempel für die Anzeige."""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
