"""
file_processor.py
------------------
Original konnte beliebige lokale Dateien lesen/zusammenfassen. Auf Android
darf eine App ab API 30+ (scoped storage) nicht mehr frei im Dateisystem
herumlesen -- nur Dateien, die der Nutzer explizit über den System-
Dateiauswahldialog freigegeben hat (oder die im eigenen App-Ordner liegen).

Deshalb erwartet run() hier einen bereits vom Nutzer ausgewählten Pfad
(die UI ruft den Android-Dateiauswahldialog über plyer.filechooser auf und
übergibt den Pfad), statt frei im Dateisystem zu suchen wie im Original.
"""

import os
import google.generativeai as genai
from assistant import config_manager

SUPPORTED_TEXT_EXTS = {".txt", ".md", ".csv", ".json", ".py", ".log"}


def read_and_summarize(filepath, question=None):
    ext = os.path.splitext(filepath)[1].lower()
    if ext not in SUPPORTED_TEXT_EXTS:
        return f"Dateityp {ext} wird aktuell nicht unterstützt (nur Textformate: {', '.join(SUPPORTED_TEXT_EXTS)})."

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as exc:
        return f"Konnte Datei nicht lesen: {exc}"

    content = content[:20000]  # Kontext-Budget schonen

    api_key = config_manager.get_api_key()
    if not api_key:
        return "Kein API-Key hinterlegt."
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    if question:
        prompt = f"Beantworte anhand dieses Dateiinhalts die Frage: {question}\n\nInhalt:\n{content}"
    else:
        prompt = f"Fasse den folgenden Dateiinhalt knapp zusammen:\n\n{content}"

    response = model.generate_content(prompt)
    return response.text
