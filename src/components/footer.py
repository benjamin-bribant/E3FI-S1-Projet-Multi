from dash import Dash, dcc, html

def create_footer():
    return html.Footer([
        html.Div([
            html.H3("CONTACT"),
            html.P("benjamin.bribant@edu.esiee.fr"),
            html.P("india.cabo@edu.esiee.fr"),
            html.Br(),
            html.P("Site réalisé par Benjamin BRIBANT et India CABO"),
            html.P("Groupe 1l"),
        ]),
    ])
