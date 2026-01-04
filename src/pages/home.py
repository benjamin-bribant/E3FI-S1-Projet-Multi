import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Configuration de l'API OpenAQ v3
BASE_URL = "https://api.openaq.org/v3"

API_KEY = os.getenv('OPENAQ_API_KEY')


if not API_KEY :
    raise ValueError("Clé API manquante! Vérifier que API_KEY est dans le fichier .env")


def get_latest_measurements(limit=1000, parameter='pm25', country=None):
    """
    Récupère les dernières mesures de qualité de l'air (API v3)
     
    Parameters:
    - limit: nombre max de résultats (max 1000 par requête en v3)
    - parameter: 'pm25', 'pm10', 'no2', 'so2', 'o3', 'co'
    - country: code pays ISO (ex: 'FR', 'US', 'IN')
    """
    url = f"{BASE_URL}/locations/2178"
    
    headers = {
        'X-API-Key': API_KEY
    }
    
    params = {
        'limit': limit,
        'parameters_id': get_parameter_id(parameter)
    }
    
    if country:
        params['countries_id'] = country.upper()
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
        else:
            print(f"Erreur API: {response.status_code}")
            print(f"Message: {response.text}")
            return []
    except Exception as e:
        print(f"Erreur de connexion: {e}")
        return []

def get_parameter_id(parameter):
    """Convertit le nom du paramètre en ID pour l'API v3"""
    mapping = {
        'pm25': 2,
        'pm10': 1,
        'no2': 3,
        'so2': 5,
        'o3': 4,
        'co': 6
    }
    return mapping.get(parameter.lower(), 2)

def get_measurements_by_location(sensors_id, date_from, date_to, parameter='pm25'):
    """
    Récupère l'historique pour un capteur spécifique (API v3)
    """
    url = f"{BASE_URL}/measurements"
    
    headers = {
        'X-API-Key': API_KEY
    }
    
    params = {
        'sensors_id': sensors_id,
        'parameters_id': get_parameter_id(parameter),
        'date_from': date_from,
        'date_to': date_to,
        'limit': 1000
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
        else:
            print(f"Erreur API: {response.status_code}")
            print(f"Message: {response.text}")
            return []
    except Exception as e:
        print(f"Erreur de connexion: {e}")
        return []

# Exemple d'utilisation
print("Récupération des données...")
raw_data = get_latest_measurements(limit=1000, parameter='co', country='FR')

if raw_data:
    print(f"✓ {len(raw_data)} mesures récupérées")
    # Afficher un échantillon
    if len(raw_data) > 0:
        print("\nExemple de données:")
        print(raw_data[0])
else:
    print("Aucune donnée récupérée")