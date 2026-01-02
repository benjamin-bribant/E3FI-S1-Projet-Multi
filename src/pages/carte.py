import geopandas as gpd
import pandas as pd
import folium
from folium.plugins import MarkerCluster

def get_color_by_pollutant(pollutant):
    colors = {
        'PM2.5': 'red',
        'PM10': 'orange',
        'CO': 'purple',
        'NO2': 'blue',
        'SO2': 'green',
        'O3': 'lightblue'
    }
    return colors.get(pollutant, 'gray')

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

def create_popup_text(row):
    pollutant = row['measurements_parameter']
    value = row['measurements_value']
    unit = row.get('measurements_unit', '')
    location = row.get('location', 'Localisation inconnue')
    country = row.get('country_name_en', row.get('country', 'N/A'))
    last_updated = row.get('measurements_lastupdated', 'N/A')
    
    level = get_pollution_level(pollutant, value)
    
    popup_text = f"""<b>{location}</b><br>
━━━━━━━━━━━━━━━━━━━━<br>
<b>Pays:</b> {country}<br>
<b>Polluant:</b> {pollutant}<br>
<b>Valeur:</b> {value} {unit}<br>
<b>Niveau de pollution:</b> {level}<br>
<b>Mis à jour:</b> {last_updated}"""
    
    return popup_text

def main():
    data = gpd.read_file("../../data/cleaned/cleaneddata.geojson")
    
    carte = folium.Map(
        location=[20, 0],
        zoom_start=2,
        control_scale=True,
        prefer_canvas=True,
        max_bounds=True,
        min_zoom=2,
        max_zoom=18,
        min_lat=-85,
        max_lat=85,
        min_lon=-180,
        max_lon=180
    )
    
    marker_cluster = MarkerCluster(
        name='Points de mesure',
        overlay=True,
        control=True,
        icon_create_function=None
    ).add_to(carte)
    
    for idx, row in data.iterrows():
        lat = row.geometry.y
        lon = row.geometry.x
        
        popup_text = create_popup_text(row)
        
        folium.CircleMarker(
            location=[lat, lon],
            radius=10,
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=f"{row['measurements_parameter']}: {row['measurements_value']} {row.get('measurements_unit', '')}",
            color=get_color_by_pollutant(row['measurements_parameter']),
            fill=True,
            fillColor=get_color_by_pollutant(row['measurements_parameter']),
            fillOpacity=0.6,
            weight=2
        ).add_to(marker_cluster)
    
    folium.LayerControl().add_to(carte)
    
    carte.save(outfile='map.html')

if __name__ == "__main__":
    main()