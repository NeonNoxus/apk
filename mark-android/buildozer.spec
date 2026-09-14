[app]
title = Mark Assistant
package.name = markassistant
package.domain = org.fatihmakes.mark

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt

version = 1.0.0

requirements = python3,kivy==2.3.0,plyer,pyjnius,requests,google-generativeai,pillow,certifi,pyperclip

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/data/icon.png

# Android-16 = API-Level 35 (Android 15) / minSdk niedriger für Kompatibilität.
# Zielt auf die neueste stabile Android-API (deckt auch Android 16 ab, da
# Android abwärts-/aufwärtskompatibel über minapi/targetapi funktioniert).
android.api = 35
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

android.permissions = INTERNET, RECORD_AUDIO, POST_NOTIFICATIONS, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, VIBRATE

android.allow_backup = True
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
