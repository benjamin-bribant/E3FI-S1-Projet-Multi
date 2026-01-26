from dash import html, dcc
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd
from src.utils.mapping_region import get_region, calculate_years_lost

def create_histo_esperance_vie(year=None):
    """
    Crée l'histogramme du dividende d'espérance de vie par région
    
    :param year entier: Année à filtrer (None pour toutes les années)
        
    Returns:
        plotly.graph_objects.Figure: Graphique Plotly
    """
    # Charger les données
    data = gpd.read_file("data/cleaned/cleaneddata.geojson")
    
    # Filtrer uniquement PM2.5
    data = data[data['measurements_parameter'] == 'PM2.5']
    
    # Filtrer par année si spécifié
    if year is not None:
        data['measurements_lastupdated'] = pd.to_datetime(data['measurements_lastupdated'])
        data = data[data['measurements_lastupdated'].dt.year == year]
    
    data['region'] = data['country'].apply(get_region)
    data['years_lost'] = data['measurements_value'].apply(calculate_years_lost)
    
    # Grouper par région et calculer la moyenne
    regional_data = data.groupby('region').agg({
        'years_lost': 'mean',
        'measurements_value': 'mean',
        'country': 'count'
    }).reset_index()
    
    regional_data.columns = ['region', 'avg_years_lost', 'avg_pm25', 'nb_measurements']
    
    # Filtrer les régions avec données significatives et trier
    regional_data = regional_data[regional_data['region'] != 'Autre']
    regional_data = regional_data.sort_values('avg_years_lost', ascending=True)
    
    # Créer le graphique
    fig = go.Figure()
    
    # Palette de couleurs avec style du dashboard
    colors = ['#005093', '#0A83E5', '#2297F6', '#45A4F2', '#78BEF8', 
              '#9DCCF3', '#C3E1F6', '#0D72CA', '#0E5EAE', '#0D4C94']
    
    fig.add_trace(go.Bar(
        x=regional_data['avg_years_lost'],
        y=regional_data['region'],
        orientation='h',
        marker=dict(
            color=colors[:len(regional_data)],
            line=dict(color='#003d73', width=1)
        ),
        text=regional_data['avg_years_lost'].apply(lambda x: f'{x:.2f} ans'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>' +
                      'Années perdues: %{x:.2f} ans<br>' +
                      'PM2.5 moyen: %{customdata[0]:.1f} µg/m³<br>' +
                      'Nombre de mesures: %{customdata[1]}<br>' +
                      '<extra></extra>',
        customdata=regional_data[['avg_pm25', 'nb_measurements']].values
    ))
    
    fig.update_layout(
        title={
            'text': 'Dividende d\'Espérance de Vie par Région<br><sub>Années gagnées si les normes OMS (5 µg/m³) étaient respectées</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#005093', 'family': 'Montserrat'}
        },
        xaxis_title='Années d\'espérance de vie perdues',
        yaxis_title='',
        height=max(400, len(regional_data) * 50),
        margin=dict(l=150, r=100, t=100, b=80),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Montserrat', color='#005093'),
        xaxis=dict(
            gridcolor='#E5E5E5',
            showgrid=True,
            zeroline=True,
            zerolinecolor='#005093',
            zerolinewidth=2
        ),
        yaxis=dict(
            showgrid=False
        ),
        showlegend=False
    )
    
    return fig


def create_graphs_section():
    """
    Crée la section complète des graphiques
    
    :returns html.Div: Composant Dash contenant les graphiques
    """
    return html.Div([
        html.H2("Analyse de l'Impact sur l'Espérance de Vie", 
                style={'textAlign': 'center', 'color': '#005093', 'marginTop': '2rem'}),
        
        html.Div([
            html.P([
                "Cet histogramme transforme une mesure chimique abstraite (PM2.5) en une donnée humaine tangible : ",
                html.Strong("le temps de vie perdu."),
                " Il permet de comparer l'impact de la pollution de l'air par rapport à d'autres facteurs de risque."
            ], style={'textAlign': 'center', 'maxWidth': '800px', 'margin': '0 auto 2rem', 
                     'color': '#005093', 'fontSize': '14px'}),
            
            html.Div([
                html.Span("💡 ", style={'fontSize': '20px'}),
                html.Span([
                    "Méthodologie : ",
                    html.Strong("AQLI (Air Quality Life Index)"),
                    " - 10 µg/m³ supplémentaires de PM2.5 réduisent l'espérance de vie d'environ 1 an"
                ], style={'fontSize': '12px', 'color': '#666'})
            ], style={'textAlign': 'center', 'marginBottom': '2rem'}),
        ]),
        
        html.Div([
            dcc.Graph(
                id='life-expectancy-chart',
                style={'height': '600px'}
            )
        ], style={'margin': '2rem'}),
        
        html.Div([
            html.Div([
                html.H4("Pour résumer ce graphique :", 
                       style={'color': '#005093', 'marginBottom': '1rem'}),
                html.Ul([
                    html.Li("Les régions d'Asie du Sud et de l'Est sont parmi les plus touchées"),
                    html.Li("Atteindre les normes OMS permettrait de gagner plusieurs années de vie"),
                    html.Li("Les disparités régionales sont considérables")
                ], style={'color': '#005093', 'lineHeight': '2'})
            ], style={
                'maxWidth': '800px',
                'margin': '2rem auto',
                'padding': '2rem',
                'backgroundColor': '#f8f9fa',
                'borderRadius': '10px',
                'border': '2px solid #005093'
            })
        ])
    ], id='graphs-section', style={'display': 'none'})