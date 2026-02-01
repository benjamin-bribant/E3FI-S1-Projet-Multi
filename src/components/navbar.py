from dash import html

def create_navbar():
    return html.Nav([
        html.Div([
            html.A([
                html.Img(src="/assets/img/globe_icon.svg", alt="Globe"),
                html.Span("Carte")
            ], id="nav-carte", className="nav-item", n_clicks=0),
            html.A([
                html.Img(src="/assets/img/bar_char_icon.svg", alt="Graphique"),
                html.Span("Graphiques")
            ], id="nav-graphiques", className="nav-item", n_clicks=0),
        ], className="nav-container")
    ], className="navbar")