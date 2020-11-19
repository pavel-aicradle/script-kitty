# @author Josh I think 
# a script to plot points on an interactive map

import folium
import logging
import json
from flask import Flask

points = json.load(open('lunkard.json', 'r'))[-5000:]


logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

app = Flask(__name__)

ROOT_COORDINATES = [40.76717, -111.90556]
GEOHASH_PRECISION_LEVEL_SIX = 6

def add_geo_feature_markers(signals, event_map):
    for signal in signals:
        geo_json = signal.geo_json
        tooltip = signal.category
        folium.GeoJson(geo_json, tooltip=tooltip).add_to(event_map)

def add_pin_markers(signals, event_map):
    for signal in signals:
        longitude, latitude = signal
        context = "signal.context"
        popup = "<i>" + context + "</i>"
        tooltip = "Click Me!"
        folium.Marker([latitude, longitude], popup=popup, tooltip=tooltip).add_to(event_map)

@app.route("/map/view")
def render_micro():
    event_map = folium.Map(location=ROOT_COORDINATES, zoom_start=11, opacity=1)
    add_pin_markers(points, event_map)
    return event_map.get_root().render()

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True, port=5001)