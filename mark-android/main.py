"""
main.py -- Mark Assistant für Android (Kivy-Port von Mark LIII)

Portierungs-Hinweise (siehe README.md für die volle Liste):
  * Live-Audio-Streaming -> Text-Chat + lokale Android-STT/TTS (robuster)
  * Wake-Word, Systemsteuerung, Desktop-/Browser-Automatisierung, Steam/Epic-
    Updater: entfallen, da auf Android nicht sinnvoll/technisch möglich.
  * Alles andere (Memory, Wetter, Websuche, Erinnerungen, Code-Helfer,
    Datei-Zusammenfassung, Clipboard-Intelligenz) ist adaptiert enthalten.
"""

import threading

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.factory import Factory

from assistant import config_manager, memory_manager, gemini_client, ui_settings, ui_memory
from assistant.actions import weather, web_search, reminder, code_helper

Builder.load_file("mark.kv")

# ── Tool-Registrierung: jede Action liefert ein TOOL-Dict + run() ───────────
_ACTION_MODULES = [weather, web_search, reminder, code_helper]

TOOLS = [m.TOOL for m in _ACTION_MODULES if hasattr(m, "TOOL")]
TOOL_ROUTER = {m.TOOL["name"]: m.run for m in _ACTION_MODULES if hasattr(m, "TOOL")}


def recall_memory(query):
    return memory_manager.search_memory(query)


def save_memory(key, value):
    memory_manager.update_memory(key, value)
    return f"Gemerkt: {key} = {value}"


TOOLS.append({
    "name": "recall_memory",
    "description": "Sucht im gespeicherten Langzeitgedächtnis nach einem Stichwort.",
    "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
})
TOOL_ROUTER["recall_memory"] = recall_memory

TOOLS.append({
    "name": "save_memory",
    "description": "Speichert einen neuen Fakt über den Nutzer dauerhaft.",
    "parameters": {
        "type": "object",
        "properties": {"key": {"type": "string"}, "value": {"type": "string"}},
        "required": ["key", "value"],
    },
})
TOOL_ROUTER["save_memory"] = save_memory


class RootScreen(BoxLayout):
    listening = False

    def on_kv_post(self, *_args):
        self.chat_history = []
        self._add_bubble(
            f"Hey, ich bin {config_manager.get_assistant_name()}. Wie kann ich helfen?",
            is_user=False,
        )
        last_session = memory_manager.pop_last_session()
        if last_session:
            self._add_bubble(f"Übrigens, zuletzt haben wir über folgendes gesprochen: {last_session}", is_user=False)

    def _add_bubble(self, text, is_user):
        bubble = Factory.ChatBubble(text=text, is_user=is_user)
        self.ids.chat_log.add_widget(bubble)
        Clock.schedule_once(lambda *_: setattr(self.ids.scroll, "scroll_y", 0), 0.05)

    def send_text(self):
        text = self.ids.text_input.text.strip()
        if not text:
            return
        self.ids.text_input.text = ""
        self._add_bubble(text, is_user=True)
        threading.Thread(target=self._run_chat, args=(text,), daemon=True).start()

    def _run_chat(self, text):
        try:
            reply, new_history = gemini_client.chat_once(
                text, history=self.chat_history, tools=TOOLS, tool_router=TOOL_ROUTER
            )
            self.chat_history = new_history
        except Exception as exc:
            reply = f"Fehler: {exc}"
        Clock.schedule_once(lambda *_: self._add_bubble(reply, is_user=False))
        Clock.schedule_once(lambda *_: self._speak(reply))

    def _speak(self, text):
        try:
            from plyer import tts
            tts.speak(message=text)
        except Exception:
            pass  # TTS optional -- z.B. beim Testen auf dem Desktop nicht verfügbar

    def toggle_listen(self):
        try:
            from plyer import stt
        except Exception:
            self._add_bubble("Spracherkennung ist auf diesem Gerät nicht verfügbar.", is_user=False)
            return

        if not self.listening:
            self.listening = True
            stt.start(callback=self._on_speech_result)
        else:
            self.listening = False
            stt.stop()

    def _on_speech_result(self, recognized_text):
        self.listening = False
        if recognized_text:
            self.ids.text_input.text = recognized_text
            self.send_text()

    def open_settings_panel(self):
        ui_settings.open_settings(on_saved=self._refresh_theme)

    def open_memory_panel(self):
        ui_memory.open_memory_panel()

    def process_clipboard(self, mode):
        """Clipboard-Intelligenz: Übersetzen / Zusammenfassen / Erklären / Fixen
        des aktuell kopierten Texts (adaptiert von 'Clipboard Intelligence')."""
        from kivy.core.clipboard import Clipboard
        text = Clipboard.paste()
        if not text:
            self._add_bubble("Zwischenablage ist leer.", is_user=False)
            return
        self._add_bubble(f"[{mode}] {text[:80]}{'…' if len(text) > 80 else ''}", is_user=True)
        threading.Thread(target=self._run_clipboard, args=(text, mode), daemon=True).start()

    def _run_clipboard(self, text, mode):
        try:
            result = gemini_client.quick_transform(text, mode)
        except Exception as exc:
            result = f"Fehler: {exc}"
        Clock.schedule_once(lambda *_: self._add_bubble(result, is_user=False))

    def _refresh_theme(self):
        App.get_running_app().ui_color = config_manager.get_ui_color()


class MarkApp(App):
    ui_color = "#00E5FF"

    def build(self):
        config_manager.init(self.user_data_dir)
        memory_manager.init(self.user_data_dir)
        self.ui_color = config_manager.get_ui_color()
        return RootScreen()

    def on_start(self):
        if not config_manager.get_api_key():
            Clock.schedule_once(lambda *_: ui_settings.open_settings(), 0.3)


if __name__ == "__main__":
    MarkApp().run()
