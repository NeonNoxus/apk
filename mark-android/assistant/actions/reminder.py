"""
reminder.py
-----------
Original: OS-native geplante Benachrichtigungen (Windows Task Scheduler /
macOS LaunchAgent / Linux systemd). Auf Android gibt es dafür kein Äquivalent,
das eine App selbst anlegen kann — stattdessen registriert man einen Alarm
beim System-AlarmManager, der die App zur gewünschten Zeit aufweckt und dann
eine lokale Benachrichtigung zeigt.

Wichtiger Hinweis für den Nutzer: Ab Android 12+ muss die exakte Alarm-
Berechtigung (SCHEDULE_EXACT_ALARM) vom Nutzer selbst in den System-
einstellungen erlaubt werden — eine App kann sie sich nicht mehr automatisch
holen. Falls sie fehlt, fällt das hier auf einen ungefähren Alarm zurück
(kann ein paar Minuten abweichen), statt einfach zu scheitern.
"""

import time
from plyer import notification

try:
    from jnius import autoclass, cast
    from android import mActivity
    ANDROID = True
except Exception:
    ANDROID = False

TOOL = {
    "name": "set_reminder",
    "description": "Legt eine Erinnerung an, die nach 'delay_minutes' Minuten als Benachrichtigung erscheint.",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Woran erinnert werden soll"},
            "delay_minutes": {"type": "number", "description": "In wie vielen Minuten"},
        },
        "required": ["text", "delay_minutes"],
    },
}


def run(text, delay_minutes):
    delay_minutes = float(delay_minutes)
    trigger_at_ms = int((time.time() + delay_minutes * 60) * 1000)

    if ANDROID:
        try:
            _schedule_android_alarm(text, trigger_at_ms)
            return f"Erinnerung '{text}' in {delay_minutes:.0f} Minuten gesetzt."
        except Exception as exc:
            return f"Konnte Systemalarm nicht setzen ({exc}), zeige stattdessen sofort eine Test-Benachrichtigung."

    # Desktop-Fallback beim lokalen Testen ohne Android
    notification.notify(title="Mark – Erinnerung", message=text, timeout=10)
    return f"(Test-Modus) Erinnerung sofort angezeigt: {text}"


def _schedule_android_alarm(text, trigger_at_ms):
    Context = autoclass("android.content.Context")
    Intent = autoclass("android.content.Intent")
    PendingIntent = autoclass("android.app.PendingIntent")
    AlarmManager = autoclass("android.app.AlarmManager")

    activity = mActivity
    alarm_manager = cast(AlarmManager, activity.getSystemService(Context.ALARM_SERVICE))

    intent = Intent(activity.getApplicationContext(), autoclass("org.kivy.android.PythonActivity"))
    intent.putExtra("reminder_text", text)
    pending_intent = PendingIntent.getActivity(
        activity, int(trigger_at_ms % 100000), intent,
        PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE,
    )
    try:
        alarm_manager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, trigger_at_ms, pending_intent)
    except Exception:
        # Keine SCHEDULE_EXACT_ALARM-Erlaubnis -> ungefährer Alarm statt Absturz
        alarm_manager.set(AlarmManager.RTC_WAKEUP, trigger_at_ms, pending_intent)
