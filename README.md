# Spritpreis Tracker Österreich

Eine kleine Flask-Webapp, die über die E-Control API aktuelle Spritpreise in Österreich abruft und anzeigt.

---

## Funktionen

- Suche nach Ort oder PLZ
- Anzeige von Super- und Dieselpreisen
- Günstigste Tankstellen werden hervorgehoben
- Letzte Suche wird im Browser gespeichert

---

## Installation auf CasaOS

### 1. Projekt auf dein CasaOS-Gerät kopieren

```bash
cd ~/
git clone <repo-url> sprit-tracker
cd sprit-tracker
```

### 2. Docker-Image bauen

```bash
docker build -t sprit-tracker .
```

### 3. Container starten

```bash
docker run -d \
  --name sprit-app \
  -p 8085:5000 \
  --restart unless-stopped \
  sprit-tracker
```

### 4. In CasaOS als Custom App einbinden (optional)

1. Öffne die **CasaOS Web-UI** (z.B. `http://<deine-casaos-ip>:81`)
2. Klicke auf **"+"** → **"Custom Install"**
3. Fülle die Felder aus:
   - **App Name:** `sprit-tracker`
   - **Docker Image:** `sprit-tracker` (lokal gebaut)
   - **Port:** `8085` → `5000`
   - **Restart Policy:** `unless-stopped`
4. (Optional) **Icon festlegen:**
   - Kopiere das Icon in ein Web-erreichbares Verzeichnis auf deinem CasaOS-Gerät
   - Gib die URL zum Icon im Feld **Icon** ein (z.B. `http://<casaos-ip>:8085/static/icon.svg` nach dem ersten Start, oder hoste es separat)
   - Alternativ: Verwende ein Online-Icon-Hosting oder konvertiere `icon.svg` zu PNG und lade es in CasaOS hoch
5. Klicke auf **Install**

### 5. Zugriff

- **Lokal:** `http://<casaos-ip>:8085`
- **Vom Heimnetz:** `http://<casaos-ip>:8085`

---

## Update / Neu bauen

Wenn du Änderungen am Code machst:

```bash
cd ~/sprit-tracker

docker stop sprit-app
docker rm sprit-app
docker build -t sprit-tracker .
docker run -d \
  --name sprit-app \
  -p 8085:5000 \
  --restart unless-stopped \
  sprit-tracker
```

Oder als Einzeiler:

```bash
docker stop sprit-app && docker rm sprit-app && docker build -t sprit-tracker . && docker run -d --name sprit-app -p 8085:5000 --restart unless-stopped sprit-tracker
```

---

## Verwendung

1. Öffne die App im Browser
2. Gib einen Ort oder eine PLZ ein (z.B. `Hohenems`)
3. Wähle **Super** oder **Diesel**
4. Klicke auf **Suchen**
5. Die günstigsten Tankstellen werden mit einem ★ markiert

---

## Technische Details

- **Backend:** Python/Flask
- **Frontend:** Vanilla HTML/JS
- **APIs:**
  - Nominatim (OpenStreetMap) für Geocoding
  - E-Control API für Spritpreise
- **Port:** `5000` (intern), empfohlen extern `8085`
