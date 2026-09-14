"""ui_settings.py -- Einstellungs-Popup: API-Key, Assistentenname, Nutzername, Farbe."""

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

from assistant import config_manager


def open_settings(on_saved=None):
    layout = BoxLayout(orientation="vertical", spacing=8, padding=12)

    api_key_input = TextInput(text=config_manager.get_api_key(), hint_text="Gemini API-Key", multiline=False, password=True)
    assistant_name_input = TextInput(text=config_manager.get_assistant_name(), hint_text="Name des Assistenten", multiline=False)
    user_name_input = TextInput(text=config_manager.get_user_name(), hint_text="Dein Name", multiline=False)
    color_input = TextInput(text=config_manager.get_ui_color(), hint_text="#00E5FF", multiline=False)

    layout.add_widget(Label(text="Gemini API-Key", size_hint_y=None, height=24))
    layout.add_widget(api_key_input)
    layout.add_widget(Label(text="Assistenten-Name", size_hint_y=None, height=24))
    layout.add_widget(assistant_name_input)
    layout.add_widget(Label(text="Dein Name", size_hint_y=None, height=24))
    layout.add_widget(user_name_input)
    layout.add_widget(Label(text="UI-Farbe (Hex)", size_hint_y=None, height=24))
    layout.add_widget(color_input)

    popup = Popup(title="Einstellungen", content=layout, size_hint=(0.9, 0.7))

    def save(_instance):
        config_manager.set_api_key(api_key_input.text.strip())
        config_manager.set("assistant_name", assistant_name_input.text.strip() or "Mark")
        config_manager.set("user_name", user_name_input.text.strip() or "Boss")
        config_manager.set("ui_color", color_input.text.strip() or "#00E5FF")
        popup.dismiss()
        if on_saved:
            on_saved()

    save_btn = Button(text="Speichern", size_hint_y=None, height=48)
    save_btn.bind(on_release=save)
    layout.add_widget(save_btn)

    popup.open()
