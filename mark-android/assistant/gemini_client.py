"""
gemini_client.py
-----------------
Dünner Wrapper um die Gemini-API (Text-Chat statt Live-Audio-Streaming).

Warum kein Live-Audio wie im Original?
Die Gemini *Live* API verlangt einen dauerhaften WebSocket mit
Roh-PCM-Streaming in beide Richtungen. Das ist auf Android technisch möglich,
aber deutlich fragiler (Verbindungsabbrüche im Hintergrund, Akku, Berechtigungen).
Für eine robuste erste App-Version nutzen wir stattdessen:
  Sprache -> Text (Android-Spracherkennung, lokal)
  Text -> Gemini (normale generate_content-Anfrage, inkl. Tool-Calling)
  Text -> Sprache (Android-TTS, lokal)
Das Ergebnis fühlt sich für den Nutzer fast identisch an, ist aber
zuverlässiger auf einem Handy. Live-Streaming kann als Ausbaustufe 2
nachgerüstet werden, sobald die Text-Variante stabil läuft.
"""

import json
import google.generativeai as genai

from assistant.memory_manager import format_memory_for_prompt
from assistant import config_manager


SYSTEM_PROMPT_TEMPLATE = """Du bist {assistant_name}, ein persönlicher KI-Assistent auf dem Handy von {user_name}.
Antworte kurz, hilfreich und in der Sprache, in der {user_name} dich anspricht.

Bekannter Kontext über den Nutzer:
{memory_block}

Du hast Zugriff auf Werkzeuge (Wetter, Websuche, Erinnerungen, Code-Hilfe,
Notiz-/Datei-Verarbeitung). Nutze sie, wenn sie die Antwort verbessern würden,
anstatt zu raten.
"""


def _build_model(tools=None):
    api_key = config_manager.get_api_key()
    if not api_key:
        raise RuntimeError("Kein Gemini-API-Key hinterlegt. Bitte in den Einstellungen eintragen.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        tools=tools,
    )


def chat_once(user_text, history=None, tools=None, tool_router=None):
    """
    Schickt eine Nachricht an Gemini, führt bei Bedarf lokale Tools aus
    (tool_router: dict[name] -> callable(**args) -> str) und gibt am Ende
    die finale Textantwort zurück.
    """
    history = history or []
    assistant_name = config_manager.get_assistant_name()
    user_name = config_manager.get_user_name()
    memory_block = format_memory_for_prompt()

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        assistant_name=assistant_name,
        user_name=user_name,
        memory_block=memory_block or "(noch nichts gespeichert)",
    )

    model = _build_model(tools=tools)
    convo = model.start_chat(history=history)

    full_prompt = f"{system_prompt}\n\nNachricht von {user_name}: {user_text}"
    response = convo.send_message(full_prompt)

    # Einfache Tool-Call-Schleife (Gemini function calling)
    for _ in range(5):
        function_call = _extract_function_call(response)
        if not function_call or not tool_router:
            break
        name = function_call.name
        args = dict(function_call.args) if function_call.args else {}
        if name not in tool_router:
            tool_result = f"Unbekanntes Werkzeug: {name}"
        else:
            try:
                tool_result = tool_router[name](**args)
            except Exception as exc:  # Tool-Fehler dürfen den Chat nie abschießen
                tool_result = f"Fehler beim Ausführen von {name}: {exc}"

        response = convo.send_message(
            genai.protos.Content(
                parts=[genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=name,
                        response={"result": tool_result},
                    )
                )]
            )
        )

    return response.text, convo.history


def _extract_function_call(response):
    try:
        for part in response.candidates[0].content.parts:
            if getattr(part, "function_call", None) and part.function_call.name:
                return part.function_call
    except Exception:
        pass
    return None


def quick_transform(text, mode):
    """Für die Zwischenablage-Intelligenz: Übersetzen / Zusammenfassen / Erklären / Fixen."""
    prompts = {
        "translate": "Übersetze den folgenden Text sinnvoll (erkenne die Zielsprache aus dem Kontext, "
                     "notfalls ins Englische). Gib NUR die Übersetzung zurück:\n\n",
        "summarize": "Fasse den folgenden Text in 2-3 knappen Sätzen zusammen:\n\n",
        "explain": "Erkläre den folgenden Text einfach und verständlich:\n\n",
        "fix": "Korrigiere Rechtschreibung und Grammatik des folgenden Texts, "
               "gib NUR den korrigierten Text zurück:\n\n",
    }
    prompt = prompts.get(mode, prompts["explain"]) + text
    model = _build_model()
    response = model.generate_content(prompt)
    return response.text.strip()
