"""
Composant : Histogramme des années perdues selon les intervalles de PM2.5
"""
from dash import html, dcc
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd
from src.utils.mapping_region import calculate_years_lost


def create_years_lost_histogram(year):
    """
    Crée un histogramme montrant les années perdues selon les intervalles de PM2.5
    
    :param year int: Année à filtrer
    :returns plotly.graph_objects.Figure: Graphique Plotly
    """
    # Charger les données
    data = gpd.read_file("data/cleaned/cleaneddata.geojson")
    data['measurements_lastupdated'] = pd.to_datetime(data['measurements_lastupdated'])
    
    # Filtrer par année et PM2.5 uniquement
    data_filtered = data[
        (data['measurements_lastupdated'].dt.year == year) &
        (data['measurements_parameter'] == 'PM2.5')
    ]
    
    # Calculer les années perdues pour chaque mesure
    data_filtered['years_lost'] = data_filtered['measurements_value'].apply(calculate_years_lost)
    
    # Créer des intervalles de PM2.5
    bins = [0, 5, 15, 25, 35, 50, 75, 100, 150, 200, 500]
    labels = ['0-5', '5-15', '15-25', '25-35', '35-50', '50-75', '75-100', '100-150', '150-200', '200+']
    data_filtered['pm25_range'] = pd.cut(data_filtered['measurements_value'], bins=bins, labels=labels, include_lowest=True)
    
    # Grouper par intervalle et calculer la moyenne des années perdues
    range_stats = data_filtered.groupby('pm25_range', observed=True).agg({
        'years_lost': 'mean',
        'measurements_value': 'count'
    }).reset_index()
    
    range_stats.columns = ['pm25_range', 'avg_years_lost', 'count']
    
    # Créer l'histogramme
    fig = go.Figure()
    
    # Couleurs progressives du bleu au rouge selon la gravité
    colors_gradient = ['#10B981', '#06B6D4', '#3B82F6', '#005093', '#F97316', '#EF4444', '#DC2626', '#991B1B', '#7F1D1D', '#450A0A']
    
    fig.add_trace(go.Bar(
        x=range_stats['pm25_range'].astype(str),
        y=range_stats['avg_years_lost'],
        marker=dict(
            color=colors_gradient[:len(range_stats)],
            line=dict(color='#003d73', width=1)
        ),
        text=range_stats['avg_years_lost'].apply(lambda x: f'{x:.2f} ans'),
        textposition='outside',
        hovertemplate='<b>PM2.5: %{x} µg/m³</b><br>' +
                      'Années perdues en moyenne: %{y:.2f} ans<br>' +
                      'Nombre de mesures: %{customdata}<br>' +
                      '<extra></extra>',
        customdata=range_stats['count']
    ))
    
    fig.update_layout(
        title=f"Impact sur l'espérance de vie selon les niveaux de PM2.5 ({year})",
        xaxis_title="Concentration de PM2.5 (µg/m³)",
        yaxis_title="Années d'espérance de vie perdues (moyenne)",
        height=600,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Montserrat', color='#005093'),
        xaxis=dict(
            showgrid=False,
        ),
        yaxis=dict(
            gridcolor='#E5E5E5',
            showgrid=True,
            zeroline=True,
            zerolinecolor='#005093',
            zerolinewidth=2
        ),
        margin=dict(l=80, r=50, t=80, b=100)
    )
    
    # Ajouter une ligne horizontale pour la norme OMS (0 années perdues à 5 µg/m³)
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#10B981",
        annotation_text="Norme OMS (5 µg/m³)",
        annotation_position="right"
    )
    
    return fig


def create_years_lost_histogram_section():
    """
    Crée la section HTML complète pour l'histogramme des années perdues
    
    :returns html.Div: Section HTML avec titre, description et graphique
    """
    return html.Div([
        html.H2("Années d'espérance de vie perdues selon les niveaux de PM2.5", 
                style={'text-align': 'center', 'margin': '2rem'}),
        html.Div([
            html.P([
                "Cet histogramme montre combien d'années de vie sont perdues pour chaque intervalle de concentration de PM2.5. ",
                "Plus la concentration est élevée, plus l'impact sur l'espérance de vie est important."
            ], style={'textAlign': 'center', 'maxWidth': '800px', 'margin': '0 auto 1rem', 
                     'color': '#005093', 'fontSize': '14px'}),
            html.Div([
                html.Span([
                    "Rappel : Norme OMS = 5 µg/m³ | ",
                    "10 µg/m³ supplémentaires = environ 1 an de vie perdu"
                ], style={'fontSize': '12px', 'color': '#666'})
            ], style={'textAlign': 'center', 'marginBottom': '2rem'}),
        ]),
        dcc.Graph(id='histogram-years-lost', style={'height': '600px'})
    ], style={'margin': '2rem'})