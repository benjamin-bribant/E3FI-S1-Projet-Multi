"""
Script de récupération des données via l'api v3 d'OpenAQ.
Récupère les données et les met dans des fichiers au format CSV et GeoJSON.
"""
import os
import requests
import pandas as pd
import json
from dotenv import load_dotenv
import time

load_dotenv()

BASE_URL = "https://api.openaq.org/v3"
API_KEY = os.getenv('OPENAQ_API_KEY')

if not API_KEY:
    raise ValueError("Clé API manquante ! Vérifier que OPENAQ_API_KEY est dans le fichier .env")

def get_parameter_id(parameter):
    """
    Convertit le nom d'un polluant en ID numérique utilisé par l'API OpenAQ v3.

    :param parameter str: Nom du polluant (ex. 'pm25', 'no2', 'o3')
    :returns int: ID du paramètre correspondant, ou 2 (pm25) par défaut si non reconnu
    """
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
    """
    Récupère la liste de tous les pays disponibles via l'API OpenAQ v3.

    :returns list: Liste de dictionnaires représentant chaque pays, ou une liste vide en cas d'erreur
    """
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
    Récupère une page de locations depuis l'API OpenAQ v3.

    :param limit int: Nombre maximum de résultats par page (max 1000)
    :param country str: Code pays ISO 2 lettres pour filtrer (ex. 'FR', 'US'), ou None pour tous
    :param page int: Numéro de page pour la pagination
    :returns tuple: Un tuple (results, meta) où results est la liste des locations
                    et meta un dictionnaire de métadonnées de pagination
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
    Récupère les dernières mesures disponibles pour un polluant donné.

    :param parameter str: Nom du polluant ('pm25', 'pm10', 'no2', 'so2', 'o3', 'co')
    :param limit int: Nombre maximum de résultats par page (max 1000)
    :param page int: Numéro de page pour la pagination
    :returns tuple: Un tuple (results, meta) où results est la liste des mesures
                    et meta un dictionnaire de métadonnées de pagination
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

def _extract_fields(m):
    """
    Extrait les champs communs d'un dictionnaire de mesure brut retourné par l'endpoint /latest.
    Cherche les informations dans 'location', 'parameter', 'sensors' et les champs racine,
    dans cet ordre de priorité.

    :param m dict: Dictionnaire brut d'une mesure telle que retournée par l'API
    :returns dict: Dictionnaire avec les clés country_code, country_name, city, location_name,
                   lat, lon, parameter_name, parameter_units, source_name, value, last_updated
    """
    coords = m.get('coordinates', {}) or {}
    lat = coords.get('latitude')
    lon = coords.get('longitude')

    location = m.get('location', {}) or {}
    country_obj = location.get('country') or m.get('country') or {}

    if isinstance(country_obj, dict):
        country_code = country_obj.get('code')
        country_name = country_obj.get('name')
    else:
        country_code = country_obj
        country_name = None

    city = location.get('city') or m.get('city')
    location_name = location.get('name') or m.get('location_name') or m.get('location')

    parameter_name = None
    parameter_units = None
    source_name = None

    param_obj = m.get('parameter') or {}
    if isinstance(param_obj, dict) and param_obj.get('name'):
        parameter_name = param_obj.get('name')
        parameter_units = param_obj.get('units')

    sensors = m.get('sensors') or []
    if sensors:
        sensor = sensors[0]
        source_name = sensor.get('name')
        if not parameter_name:
            sensor_param = sensor.get('parameter') or {}
            if isinstance(sensor_param, dict):
                parameter_name = sensor_param.get('name')
                parameter_units = sensor_param.get('units')

    if not source_name:
        source_obj = m.get('source') or {}
        if isinstance(source_obj, dict):
            source_name = source_obj.get('name')

    dt = m.get('datetime')
    last_updated = dt.get('utc') if isinstance(dt, dict) else dt

    return {
        'country_code': country_code,
        'country_name': country_name,
        'city': city,
        'location_name': location_name,
        'lat': lat,
        'lon': lon,
        'parameter_name': parameter_name,
        'parameter_units': parameter_units,
        'source_name': source_name,
        'value': m.get('value'),
        'last_updated': last_updated,
    }

def fetch_all_data(parameters=['pm25', 'pm10', 'no2', 'so2', 'o3', 'co'], 
                   countries=None, max_pages=3):
    """
    Récupère toutes les dernières mesures pour plusieurs polluants, toutes pages confondues.
    Si une liste de pays est fournie, les locations sont d'abord récupérées pour filtrer
    les mesures en conséquence.

    :param parameters list: Liste des noms de polluants à récupérer
    :param countries list: Liste des codes pays ISO 2 lettres pour filtrer, ou None pour tous les pays
    :param max_pages int: Nombre maximum de pages à parcourir par polluant
    :returns list: Liste de dictionnaires bruts de mesures
    """
    all_measurements = []
    all_locations = []
    
    total = len(parameters)
    current = 0
    
    if countries:
        for country in countries:
            print(f"  - {country}...")
            page = 1
            while page <= 5:
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
        
        print(f"{len(all_locations)} locations trouvées")
    
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
            
            if countries and all_locations:
                location_ids = {loc['id'] for loc in all_locations}
                results = [r for r in results if r.get('locationsId') in location_ids]
            
            all_measurements.extend(results)
            print(f"  Page {page}: {len(results)} mesures récupérées (Total: {len(all_measurements)})")
            
            found = meta.get('found', 0)
            if len(results) < 1000 or page * 1000 >= found:
                break
            
            page += 1
            time.sleep(0.5)
    
    if all_locations:
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
    """
    Convertit une liste de dictionnaires de mesures bruts en un DataFrame pandas
    structuré et lisible.

    :param measurements list: Liste de dictionnaires de mesures tels que retournés par fetch_all_data
    :returns DataFrame: DataFrame pandas avec les colonnes Country Code, City, Location,
                        Coordinates, Pollutant, Source Name, Unit, Value, Last Updated, Country Label
    """
    records = []
    
    for m in measurements:
        try:
            f = _extract_fields(m)

            record = {
                'Country Code': f['country_code'],
                'City': f['city'],
                'Location': f['location_name'],
                'Coordinates': f"{f['lat']}, {f['lon']}" if f['lat'] is not None and f['lon'] is not None else None,
                'Pollutant': f['parameter_name'],
                'Source Name': f['source_name'],
                'Unit': f['parameter_units'],
                'Value': f['value'],
                'Last Updated': f['last_updated'],
                'Country Label': f['country_name'],
            }
            records.append(record)
        except Exception as e:
            print(f"Erreur lors du traitement d'une mesure: {e}")
            continue
    
    return pd.DataFrame(records)

def convert_to_geojson(measurements):
    """
    Convertit une liste de dictionnaires de mesures bruts en un objet GeoJSON.

    :param measurements list: Liste de dictionnaires de mesures tels que retournés par fetch_all_data
    :returns dict: Dictionnaire GeoJSON valide contenant une FeatureCollection de points géolocalisés
    """
    features = []
    
    for m in measurements:
        try:
            f = _extract_fields(m)

            if f['lat'] is None or f['lon'] is None:
                continue
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [f['lon'], f['lat']]
                },
                "properties": {
                    "country": f['country_code'],
                    "city": f['city'],
                    "location": f['location_name'],
                    "measurements_parameter": f['parameter_name'],
                    "measurements_sourcename": f['source_name'],
                    "measurements_unit": f['parameter_units'],
                    "measurements_value": f['value'],
                    "measurements_lastupdated": f['last_updated'],
                    "country_name_en": f['country_name'],
                }
            }
            features.append(feature)
        except Exception as e:
            print(f"Erreur lors de la création d'une feature : {e}")
            continue
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

def save_data(measurements, output_dir='../../data/raw'):
    """
    Sauvegarde les mesures en CSV et GeoJSON.

    :param measurements list: Liste de dictionnaires de mesures
    :param output_dir str: Chemin du répertoire de sortie (créé s'il n'existe pas)
    :returns None
    """
    os.makedirs(output_dir, exist_ok=True)
    
    df = convert_to_dataframe(measurements)
    csv_path = os.path.join(output_dir, 'rawdata.csv')
    df.to_csv(csv_path, index=False, sep=';', encoding='utf-8')
    print(f"CSV sauvegardé: {csv_path} ({len(df)} lignes)")
    
    geojson = convert_to_geojson(measurements)
    geojson_path = os.path.join(output_dir, 'rawdata.geojson')
    with open(geojson_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, separators=(',', ':'))
    print(f"GeoJSON sauvegardé: {geojson_path} ({len(geojson['features'])} features)")

if __name__ == "__main__":
    
    countries_selection = None
    
    measurements = fetch_all_data(
        parameters=['pm25', 'pm10', 'no2', 'so2', 'o3', 'co'],
        countries=countries_selection,
        max_pages=100
    )
    
    if measurements:
        print(f"\nTotal de {len(measurements)} mesures récupérées")
        save_data(measurements)
        print("\nRécupération terminée !")
    else:
        print("\nAucune donnée récupérée")