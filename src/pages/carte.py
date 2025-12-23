import geopandas as gpd
import pandas as pd
import folium

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


def main():
    data = gpd.read_file("../../data/cleaned/cleaneddata.geojson")
    
    carte = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles='OpenStreetMap',
        control_scale=True
    )
    
    for idx, row in data.iterrows():
        lat = row.geometry.y
        lon = row.geometry.x
        
        folium.CircleMarker(
            location=[lat, lon],
            radius=5,
            popup=folium.Popup(max_width=300),
            tooltip=f"{row['measurements_parameter']}: {row['measurements_value']} {row.get('measurements_unit', '')}",
            color=get_color_by_pollutant(row['measurements_parameter']),
            fill=True,
            fillColor=get_color_by_pollutant(row['measurements_parameter']),
            fillOpacity=0.6,
            weight=2
        ).add_to(carte)
    

    folium.LayerControl().add_to(carte)

    carte.save(outfile='map.html')


if __name__ == "__main__":
    main()