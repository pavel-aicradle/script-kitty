
import json
from shapely.geometry import shape, Point
from collections import defaultdict
from tqdm import tqdm

macros = json.load(open('lunkard.json', 'r'))

states_geo = json.load(open('gz_2010_us_040_00_500k.json', 'r'))
counties_geo = json.load(open('gz_2010_us_050_00_500k.json', 'r', errors='ignore'))


num2state = {state['properties']['STATE']: (state['properties']['NAME'], shape(state['geometry']))
	for state in states_geo['features']} # map state number -> (state name, polygon)
num2counties = {state['properties']['STATE']: [] for state in states_geo['features']} # map state number -> [(county name, polygon), ...]
for county in counties_geo['features']:
	#if county['LSAD'] != 'city': #in ['County', 'Parish', 'CA', 'Borough', 'Muno']:
	num2counties[county['properties']['STATE']].append((county['properties']['NAME'], county['properties']['LSAD'], shape(county['geometry'])))



#def process_record(record, is_alert, startTimeMillis, endTimeMillis):
all_map = defaultdict(list)

def find_county(p):
	ret = []

	for state_num, (state_name, state_polygon) in num2state.items(): # iterate all states
		if state_polygon.contains(p): # then use that state_num to index counties
			
			for name, lsad, polygon in num2counties[state_num]: # iterate associated counties
				if polygon.contains(p):
					ret.append((state_name, name, lsad))
	return ret


for lon, lat in tqdm(macros):
	p = Point((lon, lat))
	ks = find_county(p)

	if len(ks) == 0: print("no county found for point:", lon, lat)
	else:
		for k in ks:
			all_map[str(k)].append((lon, lat))

print(len(all_map))

json.dump(all_map, open('lunkard_by_county2.json', 'w'))
