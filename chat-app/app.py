import json
import os
from datetime import datetime
from collections import deque

from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room

# --- Konfiguration ---
MAX_RECENT_MESSAGES = 100  # Anzahl der Nachrichten, die beim Joinen angezeigt werden
LOG_FILE = "chat_log.jsonl" # Datei für den kompletten Chatverlauf (JSON Lines Format)
SECRET_KEY = os.urandom(24) # Wichtig für Flask Sessions (um Benutzernamen zu speichern)

# --- Initialisierung ---
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
# 'threading' Mode ist einfacher für den Anfang als eventlet/gevent
socketio = SocketIO(app, async_mode='threading') 

# In-Memory Speicher für die letzten Nachrichten (effizienter Zugriff)
# deque (double-ended queue) mit max. Länge ist ideal hierfür
recent_messages = deque(maxlen=MAX_RECENT_MESSAGES)

# --- Hilfsfunktionen ---
def load_recent_messages():
    """Lädt die letzten MAX_RECENT_MESSAGES aus der Log-Datei."""
    if not os.path.exists(LOG_FILE):
        return
    
    temp_deque = deque(maxlen=MAX_RECENT_MESSAGES)
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    # Jede Zeile ist ein separates JSON-Objekt
                    message = json.loads(line.strip())
                    temp_deque.append(message) # deque kümmert sich um die Längenbeschränkung
                except json.JSONDecodeError:
                    print(f"Warnung: Konnte Zeile nicht als JSON parsen: {line.strip()}")
        recent_messages.extend(list(temp_deque)) # Füllt unsere Haupt-Deque
        print(f"{len(recent_messages)} Nachrichten aus Log geladen.")
    except Exception as e:
        print(f"Fehler beim Laden der Log-Datei: {e}")

def log_message(message_data):
    """Schreibt eine Nachricht als JSON-Zeile in die Log-Datei."""
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            # Füge Zeitstempel hinzu, falls nicht vorhanden
            if 'timestamp' not in message_data:
                 message_data['timestamp'] = datetime.now().isoformat()
            f.write(json.dumps(message_data) + '\n')
    except Exception as e:
        print(f"Fehler beim Schreiben in die Log-Datei: {e}")

# --- Flask Route ---
@app.route('/')
def index():
    """Liefert die Haupt-HTML-Seite aus."""
    # Stellt sicher, dass die Session initialisiert ist (optional, aber gut für Klarheit)
    session.permanent = True 
    return render_template('index.html')

# --- SocketIO Event-Handler ---
@socketio.on('connect')
def handle_connect():
    """Wird aufgerufen, wenn ein neuer Client die Verbindung herstellt."""
    print(f"Client verbunden: {request.sid}")
    # Noch keine Aktion hier, Nutzer muss erst Namen eingeben

@socketio.on('disconnect')
def handle_disconnect():
    """Wird aufgerufen, wenn ein Client die Verbindung trennt."""
    username = session.get('username', 'Unbekannt')
    print(f"Client getrennt: {username} ({request.sid})")
    # Informiere andere User, dass jemand gegangen ist (optional)
    if username != 'Unbekannt':
        notification = {
            'type': 'notification',
            'text': f"{username} hat den Chat verlassen."
        }
        emit('message', notification, broadcast=True)
        log_message(notification) # Optional auch das loggen
    # Session-Daten für diesen Client werden automatisch aufgeräumt

@socketio.on('user_joined')
def handle_user_joined(data):
    """Wird aufgerufen, wenn ein Benutzer seinen Namen angibt."""
    username = data.get('username')
    if not username:
        print(f"Warnung: Client {request.sid} hat keinen Namen gesendet.")
        return # Ignoriere leere Namen

    session['username'] = username # Speichere Namen in der Session für diese Verbindung
    print(f"Benutzer beigetreten: {username} ({request.sid})")

    # Sende die letzten Nachrichten NUR an den neuen Benutzer
    emit('chat_history', list(recent_messages)) 

    # Informiere ALLE ANDEREN über den neuen Benutzer
    join_notification = {
        'type': 'notification',
        'text': f"{username} hat den Chat betreten."
    }
    # broadcast=True sendet an alle, include_self=False verhindert, dass der Sender es doppelt bekommt
    emit('message', join_notification, broadcast=True, include_self=False) 
    log_message(join_notification) # Logge den Beitritt


@socketio.on('new_message')
def handle_new_message(data):
    """Wird aufgerufen, wenn ein Benutzer eine neue Nachricht sendet."""
    username = session.get('username')
    message_text = data.get('text')

    if not username:
        print(f"Warnung: Nachricht von nicht identifiziertem Client {request.sid} empfangen.")
        return # Nur eingeloggte Nutzer können senden

    if not message_text:
        print(f"Warnung: Leere Nachricht von {username} empfangen.")
        return # Keine leeren Nachrichten senden

    message_data = {
        'type': 'user_message',
        'user': username,
        'text': message_text,
        'timestamp': datetime.now().isoformat() # Zeitstempel hinzufügen
    }

    # Füge zur In-Memory Liste hinzu (für neue Joins)
    recent_messages.append(message_data) 
    
    # Logge die Nachricht in die Datei
    log_message(message_data)

    # Sende die Nachricht an ALLE verbundenen Clients (einschließlich Sender)
    emit('message', message_data, broadcast=True)
    print(f"Nachricht von {username}: {message_text}")

# --- App Start ---
if __name__ == '__main__':
    load_recent_messages() # Lade Verlauf beim Start
    print("Starte SocketIO Server...")
    # Host 0.0.0.0 macht den Server im lokalen Netzwerk erreichbar
    # Debug=True ist nützlich während der Entwicklung (automatischer Neustart bei Änderungen)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=True) 
