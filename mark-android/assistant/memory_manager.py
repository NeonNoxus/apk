"""
memory_manager.py
------------------
Adaptiert von Mark LIII (memory/memory_manager.py). Kernidee 1:1 übernommen:

  * Nichts wird automatisch gelöscht (nur ein Not-Limit als Runaway-Schutz).
  * Der Prompt bekommt nicht den ganzen Speicher, sondern einen knappen Kern
    (Identität + zuletzt aktualisierte Fakten) plus einen Index aller
    restlichen Schlüssel, damit recall_memory() gezielt nachschlagen kann.
  * long_term.json liegt im privaten Android-App-Speicher.
"""

import json
import os
import time

_MEMORY_FILE = None
_HARD_CAP_ENTRIES = 5000  # Not-Bremse, in normaler Nutzung nie erreicht
_PROMPT_CORE_CHAR_BUDGET = 1200


def init(app_data_dir):
    global _MEMORY_FILE
    os.makedirs(app_data_dir, exist_ok=True)
    _MEMORY_FILE = os.path.join(app_data_dir, "long_term.json")
    if not os.path.exists(_MEMORY_FILE):
        _write({"facts": {}, "sessions": [], "monitors": []})


def _read():
    if _MEMORY_FILE is None or not os.path.exists(_MEMORY_FILE):
        return {"facts": {}, "sessions": [], "monitors": []}
    try:
        with open(_MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"facts": {}, "sessions": [], "monitors": []}


def _write(data):
    if _MEMORY_FILE is None:
        return
    with open(_MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_memory(key, value):
    """Speichert/aktualisiert einen Fakt. Nichts wird je automatisch gelöscht,
    außer die Not-Bremse (_HARD_CAP_ENTRIES) greift – dann wird das der
    aufrufenden Stelle über den Rückgabewert mitgeteilt, statt es zu verschweigen."""
    data = _read()
    hit_cap = False
    if key not in data["facts"] and len(data["facts"]) >= _HARD_CAP_ENTRIES:
        oldest_key = min(data["facts"], key=lambda k: data["facts"][k]["updated_at"])
        del data["facts"][oldest_key]
        hit_cap = True
    data["facts"][key] = {"value": value, "updated_at": time.time()}
    _write(data)
    return hit_cap


def delete_fact(key):
    data = _read()
    if key in data["facts"]:
        del data["facts"][key]
        _write(data)
        return True
    return False


def list_facts():
    """Für das Memory-Panel in der UI: [(key, value, updated_at), ...] neueste zuerst."""
    data = _read()
    items = [(k, v["value"], v["updated_at"]) for k, v in data["facts"].items()]
    items.sort(key=lambda x: x[2], reverse=True)
    return items


def search_memory(query):
    """Lokale Volltextsuche über alle Fakten – das recall_memory-Tool für Gemini."""
    query_lower = query.lower()
    data = _read()
    hits = []
    for k, v in data["facts"].items():
        if query_lower in k.lower() or query_lower in str(v["value"]).lower():
            hits.append(f"{k}: {v['value']}")
    return "\n".join(hits) if hits else "Nichts dazu gefunden."


def format_memory_for_prompt():
    """Kern für den System-Prompt: neueste Fakten bis zum Zeichen-Budget,
    danach ein Index der übrigen Schlüssel, damit recall_memory sie noch
    findbar macht (siehe Docstring oben: 'ein Modell kann nichts nachschlagen,
    von dessen Existenz es nichts weiß')."""
    data = _read()
    items = sorted(data["facts"].items(), key=lambda kv: kv[1]["updated_at"], reverse=True)

    core_lines = []
    used_chars = 0
    included_keys = set()
    for key, entry in items:
        line = f"- {key}: {entry['value']}"
        if used_chars + len(line) > _PROMPT_CORE_CHAR_BUDGET:
            break
        core_lines.append(line)
        used_chars += len(line)
        included_keys.add(key)

    remaining_keys = [k for k, _ in items if k not in included_keys]
    index_line = ""
    if remaining_keys:
        index_line = "\n(Weitere gespeicherte Themen, per recall_memory abrufbar: " + \
                      ", ".join(remaining_keys) + ")"

    return "\n".join(core_lines) + index_line


def save_session_summary(summary_text):
    data = _read()
    data["sessions"].append({"summary": summary_text, "ts": time.time(), "consumed": False})
    _write(data)


def pop_last_session():
    """Gibt die letzte noch nicht erwähnte Sitzungs-Zusammenfassung zurück und
    markiert sie als konsumiert (wird also, wie im Original, nie zweimal erwähnt)."""
    data = _read()
    for session in reversed(data["sessions"]):
        if not session["consumed"]:
            session["consumed"] = True
            _write(data)
            return session["summary"]
    return None
