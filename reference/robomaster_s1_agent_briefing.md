# DJI RoboMaster S1 – Recherche-Briefing für einen Programmier-Agenten

## Ziel dieses Dokuments

Dieses Dokument dient als kompaktes Briefing für einen KI-Agenten oder Recherche-/Coding-Agenten.

Der Agent soll sich mit dem **DJI RoboMaster S1** beschäftigen, insbesondere mit:

- Programmiermöglichkeiten
- offizieller Online-Dokumentation
- GitHub-Repositories
- Python-APIs
- SDKs
- Community-Projekten
- ROS-/Robotik-Integration

Der Fokus liegt auf der Frage:

> Welche Online-Dokumentation und welche GitHub-Ressourcen gibt es für den programmierbaren DJI RoboMaster S1?

---

## Wichtigste Quellen

### Offizielle DJI RoboMaster S1 Programming Guide

```text
https://www.dji.com/pr/robomaster-s1/programming-guide

Wichtigste Quelle für:

    Scratch-Programmierung
    Python innerhalb der RoboMaster-App
    Chassis-Steuerung
    Gimbal-Steuerung
    Blaster
    LEDs
    Sounds
    Smart Armor
    Vision-Funktionen
    PID-Beispiele

Beispiele:

chassis_ctrl.set_trans_speed(speed)
chassis_ctrl.set_wheel_speed(lf_speed, rf_speed, lr_speed, rr_speed)
chassis_ctrl.move_with_distance(degree, distance)
gimbal_ctrl.set_follow_chassis_offset(degree)
media_ctrl.play_sound(sound_enum, wait_complete_flag=False)

Offizielles RoboMaster Python SDK

https://robomaster-dev.readthedocs.io/en/latest/
https://github.com/dji-sdk/RoboMaster-SDK
https://pypi.org/project/robomaster/

Installation:

pip install robomaster

Hinweis:

Das externe RoboMaster Python SDK ist eher auf RoboMaster EP / EP Core und Tello EDU ausgerichtet.
Die S1-Kompatibilität muss konkret geprüft werden.
Community-Projekte
collabnix/robomaster

https://github.com/collabnix/robomaster

Möglicher Nutzen:

    RoboMaster S1 Hacking
    Tutorials
    Python-Zugriff
    experimentelle S1-Nutzung

Vorsicht:

    Nicht offiziell
    Scripts vor Ausführung prüfen
    Keine Firmware-Hacks ohne klare Freigabe

nanmu42/robomasterpy

https://github.com/nanmu42/robomasterpy

Möglicher Nutzen:

    Community-Python-Framework
    Steuerlogik
    Events
    Videoverarbeitung
    strukturiertere Python-Projekte

jeguzzi/robomaster_ros

https://github.com/jeguzzi/robomaster_ros

Möglicher Nutzen:

    ROS2-Treiber
    Robotik-Integration
    Unterstützung für RoboMaster EP und S1 prüfen
    Launch-Dateien analysieren

Deutsche / PDF-Handbücher

https://dl.djicdn.com/downloads/ROBOMASTER_EP/20200423/RoboMaster_S1_User_Manual_v1.8_DE.pdf

Nützlich für:

    Aufbau
    Sicherheit
    Komponenten
    RoboMaster-App
    Programmierfunktionen
    KI-Module
    Bedienung

Aufgaben für den Agenten

Der Agent soll folgende Punkte prüfen:

    Welche offiziellen Python-Funktionen gibt es für den RoboMaster S1?
    Welche Funktionen sind nur innerhalb der RoboMaster-App verfügbar?
    Kann der RoboMaster S1 mit dem offiziellen externen robomaster Python-Paket gesteuert werden?
    Welche Firmware-Version ist nötig?
    Welcher Verbindungsmodus ist nötig?
    Welche APIs funktionieren mit dem S1?
    Welche Community-Projekte sind noch gepflegt?
    Gibt es eine robuste ROS2-Integration?
    Welche Beispielprogramme eignen sich für Anfänger?
    Welche Risiken bestehen bei Hacks oder inoffiziellen SDKs?

Empfohlener Recherche-Workflow
Schritt 1: Offizielle S1-Dokumentation prüfen

Quelle:

https://www.dji.com/pr/robomaster-s1/programming-guide

Aufgaben:

    Python-API-Funktionen extrahieren
    Scratch-zu-Python-Beziehungen erfassen
    Beispiele sammeln
    Kategorien bilden:
        Chassis
        Gimbal
        LEDs
        Blaster
        Sounds
        Vision
        Smart Armor
        Events
        Sensoren
        PID

Schritt 2: Offizielles SDK prüfen

Quellen:

https://robomaster-dev.readthedocs.io/en/latest/
https://github.com/dji-sdk/RoboMaster-SDK
https://pypi.org/project/robomaster/

Aufgaben:

    aktuelle Version prüfen
    unterstützte Geräte identifizieren
    S1-Kompatibilität prüfen
    Beispielprogramme sammeln
    Unterschiede zwischen S1-App-Python und externem SDK dokumentieren

Schritt 3: Community-Projekte prüfen

Quellen:

https://github.com/collabnix/robomaster
https://github.com/nanmu42/robomasterpy
https://github.com/jeguzzi/robomaster_ros

Aufgaben:

    README-Dateien auswerten
    Issues und Pull Requests auf S1-Kompatibilität prüfen
    letzte Commits prüfen
    Installationsanleitungen validieren
    Risiken dokumentieren
    Beispielcode extrahieren

Ergebnisformat für den Agenten

Der Agent soll am Ende liefern:
Quelle 	Typ 	S1-Relevanz 	Offiziell? 	Status 	Empfehlung
DJI S1 Programming Guide 	Dokumentation 	Hoch 	Ja 	prüfen 	Startpunkt
RoboMaster Developer Guide 	SDK-Doku 	Mittel 	Ja 	prüfen 	Ergänzend
dji-sdk/RoboMaster-SDK 	GitHub SDK 	Mittel 	Ja 	prüfen 	Python SDK
PyPI robomaster 	Python-Paket 	Mittel 	Ja 	prüfen 	Installation
collabnix/robomaster 	Community 	Mittel 	Nein 	prüfen 	Experimente
nanmu42/robomasterpy 	Community SDK 	Mittel 	Nein 	prüfen 	Framework
jeguzzi/robomaster_ros 	ROS2 	Hoch 	Nein 	prüfen 	Robotik
Sicherheits- und Vorsichtshinweise

    Offizielle Dokumentation hat Vorrang vor Community-Hacks.
    Inoffizielle Hacks können Firmware, Garantie oder Gerätesicherheit beeinflussen.
    Keine riskanten Firmware-Modifikationen ohne explizite Nutzerfreigabe empfehlen.
    Keine unbekannten ZIP-Dateien oder Scripts blind ausführen.
    Scripts wie patch.sh oder upload.sh zuerst lesen und erklären.
    Netzwerkverbindungen und Ports dokumentieren.
    Bei physischer Bewegung des Roboters Sicherheitsabstand beachten.
    Blaster-Funktionen nur kontrolliert testen.
    Roboter vor Tests aufbocken oder in sicherer Umgebung betreiben.

Empfohlene Startreihenfolge

    RoboMaster-App installieren
    S1 verbinden
    DJI S1 Programming Guide lesen
    Scratch-Beispiele testen
    Python-Beispiele innerhalb der App testen
    einfache Bewegungsprogramme schreiben
    LEDs, Sounds und Gimbal testen
    Vision- und KI-Funktionen untersuchen
    externes SDK prüfen
    Community-Projekte und ROS2 danach betrachten

Kurze Zusammenfassung

Der RoboMaster S1 ist programmierbar.
Die beste offizielle Quelle ist die DJI RoboMaster S1 Programming Guide.

Das externe DJI RoboMaster Python SDK ist wichtig, aber stärker auf RoboMaster EP / EP Core ausgerichtet.

Für fortgeschrittene Projekte sind Community-Projekte wie robomaster_ros, robomasterpy und collabnix/robomaster interessant, müssen aber auf Aktualität, Sicherheit und S1-Kompatibilität geprüft werden.
