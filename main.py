"""
Dashboard principal pour la visualisation de la qualité de l'air mondial.

Affiche une carte interactive avec les données de pollution atmosphérique,
ainsi que des graphiques sur l'espérance de vie et les années de vie perdues.
Période : 2016–2025
Polluants : PM2.5, PM10, CO, NO2, SO2, O3.
"""

from dash import Dash, dcc, ctx, html, Input, Output
from src.components.footer import create_footer
from src.components.navbar import create_navbar
from src.components.graphique_vie_pays import create_life_expectancy_graph, create_life_expectancy_section
from src.components.histo_annee_perdue import create_years_lost_histogram, create_years_lost_histogram_section
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
import pycountry
from functools import lru_cache
from flask_caching import Cache

app = Dash(__name__, title="World Air Quality")

# Configuration du cache
cache = Cache(app.server, config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutes
})

@cache.memoize(timeout=3600) 
def load_geojson_data():
    """
    Charge les données GeoJSON depuis le fichier source et les met en cache.
    Dérive les colonnes year, lat et lon depuis les métadonnées existantes.
    Mise en cache pendant 1h.

    :returns geopandas.GeoDataFrame: DataFrame enrichi avec les colonnes year, lat et lon
    """
    print("Chargement des données depuis le fichier...")
    data = gpd.read_file("data/cleaned/cleaneddata.geojson")
    data['measurements_lastupdated'] = pd.to_datetime(data['measurements_lastupdated'])
    data['year'] = data['measurements_lastupdated'].dt.year
    data['lat'] = data.geometry.y
    data['lon'] = data.geometry.x
    return data

@lru_cache(maxsize=128)
def iso2_to_iso3(iso2_code):
    """
    Convertit un code pays ISO 3166-1 alpha-2 en alpha-3.
    Le résultat est mis en cache.

    :param iso2_code str: Code pays sur deux lettres (ex. 'FR', 'US')
    :returns str Code pays sur trois lettres (ex. 'FRA'), ou None si non reconnu
    """
    try:
        return pycountry.countries.get(alpha_2=iso2_code).alpha_3
    except:
        return None

@cache.memoize(timeout=3600)
def get_all_countries_df():
    """
    Génère un DataFrame contenant tous les pays du monde selon pycountry.
    Mise en cache pendant 1h.

    :returns pandas.DataFrame: DataFrame avec les colonnes country_iso3 (alpha-3) et country_name (nom officiel)
    """
    all_countries = []
    for country in pycountry.countries:
        all_countries.append({
            'country_iso3': country.alpha_3,
            'country_name': country.name
        })
    return pd.DataFrame(all_countries)

@cache.memoize(timeout=600)
def get_filtered_data(year, pollutants_tuple):
    """
    Filtre les données de pollution par année et, optionnellement, par polluants.
    Le type tuple (immuable) est requis pour pollutants_tuple pour permettre la mise en cache.
    Mise en cache pendant 10min.

    :param year int: Année de mesure souhaitée (ex. 2020)
    :param pollutants_tuple tuple Tuple trié des polluants à retenir (ex. ('NO2', 'PM2.5')), ou None pour aucun filtre
    :returns geopandas.GeoDataFrame: Sous-ensemble des données filtré selon les critères fournis
    """
    data = load_geojson_data()
    data_filtered = data[data['year'] == year].copy()
    
    if pollutants_tuple:
        pollutants_list = list(pollutants_tuple)
        data_filtered = data_filtered[data_filtered['measurements_parameter'].isin(pollutants_list)]
    
    return data_filtered

@cache.memoize(timeout=600)
def calculate_country_pollution(year, pollutants_tuple):
    """
    Calcule la pollution moyenne par pays pour une année et des polluants donnés.
    Les pays dont le code ISO-2 ne peut pas être converti en ISO-3 sont supprimés.
    Mise en cache pendant 10min.

    :param year int: Année de mesure souhaitée
    :param pollutants_tuple tuple  Tuple trié des polluants à considérer, ou None pour tous
    :returns pandas.DataFrame: DataFrame avec les colonnes country (ISO-2), avg_pollution (moyenne en µg/m³) et country_iso3 (ISO-3)
    """
    data = get_filtered_data(year, pollutants_tuple)
    
    pollution_by_country = data.groupby('country')['measurements_value'].mean().reset_index()
    pollution_by_country.columns = ['country', 'avg_pollution']
    pollution_by_country['country_iso3'] = pollution_by_country['country'].apply(iso2_to_iso3)
    pollution_by_country = pollution_by_country.dropna(subset=['country_iso3'])
    
    return pollution_by_country


def get_color_by_pollutant(pollutant):
    """
    Retourne la couleur hexadécimale associée à un polluant.

    :param pollutant str: Nom du polluant (ex. 'PM2.5', 'O3')
    :returns str: Code couleur hexadécimal (ex. '#EF4444'), ou '#6B7280' (gris) si polluant inconnu
    """
    colors = {
        'PM2.5': '#EF4444',
        'PM10': '#F97316',
        'CO': '#A855F7',
        'NO2': '#3B82F6',
        'SO2': '#10B981',
        'O3': '#06B6D4'
    }
    return colors.get(pollutant, '#6B7280')


def get_pollution_level(pollutant, value):
    """
    Détermine le niveau qualitatif de pollution selon les seuils recommandés.
    Classifie la valeur en quatre niveaux : Bon, Moyen, Mauvais ou Très mauvais.

    :param pollutant str: Nom du polluant (ex. 'PM2.5', 'NO2')
    :param value float: Valeur mesurée dans l'unité associée au polluant
    :returns str: Niveau 'Bon', 'Moyen', 'Mauvais', 'Très mauvais', ou 'Inconnu' si le polluant n'est pas référencé
    """
    thresholds = {
        'PM2.5': [15, 35, 55],
        'PM10': [50, 100, 150],
        'NO2': [40, 100, 200],
        'SO2': [20, 80, 250],
        'O3': [100, 160, 240],
        'CO': [4000, 10000, 20000]
    }
    
    if pollutant not in thresholds:
        return "Inconnu"
    
    levels = thresholds[pollutant]
    if value <= levels[0]:
        return "Bon"
    elif value <= levels[1]:
        return "Moyen"
    elif value <= levels[2]:
        return "Mauvais"
    else:
        return "Très mauvais"


@cache.memoize(timeout=600)
def create_map(year, pollutants_tuple):
    """
    Construit la carte chloroplète Plotly.
    Mise en cache pendant 10min.

    :param year int: Année pour laquelle les données sont affichées
    :param pollutants_tuple tuple Tuple trié des polluants sélectionnés, ou None si aucun filtre
    :returns plotly.graph_objects.Figure: Figure Plotly prête à être rendue dans un dcc.Graph
    """
    
    # Récupérer les données depuis le cache
    data = get_filtered_data(year, pollutants_tuple)
    pollution_by_country = calculate_country_pollution(year, pollutants_tuple)
    all_countries_df = get_all_countries_df()
    
    world_pollution = all_countries_df.merge(
        pollution_by_country[['country_iso3', 'avg_pollution']], 
        on='country_iso3', 
        how='left'
    )
    
    world_pollution['avg_pollution'] = world_pollution['avg_pollution'].fillna(0)
    
    colorscale = [
        [0.0, "#EFEFFE"],
        [0.00001, "#C3E1F6"],
        [0.1, "#9DCCF3"],
        [0.2, "#78BEF8"],
        [0.3, "#45A4F2"],
        [0.4, "#2297F6"],
        [0.5, "#0A83E5"],
        [0.6, "#0D72CA"],
        [0.7, "#0E5EAE"],
        [0.8, "#0D4C94"],
        [1.0, "#093981"],
    ]
    
    zmin = pollution_by_country["avg_pollution"].min()
    zmax = pollution_by_country["avg_pollution"].max()
    
    fig = go.Figure()
    
    fig.add_trace(go.Choropleth(
        locations=world_pollution['country_iso3'],
        z=world_pollution['avg_pollution'],
        locationmode='ISO-3',
        colorscale=colorscale,
        zmin=zmin,
        zmax=zmax,
        marker_line_color='#333333',
        marker_line_width=0.5,
        colorbar_title="Pollution<br>(µg/m³)",
        hovertemplate='<b>%{location}</b><br>Pollution: %{z:.2f} µg/m³<extra></extra>',
        showlegend=False
    ))
    
    data['level'] = data.apply(lambda row: get_pollution_level(row['measurements_parameter'], row['measurements_value']), axis=1)
    data['hover_text'] = data.apply(lambda row: 
        f"<b>{row.get('location', 'Localisation inconnue')}</b><br>" +
        f"Pays: {row.get('country_name_en', row.get('country', 'N/A'))}<br>" +
        f"Polluant: {row['measurements_parameter']}<br>" +
        f"Valeur: {row['measurements_value']} {row.get('measurements_unit', '')}<br>" +
        f"Niveau: {get_pollution_level(row['measurements_parameter'], row['measurements_value'])}", 
        axis=1
    )
    
    for pollutant in data['measurements_parameter'].unique():
        pollutant_data = data[data['measurements_parameter'] == pollutant]
        
        fig.add_trace(go.Scattergeo(
            lon=pollutant_data['lon'],
            lat=pollutant_data['lat'],
            mode='markers',
            marker=dict(
                size=6,
                color=get_color_by_pollutant(pollutant),
                opacity=0.7,
                line=dict(width=1, color='white')
            ),
            name=pollutant,
            text=pollutant_data['hover_text'],
            hovertemplate='%{text}<extra></extra>'
        ))
    
    fig.update_geos(
        projection_type="natural earth",
        visible=False,
        showcountries=True,
        showcoastlines=True,
        coastlinecolor="#666666",
        countrycolor="#333333",
        countrywidth=0.5,
        showland=False
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=600,
        showlegend=False,
        geo=dict(
            bgcolor='rgba(255,255,255,0)'
        )
    )
    
    return fig


selected_pollutants = set()

app.layout = html.Div([
    html.H1("Dashboard - World Air Quality", style={'text-align':'center'}, className="page-title"),
    
    dcc.Store(id='active-tab', data='carte'),
    
    create_navbar(),
    
    html.Div([
        html.Div([
            html.Div([
                dcc.Slider(
                    min=2016, 
                    max=2025,
                    value=2016, 
                    step=1,
                    marks={i: str(i) for i in range(2016, 2026)},
                    id="year-slider",
                    className="custom-slider"
                ),

                html.Div([
                    html.Button([
                        "▶ Play"
                    ], id="play-pause-btn", n_clicks=0, className="play-pause-btn"),
                    
                ], className="play-pause-container"),

                dcc.Interval(
                    id="interval",
                    interval=10000,
                    n_intervals=0,
                    max_intervals=-1  
                ),
            ], style={'display': 'flex', 'justify-content': 'center', 'alignItems':'center' ,'margin':'3rem'}),
            
            html.Div([
                html.Div([
                    html.Div([
                        html.H6("Nombre de pays comptés", className='valeur-mesuree'),
                        html.H3(id="nb-pays")
                    ]),
                    html.Div([
                        html.H6("Polluant mesuré", className='valeur-mesuree'),
                        html.H3(id="polluant")
                    ]),
                ], style={'display': 'flex', 'justify-content': 'space-evenly', 'margin':'3rem'}),
                
                html.Div([
                    dcc.Loading(
                        id="loading-carte",
                        type="circle",
                        children=[
                            dcc.Graph(
                                id="carte",
                                style={'height': '600px'}
                            )
                        ], style={'margin': '2rem'})
                ], style={'margin': '2rem'}),
                
                html.Div([
                    html.Div([
                        html.Span([
                            "PM2.5 : Particules fines (µg/m³)",
                            html.Span(
                                "Les particules en suspension PM2,5 sont des entités solides dont le diamètre est inférieur à 2.5 micromètre, nocives pour la santé respiratoire et cardiovasculaire",
                                className='tooltiptext'
                            )
                        ], className='tooltip'),
                        html.Br(),
                        html.Span([
                            "PM10 : Particules grossières (µg/m³)",
                            html.Span(
                                "Les particules en suspension PM10 sont des particules dont le diamètre est inférieur à 10 micromètres (poussières inhalables)",
                                className='tooltiptext'
                            )
                        ], className='tooltip'),
                        html.Br(),
                        html.Span([
                            "NO2 : Dioxyde d'azote (µg/m³)",
                            html.Span(
                                "Le dioxyde d'azote (NO2) est un polluant émis lors des phénomènes de combustion",
                                className='tooltiptext'
                            )
                        ], className='tooltip'),
                        html.Br(),
                        html.Span([
                            "O3 : Ozone (µg/m³)",
                            html.Span(
                                "L'ozone (O₃) est un gaz essentiel à la stratosphère (entre 15 et 30 km d'altitude), où il nous protège des effets nocifs des rayons UV",
                                className='tooltiptext'
                            )
                        ], className='tooltip'),
                        html.Br(),
                        html.Span([
                            "CO2 : Émissions de dioxyde de carbone (tonnes)",
                            html.Span(
                                "Le dioxyde de carbone est un gaz incolore, inerte et non toxique. En grande quantité, il affaiblit la couche d'ozone provoquant le réchauffement de la planète",
                                className='tooltiptext'
                            )
                        ], className='tooltip'),
                    ], className='legende'),
                    html.Div([
                        html.Div([
                            html.Button('PM2.5', id='btn-pm25', n_clicks=0),
                            html.Button('PM10', id='btn-pm10', n_clicks=0),
                            html.Button('CO', id='btn-co', n_clicks=0),
                        ]),
                        html.Div([
                            html.Button('NO2', id='btn-no2', n_clicks=0),
                            html.Button('SO2', id='btn-so2', n_clicks=0),
                            html.Button('O3', id='btn-o3', n_clicks=0),
                        ]),
                    ], className="buttons-polluants")
                ], style={'display': 'flex', 'justify-content':'center'}, className="below-map"),
                
                dcc.Loading(
                    id="loading-ranking-table",
                    type="circle",
                    color="#005093",
                    children=[html.Div(id="ranking-table", className="ranking")])
            ], id="carte-section"),
        ]),
        
        html.Div([
            dcc.Loading(
                id="loading-histogram-years-lost",
                type="circle",
                children=[create_years_lost_histogram_section()]),
            
            dcc.Loading(
                id="loading-expectancy-chart",
                type="circle",
                children=[create_life_expectancy_section()]),
            
        ], id='graphiques-section', style={'display': 'none'}),
        
    ], id="main-content"),
    
    create_footer()
])


@app.callback(
    [Output('carte-section', 'style'),
     Output('graphiques-section', 'style')],
    [Input('nav-carte', 'n_clicks'),
     Input('nav-graphiques', 'n_clicks')],
    prevent_initial_call=True
)
def toggle_sections(carte_clicks, graphiques_clicks):
    """
    Bascule l'affichage entre la section carte et la section graphiques.

    :param carte_clicks int: Nombre de clics sur le bouton de navigation 'Carte'
    :param graphiques_clicks int: Nombre de clics sur le bouton de navigation 'Graphiques'
    :returns tuple[dict, dict]: Styles CSS pour carte-section puis graphiques-section
    """
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == 'nav-graphiques':
            return {'display': 'none'}, {'display': 'block'}
        else:
            return {'display': 'block'}, {'display': 'none'}
    
    return {'display': 'block'}, {'display': 'none'}


@app.callback(
    Output('life-expectancy-chart', 'figure'),
    [Input('year-slider', 'value')]
)
def update_life_expectancy(selected_year):
    """
    Met à jour le graphique d'espérance de vie selon l'année sélectionnée.

    :param selected_year int: Année choisie via le slider (entre 2016 et 2025)
    :returns plotly.graph_objects.Figure: Graphique Plotly d'espérance de vie par pays
    """
    return create_life_expectancy_graph(year=selected_year)


@app.callback(
    Output('histogram-years-lost', 'figure'),
    [Input('year-slider', 'value')]
)
def update_years_lost_histogram(selected_year):
    """
    Met à jour l'histogramme des années de vie perdues selon l'année sélectionnée.

    :param selected_year int: Année choisie via le slider (entre 2016 et 2025)
    :returns plotly.graph_objects.Figure: Histogramme Plotly de la distribution des années perdues
    """
    return create_years_lost_histogram(year=selected_year)


@app.callback(
    Output('year-slider', 'value'),
    [Input('interval', 'n_intervals')],
    prevent_initial_call=False
)
def animate_slider(n):
    """
    Anime automatiquement le slider d'année en boucle lorsque la lecture est active.

    :param n int: Nombre de tiques écoulées depuis le démarrage de l'intervalle, None à l'initialisation
    :returns int: Année à afficher sur le slider, calculée par modulo sur les années disponibles
    """
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
    if n is None:
        return years[0]
    return years[n % len(years)]

@app.callback(
    [Output("interval", "disabled"),
     Output("play-pause-btn", "children")],
    [Input("play-pause-btn", "n_clicks")]
)
def play_pause(n_clicks):
    """
    Active ou désactive l'animation automatique du slider.

    :param n_clicks int: Nombre total de clics sur le bouton 'Play'/'Pause'
    :returns bool: True si l'intervalle doit être actif (lecture) + changement du texte, True pour pause + changement du texte
    """
    
    if n_clicks is None or n_clicks == 0:
        return True, "▶ Play"
    
    # Si le nombre de clics est impair = Playing
    # Si pair = Paused
    is_playing = (n_clicks % 2) == 1
    
    if is_playing:
        return False, "⏸ Pause"
    else:
        return True, "▶ Play"


@app.callback(
    [Output('carte', 'figure'),
     Output('nb-pays', 'children'),
     Output('polluant', 'children'),
     Output('ranking-table', 'children'),
     Output('btn-pm25', 'style'),
     Output('btn-pm10', 'style'),
     Output('btn-co', 'style'),
     Output('btn-no2', 'style'),
     Output('btn-so2', 'style'),
     Output('btn-o3', 'style')],
    [Input('year-slider', 'value'),
     Input('btn-pm25', 'n_clicks'),
     Input('btn-pm10', 'n_clicks'),
     Input('btn-co', 'n_clicks'),
     Input('btn-no2', 'n_clicks'),
     Input('btn-so2', 'n_clicks'),
     Input('btn-o3', 'n_clicks')]
)
def update_map(selected_year, pm25_clicks, pm10_clicks, co_clicks, no2_clicks, so2_clicks, o3_clicks):
    """
    Callback central : met à jour la carte, les KPIs, le tableau de classement Top 5
    et les styles des boutons de polluants selon l'année et les filtres actifs.

    :param selected_year int: Année choisie via le slider
    :param pm25_clicks int: Nombre de clics sur le bouton PM2.5
    :param pm10_clicks int: Nombre de clics sur le bouton PM10
    :param co_clicks int: Nombre de clics sur le bouton CO
    :param no2_clicks int: Nombre de clics sur le bouton NO2
    :param so2_clicks int: Nombre de clics sur le bouton SO2
    :param o3_clicks int: Nombre de clics sur le bouton O3
    :returns tuple: Figure carte, nombre de pays (str), affichage polluant, tableau HTML Top 5, puis 6 dicts de styles CSS pour les boutons
    """
    
    global selected_pollutants
    
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        pollutant_map = {
            'btn-pm25': 'PM2.5',
            'btn-pm10': 'PM10',
            'btn-co': 'CO',
            'btn-no2': 'NO2',
            'btn-so2': 'SO2',
            'btn-o3': 'O3'
        }
        
        if button_id in pollutant_map:
            pollutant = pollutant_map[button_id]
            if pollutant in selected_pollutants:
                selected_pollutants.remove(pollutant)
            else:
                selected_pollutants.add(pollutant)
    
    pollutants_tuple = tuple(sorted(selected_pollutants)) if len(selected_pollutants) > 0 else None
    
    data_filtered = get_filtered_data(selected_year, pollutants_tuple)
    
    nb_pays = data_filtered['country'].nunique()
    
    if pollutants_tuple:
        polluant_display = []
        for i, pollutant in enumerate(sorted(pollutants_tuple)):
            color = get_color_by_pollutant(pollutant)
            polluant_display.append(
                html.Span(pollutant, style={'color': color, 'fontWeight': 'bold'})
            )
            if i < len(pollutants_tuple) - 1:
                polluant_display.append(", ")
    else:
        polluant_display = "Tous"
    
    top_countries = data_filtered.groupby(['country', 'country_name_en']).agg({
        'measurements_value': 'mean',
        'measurements_unit': 'first',
        'measurements_lastupdated': 'max'
    }).reset_index()
    
    top_countries = top_countries.sort_values('measurements_value', ascending=False).head(5)
    
    table_rows = []
    for idx, row in top_countries.iterrows():
        rank = len(table_rows) + 1
        country_name = row['country_name_en'] if pd.notna(row['country_name_en']) else row['country']
        unit = row['measurements_unit'] if pd.notna(row['measurements_unit']) else 'µg/m³'
        value = f"{row['measurements_value']:.2f}"
        date = pd.to_datetime(row['measurements_lastupdated']).strftime('%d/%m/%Y')
        
        table_rows.append(
            html.Tr([
                html.Td(f"#{rank}"),
                html.Td(country_name),
                html.Td(unit),
                html.Td(value),
                html.Td(date),
            ])
        )
    
    ranking_table = html.Table([
        html.Thead([
            html.Tr([
                html.Th("Rang"),
                html.Th("Pays"),
                html.Th("Unité"),
                html.Th("Valeur moyenne"),
                html.Th("Dernière mesure"),
            ])
        ]),
        html.Tbody(table_rows)
    ])
    
    fig = create_map(selected_year, pollutants_tuple)
    
    def get_button_style(pollutant):
        """
        Génère le style CSS d'un bouton de sélection de polluant.
        Fond coloré si actif, fond blanc avec bordure colorée sinon.

        :param pollutant str: Nom du polluant associé au bouton
        :returns dict: Dictionnaire de styles CSS
        """
        color = get_color_by_pollutant(pollutant)
        is_selected = pollutant in selected_pollutants
        
        return {
            'backgroundColor': color if is_selected else 'white',
            'color': 'white' if is_selected else color,
            'border': f'2px solid {color}',
            'fontWeight': 'bold' if is_selected else 'normal',
            'transition': 'all 0.3s ease',
            'width': '10rem',
            'height': '3rem',
            'borderRadius': '10px',
            'margin': '0.5rem',
            'cursor': 'pointer'
        }
    
    styles = [
        get_button_style('PM2.5'),
        get_button_style('PM10'),
        get_button_style('CO'),
        get_button_style('NO2'),
        get_button_style('SO2'),
        get_button_style('O3')
    ]
    
    return fig, str(nb_pays), polluant_display, ranking_table, *styles

if __name__ == '__main__':
    app.run(debug=True)