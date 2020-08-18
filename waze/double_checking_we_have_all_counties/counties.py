"""
import json
from pickle import dump

with open('counties.json') as f: # careful of relative paths here
	rows = json.load(f)['tbody']

	county_states = set()
	for row in rows:
		try:
			county, state = row[0]['a']['@title'].split(', ')
			county = county.replace('–', '-')
			county_states.add((county, state))
		except:
			county_states.add((row[0]['a']['@title'], None))

dump(county_states, open('county_states.pkl', 'wb'))

"""
import json
from pickle import load

#county_states = load(open('county_states.pkl', 'rb'))



#states_geo = json.load(open('gz_2010_us_040_00_500k.json', 'r'))
counties_geo = json.load(open('gz_2010_us_050_00_500k.json', 'r', errors='ignore'))


for county in counties_geo['features']:
	if county['properties']['STATE'] == '46' and county['properties']['NAME'] == 'Shannon':
		print("success")


#num2counties = {state['properties']['STATE']: [] for state in states_geo['features']} # map state number -> [(county name, polygon), ...]
#for county in counties_geo['features']:
#    num2counties[county['properties']['STATE']].append(county['properties']['NAME'])


"""
num2state = {state['properties']['STATE']: state['properties']['NAME']
    for state in states_geo['features']} # map state number -> (state name, polygon)
num2counties = {state['properties']['STATE']: [] for state in states_geo['features']} # map state number -> [(county name, polygon), ...]
for county in counties_geo['features']:
    num2counties[county['properties']['STATE']].append(county['properties']['NAME'])

seen = set()
not_seen = set()

total_in_geojson = 0
for state_num in num2state:
	state_name = num2state[state_num]
	for county_name in num2counties[state_num]:
		total_in_geojson += 1

		for c, s in county_states:
			if (state_name == s and county_name in c) or (s is None and county_name == c):
				seen.add((c,s))
				break
		else:
			if state_name != 'Puerto Rico':
				not_seen.add((county_name, state_name))

# because I manually established all puerto rico is present
for c, s in county_states:
	if s == 'Puerto Rico':
		seen.add((c,s))


print("number of matches found:", len(seen))
print("total counties in geojson:", total_in_geojson)
print("entries from wikipedia not in the geojson:", county_states-seen)
print("entries in geojson not on wikipedia:", not_seen)
"""

