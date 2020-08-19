
import json
import numpy
from shapely.geometry import shape, Point
from shapely.ops import unary_union
from tqdm import tqdm
from joblib import Parallel, delayed
from matplotlib import pyplot

earth_radius = 6371
step_distance = 11.11 # km


states_geo = json.load(open('gz_2010_us_040_00_500k.json', 'r'))
state_polys = [shape(state['geometry']) for state in states_geo['features']]

"""
us_polygon = unary_union(state_polys)

fig, axs = pyplot.subplots()
axs.set_aspect('equal', 'datalim')

for geom in us_polygon.geoms: 
    xs, ys = geom.exterior.xy    
    axs.fill(xs, ys, alpha=0.5, fc='r', ec='none')

pyplot.show()
"""


def gen_line(deci_latitude):
	line_lonlat = []

	latitude = deci_latitude/10
	print("latitude:", latitude)

	dlon = step_distance*360 / (2*earth_radius*numpy.pi*numpy.cos(latitude*numpy.pi/180))
	#print(dlon)

	longitude = -65 if latitude < 50 else -125
	for i in range(int(115//dlon)): # don't worry about truncation, because the US isn't in this spot
		p = Point((longitude, latitude))
		for poly in state_polys:
			if poly.contains(p):
				line_lonlat.append((longitude, latitude))
				break

		longitude -= dlon # step west

	print(len(line_lonlat))
	return line_lonlat


lines_lonlats = Parallel(n_jobs=7)(delayed(gen_line)(deci_latitude) for deci_latitude in tqdm(range(150, 750)))	


all_lonlat = [lonlat for line in lines_lonlats for lonlat in line]
json.dump(all_lonlat, open('lunkard.json', 'w'))

