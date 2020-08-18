
import json
from shapely.geometry import shape
from shapely.ops import unary_union
from matplotlib import pyplot

counties_geo = json.load(open('gz_2010_us_050_00_500k.json', 'r', errors='ignore'))

us_polygon = unary_union([shape(county['geometry']) for county in counties_geo['features'] if county['properties']['LSAD'] != "city"])


## plot it
fig, axs = pyplot.subplots()
axs.set_aspect('equal', 'datalim')

for geom in us_polygon.geoms:    
    xs, ys = geom.exterior.xy  
    axs.fill(xs, ys, alpha=0.5, fc='b', ec='none')

pyplot.show()