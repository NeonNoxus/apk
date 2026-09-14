"""ui_memory.py -- Memory-Panel: alle gespeicherten Fakten anzeigen und einzeln löschen können."""

from datetime import datetime

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label

from assistant import memory_manager


def open_memory_panel():
    outer = BoxLayout(orientation="vertical", spacing=6, padding=10)
    scroll = ScrollView()
    inner = BoxLayout(orientation="vertical", size_hint_y=None, spacing=6)
    inner.bind(minimum_height=inner.setter("height"))

    facts = memory_manager.list_facts()
    if not facts:
        inner.add_widget(Label(text="Noch nichts gespeichert.", size_hint_y=None, height=40))

    popup = Popup(title="🧠 Gedächtnis", size_hint=(0.9, 0.85))

    def rebuild():
        inner.clear_widgets()
        for key, value, updated_at in memory_manager.list_facts():
            row = BoxLayout(size_hint_y=None, height=56, spacing=6)
            date_str = datetime.fromtimestamp(updated_at).strftime("%d.%m.%Y")
            row.add_widget(Label(text=f"[b]{key}[/b]: {value}\n[size=11]{date_str}[/size]",
                                  markup=True, halign="left", valign="middle"))
            del_btn = Button(text="✕", size_hint_x=None, width=44)

            def make_delete(k=key):
                def _delete(_instance):
                    memory_manager.delete_fact(k)
                    rebuild()
                return _delete

            del_btn.bind(on_release=make_delete())
            row.add_widget(del_btn)
            inner.add_widget(row)

    rebuild()
    scroll.add_widget(inner)
    outer.add_widget(scroll)
    close_btn = Button(text="Schließen", size_hint_y=None, height=48)
    close_btn.bind(on_release=lambda _i: popup.dismiss())
    outer.add_widget(close_btn)

    popup.content = outer
    popup.open()
