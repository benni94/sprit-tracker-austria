import os
from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/prices')
def get_prices():
    # Holt den Suchbegriff vom Browser
    query = request.args.get('q', '').strip()
    fuel_type = request.args.get('fuel', 'SUP')

    # Wenn keine Abfrage vorhanden ist, nichts zurückgeben
    if not query:
        return jsonify([])
    
    try:
        # Schritt 1: Adresse über Nominatim in Koordinaten umwandeln
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        nominatim_params = {
            "q": query,
            "format": "json",
            "limit": 1
        }
        nominatim_headers = {
            "User-Agent": "sprit-tracker/1.0"
        }
        nominatim_response = requests.get(nominatim_url, params=nominatim_params, headers=nominatim_headers, timeout=10)
        nominatim_data = nominatim_response.json()

        if not nominatim_data or len(nominatim_data) == 0:
            return jsonify({"error": "Ort nicht gefunden"}), 404

        lat = nominatim_data[0].get('lat')
        lon = nominatim_data[0].get('lon')

        if not lat or not lon:
            return jsonify({"error": "Koordinaten nicht gefunden"}), 404

        # Schritt 2: E-Control API mit Koordinaten aufrufen
        sprit_url = "https://api.e-control.at/sprit/1.0/search/gas-stations/by-address"
        sprit_params = {
            "address": query,
            "fuelType": fuel_type,
            "latitude": lat,
            "longitude": lon
        }
        sprit_response = requests.get(sprit_url, params=sprit_params, timeout=10)
        data = sprit_response.json()

        if not isinstance(data, list):
            return jsonify({"error": "Ungültige API-Antwort", "response": data}), 500

        stations = []
        for index, item in enumerate(data):
            name = item.get('name', 'Unbekannt')
            address_data = item.get('address', {})
            street = address_data.get('street', '')
            city = address_data.get('city', '')
            full_address = f"{street}, {city}" if street else city
            
            prices_list = item.get('prices', [])
            if prices_list and len(prices_list) > 0:
                price = f"{prices_list[0].get('amount', 0.0):.3f} €"
                sort_price = prices_list[0].get('amount', 9.99)
            else:
                price = "Geschlossen"
                sort_price = 9.99
            
            stations.append({
                'name': name,
                'address': full_address,
                'price': price,
                'sort_price': sort_price,
                'is_top': False # Wird gleich gesetzt
            })
            
        # Nach Preis sortieren
        stations.sort(key=lambda x: x['sort_price'])
        
        # Die günstigsten zwei als "Top" markieren
        for i in range(min(2, len(stations))):
            if stations[i]['price'] != "Geschlossen":
                stations[i]['is_top'] = True
                
        return jsonify(stations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug)