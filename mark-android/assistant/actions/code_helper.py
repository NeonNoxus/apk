"""code_helper.py -- Inline-Code-Review/-Erklärung/-Debugging über Gemini."""

import google.generativeai as genai
from assistant import config_manager

TOOL = {
    "name": "code_helper",
    "description": "Erklärt, debuggt oder schreibt Code auf Anfrage.",
    "parameters": {
        "type": "object",
        "properties": {
            "task": {"type": "string", "description": "Was soll mit dem Code gemacht werden"},
            "code": {"type": "string", "description": "Der Code, falls vorhanden"},
        },
        "required": ["task"],
    },
}


def run(task, code=""):
    api_key = config_manager.get_api_key()
    if not api_key:
        return "Kein API-Key hinterlegt."
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"Aufgabe: {task}\n\nCode:\n{code}" if code else f"Aufgabe: {task}"
    response = model.generate_content(prompt)
    return response.text
