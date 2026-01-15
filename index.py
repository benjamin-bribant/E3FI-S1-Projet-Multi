from dash import Dash, dcc, ctx, html, Input, Output
from src.components.footer import create_footer
import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pycountry

def get_color_by_pollutant(pollutant):
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

def create_map(year=None, selected_pollutants=None):
    """Crée la carte Plotly avec fond bleu et points de pollution"""
    data = gpd.read_file("data/cleaned/cleaneddata.geojson") 

    if year is not None:
        data['measurements_lastupdated'] = pd.to_datetime(data['measurements_lastupdated'])
        data = data[data['measurements_lastupdated'].dt.year == year]
    
    # Filtrer par polluants sélectionnés
    if selected_pollutants and len(selected_pollutants) > 0:
        data = data[data['measurements_parameter'].isin(selected_pollutants)]
    
    # Fonction pour convertir ISO-2 en ISO-3
    def iso2_to_iso3(iso2_code):
        try:
            return pycountry.countries.get(alpha_2=iso2_code).alpha_3
        except:
            return None
    
    # Calculer la pollution moyenne par pays
    pollution_by_country = data.groupby('country')['measurements_value'].mean().reset_index()
    pollution_by_country.columns = ['country', 'avg_pollution']
    
    # Convertir les codes ISO-2 en ISO-3
    pollution_by_country['country_iso3'] = pollution_by_country['country'].apply(iso2_to_iso3)
    pollution_by_country = pollution_by_country.dropna(subset=['country_iso3'])
    
    # Créer un DataFrame avec TOUS les pays du monde
    all_countries = []
    for country in pycountry.countries:
        all_countries.append({
            'country_iso3': country.alpha_3,
            'country_name': country.name
        })
    all_countries_df = pd.DataFrame(all_countries)
    
    # Fusionner avec les données de pollution (left join pour garder tous les pays)
    world_pollution = all_countries_df.merge(
        pollution_by_country[['country_iso3', 'avg_pollution']], 
        on='country_iso3', 
        how='left'
    )
    
    # Remplacer les NaN par 0 pour les pays sans données
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
    
    # Utiliser les vraies valeurs min/max (sans les 0)
    zmin = pollution_by_country["avg_pollution"].min()
    zmax = pollution_by_country["avg_pollution"].max()
    
    # Créer une figure vide
    fig = go.Figure()
    
    # Ajouter le choropleth avec TOUS les pays
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
    
    # Préparer les données des points par polluant
    data['lat'] = data.geometry.y
    data['lon'] = data.geometry.x
    data['level'] = data.apply(lambda row: get_pollution_level(row['measurements_parameter'], row['measurements_value']), axis=1)
    data['hover_text'] = data.apply(lambda row: 
        f"<b>{row.get('location', 'Localisation inconnue')}</b><br>" +
        f"Pays: {row.get('country_name_en', row.get('country', 'N/A'))}<br>" +
        f"Polluant: {row['measurements_parameter']}<br>" +
        f"Valeur: {row['measurements_value']} {row.get('measurements_unit', '')}<br>" +
        f"Niveau: {get_pollution_level(row['measurements_parameter'], row['measurements_value'])}", 
        axis=1
    )
    
    # Ajouter les points de pollution par type de polluant
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
    
    # Mise en page
    fig.update_geos(
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


app = Dash()

# Variable globale pour stocker les polluants sélectionnés
selected_pollutants = set()

app.layout = html.Div([
    html.H1("Dashboard - World Air Quality", style={'text-align':'center'}, className="page-title"),
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
            html.Button("Play", id="play-btn", n_clicks=0),
            html.Button("Pause", id="pause-btn", n_clicks=0),
        ]),

        dcc.Interval(
            id="interval",
            interval=10000,
            n_intervals=0,
            max_intervals=-1  
        ),
    ], style={'display': 'flex', 'justify-content': 'center', 'margin':'3rem'}),
    
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
        dcc.Graph(
            id="carte",
            style={'height': '600px'}
        )
    ], style={'margin': '2rem'}),
    
    html.Div([
        html.Div([
            html.Span([
                "PM2.5 : Particules fines (µg/m³)",
                html.Span(
                    "Les particules fines (PM2,5) sont des entités solides de très petite taille, nocives pour la santé respiratoire et cardiovasculaire",
                    className='tooltiptext'
                )
            ], className='tooltip'),
            html.Br(),
            html.Span([
                "PM10 : Particules grossières (µg/m³)",
                html.Span(
                    "Les particules fines (PM2,5) sont des entités solides de très petite taille, nocives pour la santé respiratoire et cardiovasculaire",
                    className='tooltiptext'
                )
            ], className='tooltip'),
            html.Br(),
            html.Span([
                "NO2 : Dioxyde d'azote (µg/m³)",
                html.Span(
                    "Les particules fines (PM2,5) sont des entités solides de très petite taille, nocives pour la santé respiratoire et cardiovasculaire",
                    className='tooltiptext'
                )
            ], className='tooltip'),
            html.Br(),
            html.Span([
                "O3 : Ozone (µg/m³)",
                html.Span(
                    "Les particules fines (PM2,5) sont des entités solides de très petite taille, nocives pour la santé respiratoire et cardiovasculaire",
                    className='tooltiptext'
                )
            ], className='tooltip'),
            html.Br(),
            html.Span([
                "CO2 : Émissions de dioxyde de carbone (tonnes)",
                html.Span(
                    "Les particules fines (PM2,5) sont des entités solides de très petite taille, nocives pour la santé respiratoire et cardiovasculaire",
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
    
    html.Div(id="ranking-table", className="ranking"),
    
    create_footer()
])

# Callback pour l'animation du slider
@app.callback(
    Output('year-slider', 'value'),
    [Input('interval', 'n_intervals')],
    prevent_initial_call=False
)
def animate_slider(n):
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
    if n is None:
        return years[0]
    return years[n % len(years)]

@app.callback(
    Output("interval", "disabled"),
    Input("play-btn", "n_clicks"),
    Input("pause-btn", "n_clicks"),
)
def play_pause(play_clicks, pause_clicks):
    if play_clicks > pause_clicks:
        return False 
    return True       

@app.callback(
    [Output('carte', 'figure'),
     Output('nb-pays', 'children'),
     Output('polluant', 'children'),
     # Ajouter les outputs pour les styles
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
    """Met à jour la carte en fonction de l'année et des polluants sélectionnés"""
    
    # Initialiser la liste des polluants sélectionnés
    if 'selected_pollutants' not in globals():
        global selected_pollutants
        selected_pollutants = set()
    
    # Déterminer quel bouton a été cliqué
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
    
    # Si aucun polluant sélectionné, afficher tous
    pollutants_to_show = list(selected_pollutants) if len(selected_pollutants) > 0 else None
    
    # Charger les données pour calculer les statistiques
    data = gpd.read_file("data/cleaned/cleaneddata.geojson")
    data['measurements_lastupdated'] = pd.to_datetime(data['measurements_lastupdated'])
    data_filtered = data[data['measurements_lastupdated'].dt.year == selected_year]
    
    # Calculer le nombre de pays uniques
    nb_pays = data_filtered['country'].nunique()
    
    # Déterminer les polluants affichés
    if pollutants_to_show:
        polluant_text = ", ".join(sorted(pollutants_to_show))
    else:
        polluant_text = "Tous"
    
    fig = create_map(year=selected_year, selected_pollutants=pollutants_to_show)
    
    # Créer les styles pour chaque bouton
    def get_button_style(pollutant):
        color = get_color_by_pollutant(pollutant)
        is_selected = pollutant in selected_pollutants
        
        return {
            'backgroundColor': color if is_selected else 'white',
            'color': 'white' if is_selected else color,
            'border': f'2px solid {color}',
            'fontWeight': 'bold' if is_selected else 'normal',
            'transition': 'all 0.3s ease'
        }
    
    # Générer les styles dans l'ordre des outputs
    styles = [
        get_button_style('PM2.5'),
        get_button_style('PM10'),
        get_button_style('CO'),
        get_button_style('NO2'),
        get_button_style('SO2'),
        get_button_style('O3')
    ]
    
    return fig, str(nb_pays), polluant_text, *styles

if __name__ == '__main__':
    app.run(debug=True)