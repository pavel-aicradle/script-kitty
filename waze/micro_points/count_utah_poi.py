
import pandas
import json
from shapely.geometry import shape, Point
from collections import defaultdict
from tqdm import tqdm

counties_geo = json.load(open('../macro_points/gz_2010_us_050_00_500k.json', 'r', errors='ignore'))
utah_counties = {}

for county in counties_geo['features']:
	if county['properties']['STATE'] == '49':
		utah_counties[county['properties']['NAME']] = shape(county['geometry'])


poi = pandas.read_csv('poi.csv')


POI_CATEGORIES = {
	'Retail Stores': 'Retail Stores',
	'Hospitals': 'Hospitals',
	'Health / Medical': 'Hospitals',
	'Restaurants': 'Restaurants',
	'Fast Food Restaurants': 'Restaurants',
	'Transportation': 'Transportation',
	'Airports': 'Transportation',
	'Parks / Monuments': 'Parks / Monuments',
	'Lodging': 'Lodging',
	'Government Buildings': 'Government Buildings',
	'Religious': 'Religious',
	'Schools': 'Schools',
	'Gas Stations': 'Gas Stations'
}

counties_counts = defaultdict(lambda: defaultdict(int))

for i in tqdm(range(len(poi))):
	row = poi.loc[i]

	if row['state'] in ['UT', 'Utah']:
		p = Point((row['longitude'], row['latitude'])) # lon is x, lat is y

		for county_name, poly in utah_counties.items():
			if poly.contains(p): # then we've found our county

				try:
					category = POI_CATEGORIES[row['business_type']]
					counties_counts[county_name][category] += 1
				except:
					pass

				break

s = counties_counts.__str__()[48:]
s = s.replace("defaultdict(<class 'int'>, ", "")
s = s.replace("})", "}")

print(s)