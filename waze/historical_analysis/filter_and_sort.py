#@author Pavel Komarov and Brian Rodriguez
# This script is meant to extract Waze data from .json files living in daily directories. NOTE you need
# the associated json from https://eric.clst.org/tech/usgeojson/ for this to work.

import os
import json
import time
from tqdm import tqdm
from argparse import ArgumentParser
from joblib import Parallel, delayed
from multiprocessing import current_process
from shapely.geometry import shape, Point
#from shapely.ops import unary_union


parser = ArgumentParser()
parser.add_argument('--folder', required=True, help='a folder containing other Waze day-folders, which in turn hold json') 
parser.add_argument('--destination', required=True, help="where to store outputs; okay if doesn't exist yet")
parser.add_argument('--n_jobs', required=True, type=int, help='number of processes to spawn to parallelize this task')
args = parser.parse_args()

if not os.path.exists(args.destination): os.makedirs(args.destination)
# Point to a collection of day-folders somewhere. This is going to iterate them all, so watch out.
folders = [f for f in os.listdir(args.folder) if os.path.isdir(os.path.join(args.folder, f))]


# I'm getting all my map polygons from https://eric.clst.org/tech/usgeojson/ The filenames
# used here are the default names of those files, so you should be able to just download and run.
# The idea is to do a hierarchical search: If a point is inside the US, then search for state.
# Once state is determined, query against counties in that state.
states_geo = json.load(open('gz_2010_us_040_00_500k.json', 'r'))
counties_geo = json.load(open('gz_2010_us_050_00_500k.json', 'r', errors='ignore'))
# There's a complication, though: Because there's no nice json for the multipolygon of the US,
# I have to compute it. Ah! This actually slows the script down; querying against it must not be easy
#us_polygon = unary_union([shape(state['geometry']) for state in states_geo['features']])


# Counties aren't labeled with state names; they're labeled by state number. I'm just accepting this as the standard
# because it makes my datastructures here uniform: number -> (name, polygon)
num2state = {state['properties']['STATE']: (state['properties']['NAME'], shape(state['geometry']))
    for state in states_geo['features']} # map state number -> (state name, polygon)
num2counties = {state['properties']['STATE']: [] for state in states_geo['features']} # map state number -> [(county name, polygon), ...]
for county in counties_geo['features']:
    if county['LSAD'] != 'city': #in ['County', 'Parish', 'CA', 'Borough', 'Muno']:
        num2counties[county['properties']['STATE']].append((county['properties']['NAME'], shape(county['geometry'])))


## Helper functions

# It looks like each record has a time created associated with it. But records don't reach
# the server exactly then. They might be delayed, even indefinitely if the user shuts off
# their client. This funciton checks to make sure records are really "live", associated with
# the appropriate aggregation window on the server, as given by startTime and endTime
# We're giving a grace period of a minute here (60k milliseconds), because it takes some
# time for things to propagate to the Waze server. This allows us to keep ~95% of records
# while throwing away a very noisy 5%. If a time is "good", then the week-hour is returned.
# Otherwise None is returned.
def good_time(t, startTimeMillis, endTimeMillis):
    if t > startTimeMillis - 60000 and t <= endTimeMillis:
        utc_time = time.gmtime(t / 1000)
        return utc_time.tm_wday*24 + utc_time.tm_hour # compute hour of the week
    return None

# iterate over states and counties looking for a match. If no match, Nones are returned.
# query states in order of population

def good_location(p):
    #if us_polygon.contains(p): # expensive call, and most updates are from inside the US
    for state_num, (state_name, state_polygon) in num2state.items(): # iterate all states
        if state_polygon.contains(p): # then use that state_num to index counties
            for county_name, county_polygon in num2counties[state_num]: # iterate associated counties
                if county_polygon.contains(p):
                    return (state_name, county_name) # I'm presuming that iff you're in a state, you're also in one of its counties
    return None, None # because default single None return breaks double assignment (cannot unpack)

# because records and jams share a lot of the same logic, and I don't want to make you read it twice.
def process_record(record, is_alert, startTimeMillis, endTimeMillis):
    week_hour = good_time(record['pubMillis'], startTimeMillis, endTimeMillis)
    if week_hour is None: return

    p = Point((record['location']['x'], record['location']['y'])) if is_alert \
        else Point(( (record['line'][0]['x']+record['line'][-1]['x'])/2,
                     (record['line'][0]['y']+record['line'][-1]['y'])/2 )) # average first and last points
    state, county = good_location(p)
    if state is None: return

    # add these fields to the record
    record['week_hour'] = week_hour
    record['state'] = state
    record['county'] = county
    if not is_alert: record['location'] = {'x':p.x, 'y':p.y}

    # remove some fields that aren't so useful to us
    if 'country' in record: del record['country']
    if 'magvar' in record: del record['magvar'] # magnetic variation? magnitude of variation?
    del record['uuid']
    if not is_alert:
        del record['line']
        if 'endNode' in record: del record['endNode']
        del record['turnType']
        del record['segments']

    return record


## This is where the bulk of the work starts. Define this in a separate function for parallelism purposes.
def filter_day(day_folder):
    # A place to accumulate json records
    proc_alerts = []
    proc_jams = []

    # Iterate over each record of each file in the folder. Each process gets its own tqdm bar.
    for file in tqdm(os.listdir(os.path.join(args.folder, day_folder)),
        position=current_process()._identity[0] if args.n_jobs > 1 else 1):

        if file.endswith('.json'):
            with open(os.path.join(args.folder, day_folder, file)) as f: # careful of relative paths here
                records = json.load(f)

                # We believe these are the times over which the the Waze server was aggregating these records
                # Because we're LiveTime, we need to toss records that aren't near real time.
                startTimeMillis = records['startTimeMillis']
                endTimeMillis = records['endTimeMillis']

                # process alerts and jams
                for alert in records['alerts']:
                    pared = process_record(alert, True, startTimeMillis, endTimeMillis)
                    if pared: proc_alerts.append(pared)

                for jam in records['jams']:
                    pared = process_record(jam, False, startTimeMillis, endTimeMillis)
                    if pared: proc_jams.append(pared)

    with open(args.destination+'/'+day_folder+'_alerts.json', 'w') as f: json.dump(proc_alerts, f)
    with open(args.destination+'/'+day_folder+'_jams.json', 'w') as f: json.dump(proc_jams, f)


Parallel(n_jobs=args.n_jobs)(delayed(filter_day)(day_folder) for day_folder in tqdm(folders))

