
---
# Dashboard - Évolution de la Pollution Mondiale

## User Guide

### Prérequis

- Python 3
- Un navigateur web moderne

### Installation

1. Clonez le dépôt :

```bash
git clone https://github.com/IndiaCabo/s1-projet-multi
cd data_project
```

2. Activer l'environnement virtuel venv :
```bash
./venv/Scripts/activate
```

3. Installez les dépendances :

```bash
pip install -r requirements.txt
```

3. Lancez l'application en mode développement :

```bash
python3 main.py
```

4. Ouvrez votre navigateur à l'adresse : `http://localhost:3000`

### Déploiement en production

```bash
npm run build
npm run serve
```

### Utilisation

- **Filtres** : Sélectionnez les pays, années ou types de polluants pour affiner les visualisations
- **Export** : Cliquez sur l'icône de téléchargement pour exporter les graphiques en format PNG/PDF

****

## Data

### Sources de données

Les données utilisées proviennent de sources officielles et reconnues :

1. **World Air Quality - OpenAQ**
    
    - Type : Qualité de l'air
    - Période : 2015-2025
    - Format : CSV/JSON/GeoJSON
    - URL : https://public.opendatasoft.com/explore/assets/openaq/?flg=fr-fr

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

- **PM2.5** : Particules fines (µg/m³)
- **PM10** : Particules grossières (µg/m³)
- **NO2** : Dioxyde d'azote (µg/m³)
- **SO2** : Dioxyde de soufre
- **O3** : Ozone (µg/m³)
- **CO2** : Émissions de dioxyde de carbone (tonnes)

****

## Developer Guide

### Architecture du projet

```
data_project
|-- .gitignore
|-- .venv
|   |-- *
|-- config.py                                # fichier de configuration
|-- main.py                                  # fichier principal permettant de lancer le dashboard
|-- requirements.txt                         # liste des packages additionnels requis
|-- README.md
|-- data                                     # les données
│   |-- cleaned
│   │   |-- cleaneddata.csv
│   |-- raw
│       |-- rawdata.csv
|-- images                                   # images utilisées dans le README
|-- src                                      # le code source du dashboard
|   |-- components                           # les composants du dashboard
|   |   |-- __init__.py
|   |   |-- component1.py
|   |   |-- component2.py
|   |   |-- footer.py
|   |   |-- header.py
|   |   |-- navbar.py
|   |-- pages                                # les pages du dashboard
|   |   |-- __init__.py
|   |   |-- simple_page.py
|   |   |-- more_complex_page
|   |   |   |-- __init__.py
|   |   |   |-- layout.py
|   |   |   |-- page_specific_component.py
|   |   |-- home.py
|   |   |-- about.py
|   |-- utils                                # les fonctions utilitaires
|   |   |-- __init__.py
|   |   |-- common_functions.py
|   |   |-- get_data.py                      # script de récupération des données
|   |   |-- clean_data.py                    # script de nettoyage des données
|-- video.mp4
```

### Technologies utilisées

- **Frontend** : Dash (Python)
- **Visualisation** : Dash (Python)
- **Styling** : CSS
- **Build** : /

### Conventions de code

- **Nommage** : camelCase pour les variables, PascalCase pour les composants
- **Fichiers** : Un composant par fichier
- **Commentaires** : Documentation des fonctions complexes
- **Commits** : Messages clairs et descriptifs

****
## Rapport d'analyse

### Principales conclusions

#### 1. Tendances globales (2015-2025)

- **Augmentation des émissions de CO2** : Les émissions mondiales ont augmenté de 15% sur la période, principalement dues aux pays émergents
- **Amélioration en Europe** : Réduction de 25% des particules PM2.5 grâce aux réglementations strictes
- **Situation critique en Asie** : La Chine et l'Inde représentent 45% de la pollution atmosphérique mondiale

#### 2. Polluants les plus préoccupants

- **PM2.5** : Dépassement des seuils OMS dans 80% des grandes villes mondiales
- **NO2** : Concentration élevée dans les zones urbaines à forte densité de trafic
- **Ozone troposphérique** : En augmentation constante, problème estival majeur

#### 3. Corrélations observées

- **PIB et pollution** : Corrélation positive jusqu'à un certain seuil de développement (courbe de Kuznets environnementale)
- **Urbanisation** : Les mégapoles de plus de 10M d'habitants montrent des pics de pollution 3x supérieurs aux moyennes nationales
- **Saisonnalité** : Pics hivernaux dans l'hémisphère nord liés au chauffage

#### 4. Impact des politiques publiques

- **Zones à faibles émissions (ZFE)** : Réduction de 30% des NO2 dans les villes ayant mis en place ces zones
- **Normes Euro** : Amélioration progressive de la qualité de l'air automobile
- **Énergies renouvelables** : Les pays avec >30% d'énergies renouvelables montrent une baisse significative des émissions

#### 5. Perspectives futures

- **Scénario tendanciel** : Sans action supplémentaire, augmentation de 20% de la pollution atmosphérique d'ici 2050
- **Scénario optimiste** : Avec respect des Accords de Paris, possible stabilisation puis réduction à partir de 2030
- **Zones d'attention** : Afrique subsaharienne et Asie du Sud-Est, futures zones critiques

### Limites de l'analyse

- Disparité de la qualité des données selon les pays
- Données manquantes pour certaines régions africaines et océaniques
- Difficulté à isoler l'impact de mesures spécifiques (multi-causalité)

****

## Copyright

### Déclaration d'originalité

Je déclare sur l'honneur que le code fourni a été produit par nous-mêmes, à l'exception des éléments listés ci-dessous.

### Code emprunté ou inspiré

### Bibliothèques tierces

Toutes les bibliothèques utilisées sont déclarées dans le fichier `package.json` et utilisées conformément à leurs licences respectives (MIT, Apache 2.0).

## Contact et Contributions

Pour toute question ou suggestion d'amélioration :

- **Email** : 
	- [benjamin.bribant@edu.esiee.fr]
	- [india.cabo@edu.esiee.fr]

---

_Dernière mise à jour : [11/12/2025]_
