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

        # Debug: log first item keys and sample
        if data and len(data) > 0:
            first = data[0]
            print("API first item keys:", list(first.keys()) if isinstance(first, dict) else type(first))
            print("API first item:", first)

        stations = []
        for index, item in enumerate(data):
            if not isinstance(item, dict):
                continue
                
            name = item.get('name', 'Unbekannt')
            
            # Extract street and city separately
            street = ''
            city = ''
            postal_code = ''
            country = ''
            
            address_raw = item.get('address', '')
            if isinstance(address_raw, dict):
                street = address_raw.get('street') or ''
                city = address_raw.get('city') or ''
                postal_code = address_raw.get('postalCode') or ''
                country = address_raw.get('country') or ''
            elif isinstance(address_raw, str) and address_raw:
                street = address_raw
            
            # Fallback: try other fields
            if not street and not city:
                location = item.get('location', {})
                if isinstance(location, dict):
                    loc_addr = location.get('address', '') or location.get('formattedAddress', '')
                    if loc_addr:
                        street = loc_addr
                if not city:
                    city = item.get('city', '') or ''
            
            # Build display address (street + city for display, country only if needed)
            address_parts = []
            if street:
                address_parts.append(street)
            if postal_code and city:
                address_parts.append(f"{postal_code} {city}")
            elif city:
                address_parts.append(city)
            if country and country != 'Österreich':
                address_parts.append(country)
            full_address = ', '.join(address_parts) if address_parts else (street or city or 'Österreich')
            
            # Defensive price extraction
            prices_list = item.get('prices', []) if isinstance(item, dict) else []
            if prices_list and len(prices_list) > 0:
                first_price = prices_list[0]
                if isinstance(first_price, dict):
                    amount = first_price.get('amount', 0.0)
                    fuel_label = first_price.get('label', fuel_type)
                else:
                    # API may return plain numbers
                    amount = float(first_price) if first_price else 0.0
                    fuel_label = fuel_type
                price = f"{amount:.3f} €"
                sort_price = amount
            else:
                fuel_label = fuel_type
                price = "Geschlossen"
                sort_price = 9.99
            
            stations.append({
                'name': name,
                'address': full_address,
                'street': street,
                'city': city,
                'price': price,
                'fuel_label': fuel_label,
                'sort_price': sort_price,
                'is_top': False
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