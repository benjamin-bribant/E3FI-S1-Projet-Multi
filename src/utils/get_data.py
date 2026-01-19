import os
import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

load_dotenv()

# Configuration de l'API OpenAQ v3
BASE_URL = "https://api.openaq.org/v3"
API_KEY = os.getenv('OPENAQ_API_KEY')

if not API_KEY:
    raise ValueError("Clé API manquante! Vérifier que OPENAQ_API_KEY est dans le fichier .env")

def get_parameter_id(parameter):
    """Convertit le nom du paramètre en ID pour l'API v3"""
    mapping = {
        'pm25': 2,
        'pm2.5': 2,
        'pm10': 1,
        'no2': 3,
        'so2': 5,
        'o3': 4,
        'co': 6
    }
    return mapping.get(parameter.lower(), 2)

def get_all_countries():
    """Récupère la liste de tous les pays disponibles"""
    url = f"{BASE_URL}/countries"
    headers = {'X-API-Key': API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
        else:
            print(f"Erreur lors de la récupération des pays: {response.status_code}")
            return []
    except Exception as e:
        print(f"Erreur de connexion: {e}")
        return []

def get_locations(limit=1000, country=None, page=1):
    """
    Récupère la liste des locations (stations de mesure)
    
    Parameters:
    - limit: nombre max de résultats par page (max 1000)
    - country: code pays ISO (ex: 'FR', 'US', 'CN')
    - page: numéro de page pour la pagination
    """
    url = f"{BASE_URL}/locations"
    
    headers = {'X-API-Key': API_KEY}
    
    params = {
        'limit': limit,
        'page': page
    }
    
    if country:
        params['countries_id'] = country.upper()
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('results', []), data.get('meta', {})
        elif response.status_code == 429:
            print("Rate limit atteint, attente de 60 secondes...")
            time.sleep(60)
            return get_locations(limit, country, page)
        else:
            print(f"Erreur API: {response.status_code}")
            print(f"Message: {response.text}")
            return [], {}
    except Exception as e:
        print(f"Erreur de connexion: {e}")
        return [], {}

def get_latest_by_parameter(parameter='pm25', limit=1000, page=1):
    """
    Récupère les dernières mesures pour un paramètre spécifique
    
    Parameters:
    - parameter: 'pm25', 'pm10', 'no2', 'so2', 'o3', 'co'
    - limit: nombre max de résultats par page (max 1000)
    - page: numéro de page pour la pagination
    """
    parameter_id = get_parameter_id(parameter)
    url = f"{BASE_URL}/parameters/{parameter_id}/latest"
    
    headers = {'X-API-Key': API_KEY}
    
    params = {
        'limit': limit,
        'page': page
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('results', []), data.get('meta', {})
        elif response.status_code == 429:
            print("Rate limit atteint, attente de 60 secondes...")
            time.sleep(60)
            return get_latest_by_parameter(parameter, limit, page)
        else:
            print(f"Erreur API: {response.status_code}")
            print(f"Message: {response.text}")
            return [], {}
    except Exception as e:
        print(f"Erreur de connexion: {e}")
        return [], {}

def fetch_all_data(parameters=['pm25', 'pm10', 'no2', 'so2', 'o3', 'co'], 
                   countries=None, max_pages=3):
    """
    Récupère toutes les données pour plusieurs polluants
    
    Parameters:
    - parameters: liste des polluants à récupérer
    - countries: liste des codes pays à filtrer (optionnel)
    - max_pages: nombre maximum de pages par polluant
    """
    all_measurements = []
    all_locations = []
    
    total = len(parameters)
    current = 0
    
    # Récupérer les locations si on filtre par pays
    if countries:
        print("\n📍 Récupération des locations pour les pays sélectionnés...")
        for country in countries:
            print(f"  - {country}...")
            page = 1
            while page <= 5:  # Max 5 pages par pays
                locs, meta = get_locations(limit=1000, country=country, page=page)
                if not locs:
                    break
                all_locations.extend(locs)
                print(f"    Page {page}: {len(locs)} locations (Total: {len(all_locations)})")
                
                found = meta.get('found', 0)
                if len(locs) < 1000 or page * 1000 >= found:
                    break
                page += 1
                time.sleep(0.3)
        
        print(f"✓ {len(all_locations)} locations trouvées")
    
    # Récupérer les mesures par paramètre
    for parameter in parameters:
        current += 1
        print(f"\n[{current}/{total}] Récupération des dernières mesures de {parameter.upper()}...")
        
        page = 1
        while page <= max_pages:
            results, meta = get_latest_by_parameter(
                parameter=parameter,
                limit=1000,
                page=page
            )
            
            if not results:
                break
            
            # Filtrer par pays si nécessaire
            if countries and all_locations:
                location_ids = {loc['id'] for loc in all_locations}
                results = [r for r in results if r.get('locationsId') in location_ids]
            
            all_measurements.extend(results)
            print(f"  Page {page}: {len(results)} mesures récupérées (Total: {len(all_measurements)})")
            
            # Vérifier s'il y a une page suivante
            found = meta.get('found', 0)
            if len(results) < 1000 or page * 1000 >= found:
                break
            
            page += 1
            time.sleep(0.5)  # Pause pour éviter le rate limiting
    
    # Enrichir les données avec les informations des locations
    if all_locations:
        print("\n🔗 Enrichissement des données avec les informations de location...")
        locations_dict = {loc['id']: loc for loc in all_locations}
        
        for measurement in all_measurements:
            loc_id = measurement.get('locationsId')
            if loc_id in locations_dict:
                loc = locations_dict[loc_id]
                measurement['country'] = loc.get('country')
                measurement['city'] = loc.get('city')
                measurement['location_name'] = loc.get('name')
    
    return all_measurements

def convert_to_dataframe(measurements):
    """Convertit les mesures en DataFrame pandas"""
    records = []
    
    for m in measurements:
        try:
            # Extraction des coordonnées
            coords = m.get('coordinates', {})
            lat = coords.get('latitude')
            lon = coords.get('longitude')
            
            # Récupérer les informations de pays
            country_info = m.get('country', {})
            if isinstance(country_info, dict):
                country_code = country_info.get('code')
                country_name = country_info.get('name')
            else:
                country_code = country_info
                country_name = None
            
            # Récupérer le paramètre (polluant)
            sensors = m.get('sensors', [])
            parameter_name = None
            parameter_units = None
            if sensors and len(sensors) > 0:
                sensor = sensors[0]
                parameter_info = sensor.get('parameter', {})
                if isinstance(parameter_info, dict):
                    parameter_name = parameter_info.get('name')
                    parameter_units = parameter_info.get('units')
            
            # Si pas trouvé dans sensors, chercher ailleurs
            if not parameter_name:
                # Dans l'API v3, le paramètre peut être au niveau racine
                if 'parameter' in m:
                    param = m['parameter']
                    if isinstance(param, dict):
                        parameter_name = param.get('name')
                        parameter_units = param.get('units')
            
            record = {
                'Country Code': country_code,
                'Country Label': country_name or m.get('location_name'),
                'City': m.get('city'),
                'Location': m.get('location_name') or m.get('location'),
                'Coordinates': f"{lat},{lon}" if lat and lon else None,
                'Pollutant': parameter_name,
                'Value': m.get('value'),
                'Unit': parameter_units,
                'Last Updated': m.get('datetime', {}).get('utc') if isinstance(m.get('datetime'), dict) else m.get('datetime'),
                'Source Name': sensors[0].get('name') if sensors else None
            }
            records.append(record)
        except Exception as e:
            print(f"Erreur lors du traitement d'une mesure: {e}")
            continue
    
    return pd.DataFrame(records)

def convert_to_geojson(measurements):
    """Convertit les mesures en format GeoJSON"""
    features = []
    
    for m in measurements:
        try:
            coords = m.get('coordinates', {})
            lat = coords.get('latitude')
            lon = coords.get('longitude')
            
            if lat is None or lon is None:
                continue
            
            # Récupérer les informations de pays
            country_info = m.get('country', {})
            if isinstance(country_info, dict):
                country_code = country_info.get('code')
                country_name = country_info.get('name')
            else:
                country_code = country_info
                country_name = None
            
            # Récupérer le paramètre (polluant)
            sensors = m.get('sensors', [])
            parameter_name = None
            parameter_units = None
            sensor_name = None
            
            if sensors and len(sensors) > 0:
                sensor = sensors[0]
                sensor_name = sensor.get('name')
                parameter_info = sensor.get('parameter', {})
                if isinstance(parameter_info, dict):
                    parameter_name = parameter_info.get('name')
                    parameter_units = parameter_info.get('units')
            
            # Si pas trouvé dans sensors, chercher ailleurs
            if not parameter_name and 'parameter' in m:
                param = m['parameter']
                if isinstance(param, dict):
                    parameter_name = param.get('name')
                    parameter_units = param.get('units')
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "country": country_code,
                    "city": m.get('city'),
                    "location": m.get('location_name') or m.get('location'),
                    "measurements_parameter": parameter_name,
                    "measurements_sourcename": sensor_name,
                    "measurements_unit": parameter_units,
                    "measurements_value": m.get('value'),
                    "measurements_lastupdated": m.get('datetime', {}).get('utc') if isinstance(m.get('datetime'), dict) else m.get('datetime'),
                    "country_name_en": country_name
                }
            }
            features.append(feature)
        except Exception as e:
            print(f"Erreur lors de la création d'une feature: {e}")
            continue
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

def save_data(measurements, output_dir='../../data/raw'):
    """Sauvegarde les données en CSV et GeoJSON"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Sauvegarder en CSV
    print("\n💾 Conversion en DataFrame...")
    df = convert_to_dataframe(measurements)
    csv_path = os.path.join(output_dir, 'rawdata.csv')
    df.to_csv(csv_path, index=False, sep=';', encoding='utf-8')
    print(f"✓ CSV sauvegardé: {csv_path} ({len(df)} lignes)")
    
    # Sauvegarder en GeoJSON
    print("\n💾 Conversion en GeoJSON...")
    geojson = convert_to_geojson(measurements)
    geojson_path = os.path.join(output_dir, 'rawdata.geojson')
    with open(geojson_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    print(f"✓ GeoJSON sauvegardé: {geojson_path} ({len(geojson['features'])} features)")
    
    # Statistiques
    print("\n📊 STATISTIQUES:")
    print(f"  - Total de mesures: {len(measurements)}")
    print(f"\n  Répartition par polluant:")
    if not df.empty:
        for pollutant, count in df['Pollutant'].value_counts().items():
            print(f"    • {pollutant}: {count}")
        print(f"\n  Répartition par pays (top 10):")
        for country, count in df['Country Label'].value_counts().head(10).items():
            print(f"    • {country}: {count}")

if __name__ == "__main__":
    print("="*60)
    print("🌍 RÉCUPÉRATION DES DONNÉES OPENAQ")
    print("="*60)
    
    # Option 1: Récupérer pour quelques pays spécifiques (plus rapide)
    #print("\n🔧 Mode: Pays sélectionnés")
    #countries_selection = ['FR', 'US', 'CN', 'IN', 'GB', 'DE', 'ES', 'IT', 'JP', 'BR']
    
    # Option 2: Pour tous les pays (décommenter pour utiliser)
    print("\n🔧 Mode: Tous les pays")
    countries_selection = None
    
    # Récupérer les données
    measurements = fetch_all_data(
        parameters=['pm25', 'pm10', 'no2', 'so2', 'o3', 'co'],
        countries=countries_selection,
        max_pages=100  # Limiter à 3 pages par combinaison (3000 mesures max)
    )
    
    if measurements:
        print(f"\n✓ Total de {len(measurements)} mesures récupérées")
        save_data(measurements)
        print("\n✅ RÉCUPÉRATION TERMINÉE!")
    else:
        print("\n❌ Aucune donnée récupérée")
    
    print("="*60)