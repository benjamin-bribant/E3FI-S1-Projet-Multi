import pandas as pd
import numpy as np
import json
from datetime import datetime

def nettoyer_csv(fichier_entree, fichier_sortie='../../data/cleaned/cleaneddata.csv'):
    """
    Nettoie les données de pollution au format CSV.
    
    Parameters:
    -----------
    fichier_entree : str
        Chemin vers le fichier CSV d'entrée
    fichier_sortie : str
        Chemin vers le fichier CSV nettoyé
    """
    
    print("📥 Chargement des données CSV...")
    df = pd.read_csv(fichier_entree, sep=';', encoding='utf-8')
    
    print(f"✅ Données chargées : {len(df)} lignes")
    
    # Liste des polluants à garder
    polluants_gardes = ['PM2.5', 'PM10', 'CO', 'NO2', 'SO2', 'O3']
    
    print(f"\n🔧 Filtrage des polluants...")
    df_filtre = df[df['Pollutant'].isin(polluants_gardes)].copy()
    
    print(f"   ✅ {len(df_filtre)} lignes conservées sur {len(df)} ({len(df_filtre)/len(df)*100:.1f}%)")
    
    # Traitement des coordonnées
    print(f"\n🌍 Traitement des coordonnées...")
    def extraire_coordonnees(coord_str):
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
    
    # Conversion de la date avec gestion des fuseaux horaires
    print(f"📅 Conversion des dates...")
    df_filtre['Last Updated'] = pd.to_datetime(df_filtre['Last Updated'], errors='coerce', utc=True)
    
    if pd.api.types.is_datetime64_any_dtype(df_filtre['Last Updated']):
        df_filtre['Date'] = df_filtre['Last Updated'].dt.date
        df_filtre['Year'] = df_filtre['Last Updated'].dt.year
        df_filtre['Month'] = df_filtre['Last Updated'].dt.month
    else:
        print("⚠️  Attention : problème de conversion des dates")
        df_filtre['Date'] = None
        df_filtre['Year'] = None
        df_filtre['Month'] = None
    
    # Conversion des valeurs en numérique
    print(f"🔢 Conversion des valeurs...")
    df_filtre['Value'] = pd.to_numeric(df_filtre['Value'], errors='coerce')
    
    # Suppression des valeurs manquantes critiques
    print(f"\n🧹 Suppression des valeurs manquantes critiques...")
    avant = len(df_filtre)
    df_filtre = df_filtre.dropna(subset=['Value', 'Latitude', 'Longitude', 'Country Label'])
    df_filtre = df_filtre[df_filtre['Value'] >= 0]
    print(f"   ✅ {avant - len(df_filtre)} lignes supprimées")
    
    # Réorganiser les colonnes
    colonnes_finales = [
        'Country Code', 'Country Label', 'City', 'Location', 
        'Latitude', 'Longitude', 'Pollutant', 'Value', 'Unit',
        'Date', 'Year', 'Month', 'Last Updated', 'Source Name'
    ]
    df_filtre = df_filtre[colonnes_finales]
    df_filtre = df_filtre.sort_values(['Country Label', 'Last Updated'], ascending=[True, False])
    
    # Sauvegarde
    df_filtre.to_csv(fichier_sortie, index=False, encoding='utf-8')
    print(f"   💾 Fichier sauvegardé : {fichier_sortie}")
    
    return df_filtre


def nettoyer_geojson(fichier_entree, fichier_sortie='../../data/cleaned/cleaneddata.geojson'):
    """
    Nettoie les données de pollution au format GeoJSON.
    
    Parameters:
    -----------
    fichier_entree : str
        Chemin vers le fichier GeoJSON d'entrée
    fichier_sortie : str
        Chemin vers le fichier GeoJSON nettoyé
    """
    
    print("\n" + "="*60)
    print("📥 Chargement des données GeoJSON...")
    
    with open(fichier_entree, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Données chargées : {len(data['features'])} features")
    
    # Liste des polluants à garder
    polluants_gardes = ['PM2.5', 'PM10', 'CO', 'NO2', 'SO2', 'O3']
    
    print(f"\n🔧 Filtrage des polluants...")
    features_filtrees = []
    
    for feature in data['features']:
        try:
            # Vérifier que la structure de base existe
            if not feature.get('properties') or not feature.get('geometry'):
                continue
            
            props = feature['properties']
            geometry = feature['geometry']
            
            # Vérifier que les coordonnées existent
            if not geometry or not geometry.get('coordinates'):
                continue
            
            coords = geometry['coordinates']
            polluant = props.get('measurements_parameter')
            value = props.get('measurements_value')
            
            # Vérifications
            if (polluant in polluants_gardes and 
                value is not None and 
                value >= 0 and
                coords and len(coords) == 2 and
                coords[0] is not None and coords[1] is not None):
                
                features_filtrees.append(feature)
        except (KeyError, TypeError, AttributeError) as e:
            # Ignorer les features mal formées
            continue
    
    print(f"   ✅ {len(features_filtrees)} features conservées sur {len(data['features'])} ({len(features_filtrees)/len(data['features'])*100:.1f}%)")
    
    # Créer le nouveau GeoJSON
    geojson_propre = {
        "type": "FeatureCollection",
        "features": features_filtrees
    }
    
    # Sauvegarder
    print(f"\n💾 Sauvegarde des données nettoyées...")
    with open(fichier_sortie, 'w', encoding='utf-8') as f:
        json.dump(geojson_propre, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ Fichier sauvegardé : {fichier_sortie}")
    
    # Statistiques
    print(f"\n📈 STATISTIQUES GEOJSON :")
    print(f"   - Nombre total de mesures : {len(features_filtrees)}")
    
    # Compter par polluant
    compteur_polluants = {}
    compteur_pays = {}
    
    for feature in features_filtrees:
        polluant = feature['properties']['measurements_parameter']
        pays = feature['properties'].get('country_name_en', 'Inconnu')
        
        compteur_polluants[polluant] = compteur_polluants.get(polluant, 0) + 1
        compteur_pays[pays] = compteur_pays.get(pays, 0) + 1
    
    print(f"\n   Répartition par polluant :")
    for polluant in polluants_gardes:
        count = compteur_polluants.get(polluant, 0)
        print(f"      • {polluant:6s} : {count:8d} mesures")
    
    print(f"\n   Top 5 pays avec le plus de mesures :")
    top_pays = sorted(compteur_pays.items(), key=lambda x: x[1], reverse=True)[:5]
    for pays, count in top_pays:
        print(f"      • {pays:20s} : {count:8d} mesures")
    
    return geojson_propre


# Exemple d'utilisation
if __name__ == "__main__":
    print("="*60)
    print("🧹 NETTOYAGE DES DONNÉES DE POLLUTION")
    print("="*60)
    
    # Option 1 : Nettoyer un fichier CSV
    try:
        print("\n📋 NETTOYAGE CSV")
        print("="*60)
        df_csv = nettoyer_csv('../../data/raw/rawdata.csv')
        print("\n✨ Nettoyage CSV terminé avec succès !")
    except FileNotFoundError:
        print("❌ Fichier CSV '../../data/raw/rawdata.csv' non trouvé")
    except Exception as e:
        print(f"❌ Erreur CSV : {str(e)}")
    
    # Option 2 : Nettoyer un fichier GeoJSON
    try:
        print("\n\n🗺️  NETTOYAGE GEOJSON")
        geojson_propre = nettoyer_geojson('../../data/raw/rawdata.geojson')
        print("\n✨ Nettoyage GeoJSON terminé avec succès !")
        
        
    except FileNotFoundError:
        print("❌ Fichier GeoJSON '../../data/raw/rawdata.geojson' non trouvé")
    except Exception as e:
        print(f"❌ Erreur GeoJSON : {str(e)}")
    
    print("\n" + "="*60)
    print("✅ NETTOYAGE TERMINÉ")
    print("="*60)