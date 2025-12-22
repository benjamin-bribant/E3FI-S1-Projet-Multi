import pandas as pd
import numpy as np
from datetime import datetime

def nettoyer_donnees_pollution(fichier_entree, fichier_sortie='../../data/cleaned/cleaneddata.csv'):
    """
    Nettoie les données de pollution en filtrant les polluants et en traitant les valeurs manquantes.
    
    Parameters:
    -----------
    fichier_entree : str
        Chemin vers le fichier CSV d'entrée
    fichier_sortie : str
        Chemin vers le fichier CSV nettoyé (par défaut: 'donnees_pollution_nettoyees.csv')
    """
    
    print("📥 Chargement des données...")
    # Charger le CSV avec le bon séparateur (point-virgule)
    df = pd.read_csv(fichier_entree, sep=';', encoding='utf-8')
    
    print(f"✅ Données chargées : {len(df)} lignes")
    print(f"📊 Colonnes : {', '.join(df.columns)}")
    
    # Afficher les informations de base
    print(f"\n🔍 Aperçu des données avant nettoyage :")
    print(f"   - Nombre total de lignes : {len(df)}")
    print(f"   - Polluants uniques : {df['Pollutant'].nunique()}")
    print(f"   - Pays uniques : {df['Country Label'].nunique()}")
    
    # Liste des polluants à garder
    polluants_gardes = ['PM2.5', 'PM10', 'CO', 'NO2', 'SO2', 'O3']
    
    print(f"\n🔧 Filtrage des polluants...")
    print(f"   Polluants conservés : {', '.join(polluants_gardes)}")
    
    # Filtrer uniquement les polluants souhaités
    df_filtre = df[df['Pollutant'].isin(polluants_gardes)].copy()
    
    print(f"   ✅ {len(df_filtre)} lignes conservées sur {len(df)} ({len(df_filtre)/len(df)*100:.1f}%)")
    
    # Nettoyage des coordonnées
    print(f"\n🌍 Traitement des coordonnées...")
    def extraire_coordonnees(coord_str):
        """Extrait latitude et longitude d'une chaîne de coordonnées"""
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
    
    # Vérifier que la conversion a fonctionné
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
    
    # Suppression des lignes avec des valeurs manquantes critiques
    print(f"\n🧹 Suppression des valeurs manquantes critiques...")
    avant_nettoyage = len(df_filtre)
    
    df_filtre = df_filtre.dropna(subset=['Value', 'Latitude', 'Longitude', 'Country Label'])
    
    apres_nettoyage = len(df_filtre)
    print(f"   ✅ {avant_nettoyage - apres_nettoyage} lignes supprimées")
    print(f"   📊 {apres_nettoyage} lignes restantes")
    
    # Suppression des valeurs aberrantes (valeurs négatives)
    df_filtre = df_filtre[df_filtre['Value'] >= 0]
    
    # Réorganiser les colonnes pour plus de clarté
    colonnes_finales = [
        'Country Code', 'Country Label', 'City', 'Location', 
        'Latitude', 'Longitude', 'Pollutant', 'Value', 'Unit',
        'Date', 'Year', 'Month', 'Last Updated', 'Source Name'
    ]
    
    df_filtre = df_filtre[colonnes_finales]
    
    # Tri par pays et date
    df_filtre = df_filtre.sort_values(['Country Label', 'Last Updated'], ascending=[True, False])
    
    # Sauvegarder le fichier nettoyé
    print(f"\n💾 Sauvegarde des données nettoyées...")
    df_filtre.to_csv(fichier_sortie, index=False, encoding='utf-8')
    print(f"   ✅ Fichier sauvegardé : {fichier_sortie}")
    
    # Statistiques finales
    print(f"\n📈 STATISTIQUES FINALES :")
    print(f"   - Nombre total de mesures : {len(df_filtre)}")
    print(f"   - Pays : {df_filtre['Country Label'].nunique()}")
    print(f"   - Villes : {df_filtre['City'].nunique()}")
    print(f"   - Période : {df_filtre['Year'].min()} - {df_filtre['Year'].max()}")
    print(f"\n   Répartition par polluant :")
    for polluant in polluants_gardes:
        count = len(df_filtre[df_filtre['Pollutant'] == polluant])
        print(f"      • {polluant:6s} : {count:8d} mesures")
    
    print(f"\n   Top 5 pays avec le plus de mesures :")
    top_pays = df_filtre['Country Label'].value_counts().head()
    for pays, count in top_pays.items():
        print(f"      • {pays:20s} : {count:8d} mesures")
    
    return df_filtre


# Exemple d'utilisation
if __name__ == "__main__":
    # Remplacez 'votre_fichier.csv' par le chemin vers votre fichier
    fichier_entree = '../../data/raw/rawdata.csv'
    
    try:
        df_propre = nettoyer_donnees_pollution(fichier_entree)
        print("\n✨ Nettoyage terminé avec succès !")
        
        # Afficher un aperçu des données nettoyées
        print("\n👀 Aperçu des premières lignes :")
        print(df_propre.head(10))
        
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier '{fichier_entree}' n'a pas été trouvé.")
        print("   Assurez-vous que le fichier est dans le même dossier que ce script.")
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage : {str(e)}")