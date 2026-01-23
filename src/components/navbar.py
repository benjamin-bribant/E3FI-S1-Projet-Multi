from dash import html

def create_navbar():
    return html.Nav([
        html.Div([
            html.A([
                html.Img(src="/assets/img/globe_icon.svg", alt="Globe"),
                html.Span("Carte")
            ], href="#carte", className="nav-item"),
            html.A([
                html.Img(src="/assets/img/bar_char_icon.svg", alt="Graphique"),
                html.Span("Graphiques")
            ], href="#graphiques", className="nav-item"),
        ], className="nav-container")
    ], className="navbar")