from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# Koordinaten für Hohenems
LAT = "47.3615"
LON = "9.6917"
URL = f"https://api.e-control.at/sprit/1.0/search/gas-stations/by-address?latitude={LAT}&longitude={LON}&fuelType=SUP&includeClosed=false"

# Deine Favoriten
FAVORITEN_KEYWORDS = ["JET", "OIL!"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/prices')
def get_prices():
    try:
        response = requests.get(URL, timeout=10)
        data = response.json()
        
        stations = []
        for item in data:
            name = item.get('name', 'Unbekannt')
            address = item.get('address', {}).get('street', 'Unbekannte Straße')
            
            # Fehlerquelle behoben: Sicherstellen, dass 'prices' existiert und nicht leer ist
            prices_list = item.get('prices', [])
            if prices_list and len(prices_list) > 0:
                price = f"{prices_list[0].get('amount', 0.0):.3f} €"
                sort_price = prices_list[0].get('amount', 9.99) # Fallback für Sortierung
            else:
                price = "Geschlossen / Kein Preis"
                sort_price = 9.99  # Sortiert Tankstellen ohne Preis nach ganz unten
            
            # Prüfen, ob es ein Favorit ist
            is_fav = any(fav.lower() in name.lower() for fav in FAVORITEN_KEYWORDS)
            
            stations.append({
                'name': name,
                'address': address,
                'price': price,
                'sort_price': sort_price,
                'is_fav': is_fav
            })
            
        # Favoriten nach oben sortieren, danach nach dem numerischen Preis
        stations.sort(key=lambda x: (not x['is_fav'], x['sort_price']))
        return jsonify(stations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)