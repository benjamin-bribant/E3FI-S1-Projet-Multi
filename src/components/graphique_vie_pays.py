"""
Composant : Graphique en barres de l'espérance de vie par région
"""
from dash import html, dcc
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd
from src.utils.mapping_region import get_region, calculate_years_lost


def create_life_expectancy_graph(year=None):
    """
    Crée le graphique en barres du dividende d'espérance de vie par région
    
    :param year int: Année à filtrer (None pour toutes les années)
    :returns plotly.graph_objects.Figure: Graphique Plotly
    """

    data = gpd.read_file("data/cleaned/cleaneddata.geojson")
    
    data = data[data['measurements_parameter'] == 'PM2.5']
    
    if year is not None:
        data['measurements_lastupdated'] = pd.to_datetime(data['measurements_lastupdated'])
        data = data[data['measurements_lastupdated'].dt.year == year]
    
    data['region'] = data['country'].apply(get_region)
    data['years_lost'] = data['measurements_value'].apply(calculate_years_lost)
    
    regional_data = data.groupby('region').agg({
        'years_lost': 'mean',
        'measurements_value': 'mean',
        'country': 'count'
    }).reset_index()
    
    regional_data.columns = ['region', 'avg_years_lost', 'avg_pm25', 'nb_measurements']
    
    regional_data = regional_data[regional_data['region'] != 'Autre']
    regional_data = regional_data.sort_values('avg_years_lost', ascending=True)
    
    fig = go.Figure()
    
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


def create_life_expectancy_section():
    """
    Crée la section HTML complète pour le graphique d'espérance de vie
    
    :returns html.Div: Section HTML avec titre, description et graphique
    """
    return html.Div([
        html.H2("Dividende d'Espérance de Vie par Région du Monde", 
                style={'textAlign': 'center', 'color': '#005093', 'marginTop': '2rem'}),
        
        html.Div([
            html.P([
                "Ce graphique transforme une mesure chimique abstraite (PM2.5) en une donnée humaine tangible : ",
                html.Strong("le temps de vie perdu."),
                " Il montre combien d'années les populations de chaque région gagneraient si la pollution aux PM2.5 ",
                "respectait les normes de l'OMS (5 µg/m³). C'est ce qu'on appelle le ",
                html.Strong("\"dividende d'espérance de vie\""),
                " : le bénéfice sanitaire potentiel d'une amélioration de la qualité de l'air."
            ], style={'textAlign': 'center', 'maxWidth': '900px', 'margin': '0 auto 1rem', 
                     'color': '#005093', 'fontSize': '14px'}),
            
            html.Div([
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
                style={'height': '600px', 'maxWidth': '85%', 'margin': '0 auto'}
            )
        ], style={'margin': '2rem'}),
        
        html.Div([
            html.Div([
                html.H4("Comment lire ce graphique :", 
                       style={'color': '#005093', 'marginBottom': '1rem'}),
                html.Ul([
                    html.Li([
                        html.Strong("Barres horizontales : "),
                        "Chaque barre représente une région géographique du monde (Asie du Sud, Europe, Amérique du Nord, etc.)."
                    ]),
                    html.Li([
                        html.Strong("Longueur des barres : "),
                        "Indique le nombre d'années d'espérance de vie gagnées si la pollution PM2.5 atteignait les normes OMS. ",
                        "Plus la barre est longue, plus le gain potentiel est important."
                    ]),
                    html.Li([
                        html.Strong("Couleur des barres : "),
                        "Dégradé de bleu du clair au foncé. Les couleurs sombres indiquent les régions avec le plus fort potentiel de gain."
                    ]),
                    html.Li([
                        html.Strong("Au survol : "),
                        "Vous pouvez voir le nombre d'années exactes, la concentration moyenne de PM2.5, et le nombre de mesures utilisées."
                    ])
                ], style={'color': '#005093', 'lineHeight': '2'}),
                
                html.Hr(style={'margin': '1.5rem 0', 'border': '1px solid #005093'}),
                
                html.H4("Ce que révèle ce graphique :", 
                       style={'color': '#005093', 'marginTop': '1.5rem', 'marginBottom': '1rem'}),
                html.Ul([
                    html.Li([
                        html.Strong("Inégalités mondiales : "),
                        "Les régions d'Asie du Sud et de l'Est sont les plus impactées, avec des gains potentiels de 3 à 6 ans d'espérance de vie. ",
                        "À l'inverse, l'Europe occidentale et l'Amérique du Nord ont des gains plus faibles (<1 an)."
                    ]),
                    html.Li([
                        html.Strong("Priorités d'action : "),
                        "Les régions avec les barres les plus longues devraient être prioritaires pour les politiques de réduction de la pollution. ",
                        "L'impact sanitaire y serait maximal."
                    ]),
                    html.Li([
                        html.Strong("Justice environnementale : "),
                        "Ce graphique illustre une injustice : les populations des pays en développement perdent plus d'années de vie à cause de la pollution, ",
                        "alors qu'elles contribuent historiquement moins aux émissions globales."
                    ]),
                    html.Li([
                        html.Strong("Potentiel d'amélioration : "),
                        "Même les régions avec de \"petites\" barres (comme l'Europe) peuvent gagner des centaines de milliers d'années de vie au total ",
                        "grâce à leur population importante."
                    ])
                ], style={'color': '#005093', 'lineHeight': '2'}),
                
                html.Hr(style={'margin': '1.5rem 0', 'border': '1px solid #005093'}),
                
                html.H4("Comparaison avec d'autres facteurs de risque :", 
                       style={'color': '#005093', 'marginTop': '1.5rem', 'marginBottom': '1rem'}),
                html.P([
                    "Pour mettre en perspective l'ampleur du problème, la pollution aux PM2.5 est ",
                    html.Strong("le plus grand risque environnemental pour la santé humaine", style={'color': '#DC2626'}),
                    " :"
                ], style={'color': '#005093', 'fontSize': '14px', 'marginBottom': '1rem'}),
                html.Ul([
                    html.Li("Plus mortelle que le tabagisme passif (perte de 1,8 an)"),
                    html.Li("Plus mortelle que la consommation d'alcool (perte de 1,6 an)"),
                    html.Li("Plus mortelle que les accidents de la route (perte de 0,7 an)"),
                    html.Li("Plus mortelle que les conflits et le terrorisme (perte de 0,3 an)")
                ], style={'color': '#005093', 'lineHeight': '2', 'fontSize': '14px'}),
                
                html.Hr(style={'margin': '1.5rem 0', 'border': '1px solid #005093'}),
                
                html.H4("Message clé :", 
                       style={'color': '#005093', 'marginTop': '1.5rem', 'marginBottom': '1rem'}),
                html.P([
                    "Si toutes les régions du monde respectaient la norme OMS de 5 µg/m³ de PM2.5, ",
                    html.Strong("l'humanité gagnerait collectivement 2,3 ans d'espérance de vie en moyenne", style={'color': '#005093', 'fontSize': '16px'}),
                    ". Cela représente des milliards d'années de vie gagnées au niveau mondial. ",
                    "C'est un enjeu sanitaire majeur qui mérite autant d'attention que les grandes maladies infectieuses."
                ], style={'color': '#005093', 'fontSize': '14px', 'lineHeight': '1.8', 
                         'fontStyle': 'italic', 'padding': '1rem', 'backgroundColor': '#E3F2FD', 
                         'borderRadius': '8px', 'border': '2px solid #005093'})
            ], style={
                'maxWidth': '900px',
                'margin': '2rem',
                'padding': '2rem',
                'backgroundColor': '#f8f9fa',
                'borderRadius': '10px',
                'border': '2px solid #005093'
            })
        ], style={'display': 'flex',
                 'justifyContent' : 'center'})
    ], style={'margin': '2rem'})