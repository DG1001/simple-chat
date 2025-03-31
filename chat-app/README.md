# Echtzeit-Chat Anwendung

Eine einfache Web-Chat-Anwendung mit Flask und Socket.IO für Echtzeit-Kommunikation.

## Funktionen
- 📲 Echtzeit-Nachrichtenaustausch
- 👤 Benutzernamen-Eingabe beim Beitreten
- 📜 Anzeige der letzten 100 Nachrichten beim Beitreten
- 🔔 Benachrichtigungen bei Benutzer-Beitritt/Austritt
- 📁 Persistenter Nachrichtenverlauf (JSONL-Logdatei)

## Voraussetzungen
- Python 3.7+
- pip

## Installation
1. Repository klonen:
   ```bash
   git clone [Ihr-Repository-URL]
   cd chat-app
   ```

2. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```

## Verwendung
Anwendung starten:
```bash
python app.py
```

Öffnen Sie im Browser:
`http://localhost:5000`

## Konfiguration
Einstellungen können in `app.py` angepasst werden:
- `MAX_RECENT_MESSAGES`: Anzahl der angezeigten Nachrichten
- `LOG_FILE`: Pfad der Logdatei
- `SECRET_KEY`: Wird automatisch generiert

## Projektstruktur
```
chat-app/
├── app.py               # Hauptanwendung
├── requirements.txt     # Abhängigkeiten
├── README.md            # Diese Datei
└── templates/
    └── index.html       # Client-Seite
```

## Technologien
- **Flask** - Web Framework
- **Socket.IO** - Echtzeit-Kommunikation
- **JavaScript** - Client-Logik
- **HTML/CSS** - UI/UX

## Lizenz
[MIT](https://choosealicense.com/licenses/mit/) - Siehe [app.py](app.py) für Details

---

**Hinweis:** Diese Anwendung ist für Entwicklungszwecke gedacht. Für Produktionseinsatz sollten Sicherheitsmaßnahmen ergriffen werden.
