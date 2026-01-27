"""
Composant : Histogramme de distribution des valeurs de pollution
"""
from dash import html, dcc
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd


def get_color_by_pollutant(pollutant):
    """
    Retourne la couleur associée à un polluant
    
    :param pollutant str: Nom du polluant
    :returns str: Code couleur hexadécimal
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


def create_pollution_histogram(year, selected_pollutants=None):
    """
    Crée un histogramme montrant la distribution des valeurs de pollution
    
    :param year int: Année à filtrer
    :param selected_pollutants list: Liste des polluants sélectionnés (None = tous)
    :returns plotly.graph_objects.Figure: Graphique Plotly
    """
    # Charger les données
    data = gpd.read_file("data/cleaned/cleaneddata.geojson")
    data['measurements_lastupdated'] = pd.to_datetime(data['measurements_lastupdated'])
    data_filtered = data[data['measurements_lastupdated'].dt.year == year]
    
    # Filtrer par polluants si sélectionnés
    if selected_pollutants and len(selected_pollutants) > 0:
        data_filtered = data_filtered[data_filtered['measurements_parameter'].isin(selected_pollutants)]
    
    # Créer l'histogramme
    fig = go.Figure()
    
    # Si plusieurs polluants, créer un histogramme par polluant
    if selected_pollutants and len(selected_pollutants) > 0:
        for pollutant in selected_pollutants:
            pollutant_data = data_filtered[data_filtered['measurements_parameter'] == pollutant]
            
            fig.add_trace(go.Histogram(
                x=pollutant_data['measurements_value'],
                name=pollutant,
                marker_color=get_color_by_pollutant(pollutant),
                opacity=0.7,
                nbinsx=30  # Nombre de barres dans l'histogramme
            ))
    else:
        # Si aucun polluant sélectionné, afficher tous les polluants
        for pollutant in data_filtered['measurements_parameter'].unique():
            pollutant_data = data_filtered[data_filtered['measurements_parameter'] == pollutant]
            
            fig.add_trace(go.Histogram(
                x=pollutant_data['measurements_value'],
                name=pollutant,
                marker_color=get_color_by_pollutant(pollutant),
                opacity=0.7,
                nbinsx=30
            ))
    
    fig.update_layout(
        title=f"Distribution des valeurs de pollution en {year}",
        xaxis_title="Valeur de pollution (µg/m³)",
        yaxis_title="Nombre de mesures",
        barmode='overlay',  # Les histogrammes se superposent
        height=600,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_pollution_histogram_section():
    """
    Crée la section HTML complète pour l'histogramme de distribution
    
    :returns html.Div: Section HTML avec titre, description et graphique
    """
    return html.Div([
        html.H2("Distribution des valeurs de pollution", 
                style={'text-align': 'center', 'margin': '2rem'}),
        html.P("Cet histogramme montre la fréquence des différentes valeurs de pollution mesurées.", 
               style={'text-align': 'center', 'color': '#666', 'fontSize': '0.9rem', 'marginBottom': '1rem'}),
        dcc.Graph(id='histogram-pollution', style={'height': '600px'})
    ], style={'margin': '2rem'})