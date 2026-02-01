# Dashboard - Évolution de la Pollution Mondiale

## User Guide

### Prérequis

- Python 3
- Un navigateur web moderne

### Installation

1. Clonez le dépôt :

```bash
git clone https://github.com/benjamin-bribant/E3FI-S1-Projet-Multi
cd E3FI-S1-Projet-Multi
```

2. Créer ou activer l'environnement virtuel venv :

**Windows :**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**Linux/Mac :**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Installez les dépendances :

```bash
pip install -r requirements.txt
```

4. Lancez l'application en mode développement :

```bash
python main.py
```

5. Ouvrez votre navigateur à : **http://127.0.0.1:8050/**


### Utilisation

- **Filtres** : Sélectionnez les années (slider) ou types de polluants (boutons) pour affiner les visualisations
- **Export** : Cliquez sur l'icône appareil photo pour exporter les graphiques en format PNG

****

## Data

### Sources de données

Les données utilisées proviennent de sources officielles et reconnues :


1. **OpenAQ (Open Air Quality)**
    - **Description** : Base de données mondiale collaborative de qualité de l'air en temps réel
    - **Période couverte** : 2016-2025
    - **Format** : CSV, GeoJSON
    - **Licence** : CC BY 4.0
    - **URL** : https://public.opendatasoft.com/explore/assets/openaq/

### Structure des données
---
Les fichiers de données sont organisés dans le dossier `/data` :

```
|-- data                                  # les données
│   |-- cleaned
│   │   |-- cleaneddata.csv
│   |-- raw
│   │   |-- rawdata.csv
```

### Variables principales

### Variables principales

| Polluant | Description | Unité | Seuil OMS |
|----------|-------------|-------|-----------|
| **PM2.5** | Particules fines (≤2.5 µm) | µg/m³ | 5 |
| **PM10** | Particules inhalables (≤10 µm) | µg/m³ | 15 |
| **NO2** | Dioxyde d'azote | µg/m³ | 10 |
| **SO2** | Dioxyde de soufre | µg/m³ | 40 |
| **O3** | Ozone troposphérique | µg/m³ | 100 |
| **CO** | Monoxyde de carbone | µg/m³ | 4000 |


## Developer Guide

### Stack technique

| Catégorie | Technologies |
|-----------|-------------|
| **Framework** | Dash 2.x (Python) |
| **Visualisation** | Plotly Graph Objects |
| **Data Processing** | Pandas, GeoPandas |
| **Caching** | Flask-Caching |
| **API** | OpenAQ v3 |
| **Styling** | CSS3 custom |


### Architecture du projet

```

E3FI-S1-Projet-Multi
|   
+---.venv
|    |-- *
+---assets
|   +---css
|   |       buttons.css
|   |       footer.css
|   |       navbar.css
|   |       style.css
|   |       
|   +---img
|   |       bar_char_icon.svg
|   |       globe_icon.svg
+---data
|   +---cleaned
|   |       cleaneddata.csv
|   |       cleaneddata.geojson
|   |       
|   \---raw
|           rawdata.csv
|           rawdata.geojson
|           
+---src
|   +---components
|   |   |   component.py
|   |   |   footer.py
|   |   |   graphique_vie_pays.py   # Graphique espérance de vie
|   |   |   header.py
|   |   |   histo_annee_perdue.py   # Histogramme années perdues
|   |   |   navbar.py
|   |   |   __init__.py
|   |           
|   +---pages
|   |   |   __init__.py
|   |   |   
|   |   \---data
|   |       \---raw
|   |               rawdata.csv
|   |               rawdata.geojson
|   |               
|   \---utils
|       |   clean_data.py
|       |   fonctions.py
|       |   get_data.py
|       |   mapping_region.py  # Mapping pays -> régions
|       |   __init__.py
|
|   .env
|   .gitignore
|   config.py
|   main.py
|   README.md
|   requirements.txt
|   video.mp4
|                 
```


### Technologies utilisées

- **Frontend** : Dash (Python)
- **Visualisation** : Plotly (graph_objects)
- **Manipulation et analyse des données** : Pandas, GeoPandas
- **Styling** : CSS
- **Cache** : Flask-Caching

### Conventions de code

- **Nommage** : snake_case
- **Fichiers** : Un composant par fichier
- **Commentaires** : Docstring des fonctions et fichiers 
- **Commits** : Messages clairs et descriptifs

****
## Rapport d'analyse

**Note méthodologique** : Les analyses ci-dessous sont basées sur des mesures de qualité de l'air collectées entre 2016 et 2025 dans 68 pays.

### Principales conclusions

#### 1. Tendances globales (2016-2025)

- **Asie en tête** : L'Asie de l'Est et du Sud concentrent **78 ans d'espérance de vie perdus** en moyenne par habitant (voir graphique : Dividende d'Espérance de Vie par Région du Monde)
- **Europe performante** : L'Europe du Nord affiche seulement **0,34 an perdu**, grâce aux politiques environnementales strictes
- **Inégalités criantes** : Ratio de 1 à 230 entre l'Océanie (0,05 an) et l'Asie de l'Est


#### 2. Polluants les plus préoccupants

| Polluant | % dépassement OMS | Pays les plus touchés |
|----------|-------------------|----------------------|
| PM2.5 | 85% | Inde, Bangladesh, Pakistan |
| NO2 | 67% | Chine, Corée du Sud |
| O3 | 45% | Moyen-Orient, Californie |


#### 3. Impact sur la santé

**Méthodologie AQLI** : 
- **10 µg/m³ de PM2.5** au-dessus de la norme OMS (5 µg/m³) = **~1 an de vie perdu**
- **New Delhi (110 µg/m³)** : **~10 ans de vie perdus** par habitant
- **Paris (12 µg/m³)** : **~0,7 an perdu**

#### 4. Politiques efficaces observées

- **Chine (2016-2025)** : Réduction de 40% du PM2.5 grâce aux fermetures d'usines charbon
- **UE** : Normes Euro 6 → baisse de 30% du NO2 urbain
- **Inde** : Échec relatif malgré les plans d'action (pollution stable)

### Limites de l'analyse

**Biais de mesure** : 
- Couverture inégale (Europe sur-représentée, Afrique sous-représentée)
- Stations urbaines majoritaires (sous-estimation des zones rurales polluées)
- Données manquantes pour certains mois/années

### Recommandations

1. **Prioriser PM2.5** : C'est le polluant avec le plus fort impact santé
2. **Densifier le réseau de mesure** en Afrique et Amérique du Sud
3. **Harmoniser les méthodologies** de mesure entre pays

## Copyright

### Déclaration d'originalité

Nous déclarons sur l'honneur que le code fourni a été produit par nous-mêmes, **à l'exception des éléments listés ci-dessous**.

### Code emprunté ou assisté

#### 1. Structure de base Dash
**Source** : [Documentation officielle Dash](https://dash.plotly.com/) \
**Lignes concernées** : Structure générale du `main.py` (lignes 1-30) \
**Explication** : Initialisation standard d'une application Dash avec layout et callbacks

#### 2. Calcul des années perdues (AQLI)
**Source** : [Air Quality Life Index - Méthodologie](https://aqli.epic.uchicago.edu/about/methodology/) \
**Fichier** : `src/utils/mapping_region.py`, fonction `calculate_years_lost()` \
**Explication** : Formule scientifique : 10 µg/m³ de PM2.5 = ~1 an de vie perdu

#### 3. Palette de couleurs choropleth
**Source** : [ColorBrewer](https://colorbrewer2.org/) \
**Fichier** : `main.py`, fonction `create_map()`, variable `colorscale` \
**Explication** : Gradient de bleus pour la visualisation cartographique

#### 4. Assistance IA (Claude/ChatGPT)
**Utilisation** : 
- Aide au débogage des callbacks Dash
- Suggestions d'amélioration du CSS
- Explication de concepts (caching, GeoJSON, etc.)
- Aide à la structuration du code

**Note** : L'IA a été utilisée comme **outil d'apprentissage et d'assistance**, mais **tout le code a été compris, testé et adapté** par nos soins.


### Bibliothèques tierces

Toutes les bibliothèques utilisées sont déclarées dans le fichier `requirements.txt` et utilisées conformément à leurs licences respectives (MIT, Apache 2.0).

## Contact et Contributions

- **Email** : 
	- Benjamin BRIBANT : benjamin.bribant@edu.esiee.fr
	- India CABO : india.cabo@edu.esiee.fr

---

_Dernière mise à jour : **01/02/2026**_
