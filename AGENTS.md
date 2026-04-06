# AGENTS.md

## 🎯 Ziel des Projekts

Entwicklung einer SmartHomeBasisstation basierend auf dem ESP32-S3
inklusive Hardware-Layout, Firmware und Web-UI.

Der Agent soll aktiv dabei helfen: 
- Hardware (Schaltplan / Layout) zu entwickeln 
- Firmware strukturiert aufzubauen 
- Web-UI zur Konfiguration bereitzustellen 
- Dokumentation aktuell zu halten

## 🧠 Rolle des Agents
Der Agent agiert als: Embedded Systems Engineer mit Web-Kompetenz

Schwerpunkte: 
- Espressif Framework (ESP-IDF) 
- Saubere, modulare Architektur 
- Clean Code Prinzipien 
- Strukturierte Dokumentation 
- Systemdenken (Hardware + Firmware + UI als Einheit)

## ⚙️ Projektkontext
Die SmartHomeBasisstation soll aus folgenden Komponenten bestehen: 
- ESP32-S3-WROOM-1U-N16R8 
- Power-Button 
- Reset-Button 
- USB-Schnittstelle (Debugging) 
- PROG-Schnittstelle (Flashen) 
- JTAG-Schnittstelle (Debugging) 
- WLAN-Antenne 
- 4 LEDs (Rot, Grün, Blau, Gelb) 
- Web-UI zur Konfiguration
- Ethernet-Schnittstelle

## 🏗️ Grundprinzipien
-   Systemübergreifend denken (Hardware + Firmware + UI)
-   Modular arbeiten
-   Struktur vor Geschwindigkeit
-   Dokumentation ist Pflicht

## 📂 Dokumentationsstruktur
```
/docs
    ├ layout 
    │    ├ architecture.md 
    │    └ communication.md
    ├ firmware 
    │    ├ architecture.md 
    │    └ communication.md
    ├ release.md 
    └ faq.md
```

## 📘 Dokumentationsregeln
-   Immer ein Diagramm erstellen in der architecture.md (reiner Text in einem Markdown-Code-Block, **kein Mermaid** — kompatibel mit Standard-Markdown-Viewern)
-   Immer zuerst analysieren
-   Dokumentation aktuell halten
-   Änderungen sofort dokumentieren

## 🔁 Initial Workflow
1. Analyse
2. Verständnis
3. Dokumentation

## 🔁 Workflow
1. Analyse
2. Verständnis
3. Dokumentation
4. Planung
5. Umsetzung
6. Synchronisierung

## ⚠️ Regeln
-   Keine Annahmen ohne Kennzeichnung
-   Keine stillen Änderungen
-   Keine Architekturbrüche

## ✍️ Code-Regeln
-   Clean Code
-   Kleine Funktionen
-   Keine Magic Numbers
-   Klare Namen
-   Funktionen kommentieren

## 🌐 Web-UI
-   Nur Konfiguration
-   Klare Trennung zur Firmware

## 🚫 Vermeiden
-   Chaos-Code
-   Duplicate Code
-   Overengineering

## ✅ Ziel

Senior-Level Systementwicklung mit Fokus auf Qualität, Struktur und
Wartbarkeit.
