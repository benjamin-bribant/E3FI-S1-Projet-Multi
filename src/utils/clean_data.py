"""
Script de nettoyage des données.
Supprime les lignes avec des données manquantes ou inutiles,
pour pouvoir être utilisées dans le dashboard final.
"""
import pandas as pd
import numpy as np
import json

def nettoyer_csv(fichier_entree, fichier_sortie='../../data/cleaned/cleaneddata.csv'):
    """
    Nettoie les données de pollution au format CSV : filtrage des polluants,
    extraction des coordonnées, conversion des dates, suppression des valeurs
    manquantes ou négatives, puis sauvegarde avec une sélection et un tri des colonnes.

    :param fichier_entree str: Chemin vers le fichier CSV d'entrée
    :param fichier_sortie str: Chemin vers le fichier CSV nettoyé en sortie
    :returns DataFrame: DataFrame pandas nettoyé et trié
    """
    
    df = pd.read_csv(fichier_entree, sep=';', encoding='utf-8')
    
    polluants_gardes = ['PM2.5', 'PM10', 'CO', 'NO2', 'SO2', 'O3']
    
    print("\nFiltrage des polluants...")
    df_filtre = df[df['Pollutant'].isin(polluants_gardes)].copy()
    
    print(f"{len(df_filtre)} lignes conservées sur {len(df)} ({len(df_filtre)/len(df)*100:.1f}%)")
    
    def extraire_coordonnees(coord_str):
        """
        Parse une chaîne de coordonnées au format 'lat, lon' en deux flottants.
        Retourne (NaN, NaN) si la chaîne est absente ou mal formée.

        :param coord_str str: Chaîne de caractères au format 'latitude, longitude'
        :returns tuple: Tuple (latitude, longitude) sous forme de floats, ou (NaN, NaN)
        """
        try:
            if pd.isna(coord_str):
                return np.nan, np.nan
            coords = str(coord_str).split(',')
            lat = float(coords[0].strip())
            lon = float(coords[1].strip())
            return lat, lon
        except:
            return np.nan, np.nan
    
    df_filtre[['Latitude', 'Longitude']] = df_filtre['Coordinates'].apply(
        lambda x: pd.Series(extraire_coordonnees(x))
    )
    
    df_filtre['Last Updated'] = pd.to_datetime(df_filtre['Last Updated'], errors='coerce', utc=True)
    
    if pd.api.types.is_datetime64_any_dtype(df_filtre['Last Updated']):
        df_filtre['Date'] = df_filtre['Last Updated'].dt.date
        df_filtre['Year'] = df_filtre['Last Updated'].dt.year
        df_filtre['Month'] = df_filtre['Last Updated'].dt.month
    else:
        print("Problème de conversion des dates")
        df_filtre['Date'] = None
        df_filtre['Year'] = None
        df_filtre['Month'] = None
    
    df_filtre['Value'] = pd.to_numeric(df_filtre['Value'], errors='coerce')
    
    print("\nSuppression des valeurs manquantes critiques...")
    avant = len(df_filtre)
    df_filtre = df_filtre.dropna(subset=['Value', 'Latitude', 'Longitude', 'Country Label'])
    df_filtre = df_filtre[df_filtre['Value'] >= 0]
    print(f"{avant - len(df_filtre)} lignes supprimées")
    
    colonnes_finales = [
        'Country Code', 'Country Label', 'City', 'Location', 
        'Latitude', 'Longitude', 'Pollutant', 'Value', 'Unit',
        'Date', 'Year', 'Month', 'Last Updated', 'Source Name'
    ]
    df_filtre = df_filtre[colonnes_finales]
    df_filtre = df_filtre.sort_values(['Country Label', 'Last Updated'], ascending=[True, False])
    
    df_filtre.to_csv(fichier_sortie, index=False, encoding='utf-8')
    print(f"Fichier sauvegardé : {fichier_sortie}")
    
    return df_filtre


def nettoyer_geojson(fichier_entree, fichier_sortie='../../data/cleaned/cleaneddata.geojson'):
    """
    Nettoie les données de pollution au format GeoJSON : filtrage des polluants,
    validation de la géométrie et des coordonnées, suppression des features avec
    une valeur manquante ou négative, puis sauvegarde.

    :param fichier_entree str: Chemin vers le fichier GeoJSON d'entrée
    :param fichier_sortie str: Chemin vers le fichier GeoJSON nettoyé en sortie
    :returns dict: Dictionnaire GeoJSON nettoyé
    """
    
    with open(fichier_entree, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    polluants_gardes = ['PM2.5', 'PM10', 'CO', 'NO2', 'SO2', 'O3']
    
    print("\nFiltrage des polluants...")
    features_filtrees = []
    
    for feature in data['features']:
        try:
            if not feature.get('properties') or not feature.get('geometry'):
                continue
            
            props = feature['properties']
            geometry = feature['geometry']
            
            if not geometry or not geometry.get('coordinates'):
                continue
            
            coords = geometry['coordinates']
            polluant = props.get('measurements_parameter')
            value = props.get('measurements_value')
            
            if (polluant in polluants_gardes and 
                value is not None and 
                value >= 0 and
                coords and len(coords) == 2 and
                coords[0] is not None and coords[1] is not None):
                
                features_filtrees.append(feature)
        except (KeyError, TypeError, AttributeError) as e:
            continue
    
    print(f"{len(features_filtrees)} features conservées sur {len(data['features'])} ({len(features_filtrees)/len(data['features'])*100:.1f}%)")
    
    geojson_propre = {
        "type": "FeatureCollection",
        "features": features_filtrees
    }
    
    with open(fichier_sortie, 'w', encoding='utf-8') as f:
        json.dump(geojson_propre, f, ensure_ascii=False, indent=2)
    
    print(f"Fichier sauvegardé : {fichier_sortie}")
    
    return geojson_propre


if __name__ == "__main__":
    
    # Nettoyer un fichier CSV
    try:
        df_csv = nettoyer_csv('../../data/raw/rawdata.csv')
        print("\nNettoyage CSV terminé avec succès !")
    except FileNotFoundError:
        print("Fichier CSV '../../data/raw/rawdata.csv' non trouvé")
    except Exception as e:
        print(f"Erreur CSV : {str(e)}")
    
    # Nettoyer un fichier GeoJSON
    try:
        geojson_propre = nettoyer_geojson('../../data/raw/rawdata.geojson')
        print("\nNettoyage GeoJSON terminé avec succès !")
        
        
    except FileNotFoundError:
        print("Fichier GeoJSON '../../data/raw/rawdata.geojson' non trouvé")
    except Exception as e:
        print(f"Erreur GeoJSON : {str(e)}")
    
    print("Nettoyage terminé !")