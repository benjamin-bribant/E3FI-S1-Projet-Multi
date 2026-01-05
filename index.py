from dash import Dash, dcc, html
from src.components.footer import create_footer


app = Dash()

app.layout = html.Div([
    html.H1("Dashboard - World Air Quality", style={'text-align':'center'}, className="page-title"),
    html.Div([
        dcc.Slider(
            min=2015, 
            max=2025, 
            step=1,
            marks={i: str(i) for i in range(2015, 2026)},
            id="year-slider",
            className="custom-slider"
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
    
    html.H1("CARTE", style={'text-align':'center'}, className="page-title"),
    
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
                html.Button('PM2.5', id='', n_clicks=0),
                html.Button('PM10', id='', n_clicks=0),
                html.Button('CO', id='', n_clicks=0),
            ]),
            html.Div([
                html.Button('NO2', id='', n_clicks=0),
                html.Button('SO2', id='', n_clicks=0),
                html.Button('O3', id='', n_clicks=0),
            ]),
        ], className="buttons-polluants")
    ], style={'display': 'flex', 'justify-content':'center'}, className="below-map"),
    
    html.Div([
        html.Table([
            html.Thead([
                html.Tr([
                    html.Th(""),
                    html.Th("Pays"),
                    html.Th("Unité"),
                    html.Th("Valeur"),
                    html.Th("Date"),
                ])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td("Pays 1"),
                    html.Td("Pays 1"),
                    html.Td("Pays 1"),
                    html.Td("Pays 1"),
                    html.Td("Pays 1"),
                ]),
                html.Tr([
                    html.Td("Pays 1"),
                    html.Td("Pays 1"),
                    html.Td("Pays 1"),
                    html.Td("Pays 1"),
                    html.Td("Pays 1"),
                ]),
                html.Tr([
                    html.Td("Pays 1"),
                    html.Td("Pays 1"),
                    html.Td("Pays 1"),
                    html.Td("Pays 1"),
                    html.Td("Pays 1"),
                ]),
            ])
        ],)
    ], className="ranking"),
    create_footer()
])

if __name__ == '__main__':
    app.run(debug=True)