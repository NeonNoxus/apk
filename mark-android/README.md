# Mark Assistant – Android-Port von Mark LIII

Dieses Projekt ist eine **Neuentwicklung** in Kivy/Python, inspiriert vom
Desktop-Assistenten "Mark LIII", angepasst an das, was auf Android technisch
möglich und sinnvoll ist.

## Was ist anders als im Original – und warum

| Original (Desktop) | Hier (Android) | Grund |
|---|---|---|
| Gemini **Live**-API, Audio-Streaming | Text-Chat + lokale Sprach-Ein-/Ausgabe (Android STT/TTS) | Live-WebSocket-Streaming im Hintergrund ist auf Android deutlich instabiler (Verbindungsabbrüche, Akku, Background-Limits). Fühlt sich für den Nutzer fast gleich an. |
| Wake-Word "Hey Jarvis" | entfällt (Ausbaustufe 2) | Dauerhaftes Mikrofon-Zuhören im Hintergrund ist auf modernen Android-Versionen stark eingeschränkt und verbraucht viel Akku. |
| Windows-Registry / macOS-/Linux-Systemsteuerung, `pyautogui` | entfällt | Android sandboxt Apps bewusst – kein Zugriff auf andere Apps, keine Maus-/Tastatursteuerung des Systems. |
| Taskleiste/Desktop-Steuerung, Spiele-Updater (Steam/Epic) | entfällt | Ergibt auf einem Handy keinen Sinn / ist technisch nicht erreichbar. |
| Browser-Fernsteuerung | nur "Link öffnen" | Android-Apps können keine fremde Browser-Instanz fernsteuern. |
| Freie Dateisystem-Zugriffe | Nur Dateien, die der Nutzer per System-Dialog freigibt | Android "Scoped Storage" (seit Android 10+) erlaubt keinen freien Zugriff mehr. |
| Beliebige OS-Benachrichtigungs-Scheduler | Android `AlarmManager` + Benachrichtigung | Android-Äquivalent für "Erinnerungen". Ab Android 12 muss der Nutzer die Exact-Alarm-Berechtigung selbst erlauben. |

Enthalten und funktionsfähig: Chat mit Gemini (inkl. Tool-Calling), persistentes
Gedächtnis mit Recall, Wetter, Websuche (news/research/price/compare), Code-
Helfer, Datei-Zusammenfassung, Clipboard-Intelligenz (Übersetzen/
Zusammenfassen/Erklären/Fixen), Einstellungen (API-Key, Namen, Farbe).

## APK bauen – ohne irgendetwas selbst zu installieren

Ich kann in meiner Umgebung keine echte `.apk` erzeugen (das Android SDK/NDK,
das Buildozer dafür braucht, liegt auf Servern, zu denen ich keinen Zugriff
habe). Deshalb ist hier eine **GitHub-Actions-Pipeline** dabei
(`.github/workflows/build-apk.yml`), die das automatisch für dich übernimmt:

1. Erstelle ein neues (privates oder öffentliches) Repository auf GitHub.
2. Lade den kompletten Inhalt dieses Ordners dort hoch (z. B. per
   "Upload files" im Browser, oder `git push`).
3. Gehe im Repo auf den Tab **Actions** → Workflow **"Build Android APK"** →
   **Run workflow**. (Er startet auch automatisch bei jedem Push auf `main`.)
4. Nach ca. 15–25 Minuten (der erste Build lädt das Android-SDK/NDK herunter)
   erscheint unten ein Artefakt **"mark-assistant-apk"** zum Download – das
   ist deine fertige APK.
5. APK aufs Handy laden und installieren (ggf. "Unbekannte Quellen"
   erlauben) – funktioniert auf Android 16 und älteren Versionen ab Android 7.

### Lokal bauen (Alternative, falls du eine Linux-Maschine hast)
```bash
pip install buildozer cython==0.29.36
buildozer android debug
# fertige Datei liegt danach in bin/*.apk
```

## Auf dem Desktop testen, bevor du eine APK baust
```bash
pip install -r requirements.txt
python main.py
```
(Mikrofon/TTS-Buttons funktionieren dabei nicht, alles andere schon – so
kannst du die App-Logik ohne Android-Gerät ausprobieren.)

## API-Key
Die App fragt beim ersten Start nach einem kostenlosen Gemini-API-Key
(erhältlich auf https://aistudio.google.com/apikey). Er wird nur lokal auf
dem Gerät gespeichert.

## Lizenz
Wie das Original: Creative Commons BY-NC 4.0 (nicht-kommerzielle Nutzung).
