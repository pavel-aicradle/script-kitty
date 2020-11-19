#@author Brian Rodriguez and Pavel Komarov

import os
import json
import time
from tqdm import tqdm
from argparse import ArgumentParser
from joblib import Parallel, delayed
from multiprocessing import current_process
from shapely.geometry import shape, Point


def mkdir(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

parser = ArgumentParser()
parser.add_argument("--folder", required=True)
parser.add_argument("--destination", required=True)
args = parser.parse_args()


# grab the state outline from files
utah_geojson = json.load(open('utah.json', 'r'))['hits']['hits'][0]['_source']['geo'] # gross
ohio_geojson = json.load(open('ohio.json', 'r'))
utah_polygon = shape(utah_geojson)
ohio_polygon = shape(ohio_geojson)

states = ['UT', 'OH']

# Point to a collection of day-folders somewhere. This is going to iterate them all, so watch out.
folders = [os.path.join(args.folder, f)
    for f in os.listdir(args.folder)
    if os.path.isdir(os.path.join(args.folder, f))]

mkdir(args.destination)

for state in states:
    mkdir('/'.join([args.destination, state, 'alerts']))
    mkdir('/'.join([args.destination, state, 'jams']))


# provide a place to put all alerts and jams for each state. alerts and jams are stored as
# 2D lists, where the first dimension is the hour of the week, and the second stores multiple
# records from that hour.
filtered = {state: {"alerts":[[] for _ in range(168)], "jams":[[] for _ in range(168)]}
    for state in states}

# define this in a separate function for parallelism purposes
def filter_day(folder):
    p_utah_alerts = [[] for _ in range(168)] # "p" for "process"
    p_utah_jams = [[] for _ in range(168)]
    p_ohio_alerts = [[] for _ in range(168)]
    p_ohio_jams = [[] for _ in range(168)]

    # It looks like each record has a time created associated with it. But records don't reach
    # the server exactly then. They might be delayed, even indefinitely if the user shuts off
    # their client. This funciton checks to make sure records are really "live", associated with
    # the appropriate aggregation window on the server, as given by startTime and endTime
    # We're giving a grace period of a minute here (60k milliseconds), because it takes some
    # time for things to propagate to the Waze server. This allows us to keep ~95% of records
    # while throwing away a very noisy 5%.
    def time_filter(t, startTimeMillis, endTimeMillis): return t > startTimeMillis - 60000 and t <= endTimeMillis

    # point here is a geographical location in lon, lat. polygon is a state border.
    def spatial_filter(point, polygon): return polygon.contains(point)

    def compute_week_hour(t):
        utc_time = time.gmtime(t / 1000)
        return utc_time.tm_wday*24 + utc_time.tm_hour # compute hour of the week


    process_number = current_process()._identity[0]
    for file in tqdm(os.listdir(folder), position=process_number-1):
        if file.endswith('.json'):
            with open(os.path.join(folder, file)) as f: # careful of relative paths here
                json_file = json.load(f)

                # We believe these are the times over which the the Waze server was aggregating these records
                # Because we're LiveTime, we need to toss records that aren't near real time.
                startTimeMillis = json_file['startTimeMillis']
                endTimeMillis = json_file['endTimeMillis']

                alerts = json_file["alerts"]
                for alert in alerts:
                    t = alert["pubMillis"]
                    if not time_filter(t, startTimeMillis, endTimeMillis): continue

                    week_hour = compute_week_hour(t)
                    location = Point((alert["location"]["x"], alert["location"]["y"]))

                    if spatial_filter(location, utah_polygon):
                        p_utah_alerts[week_hour].append(alert)

                    elif spatial_filter(location, ohio_polygon):
                        p_ohio_alerts[week_hour].append(alert)

                jams = json_file["jams"]
                for jam in jams:
                    t = jam["pubMillis"]
                    if not time_filter(t, startTimeMillis, endTimeMillis): continue

                    week_hour = compute_week_hour(t)
                    location = Point((jam["line"][0]["x"], jam["line"][0]["y"]))

                    if spatial_filter(location, utah_polygon):
                        p_utah_jams[week_hour].append(jam)

                    elif spatial_filter(location, ohio_polygon):
                        p_ohio_jams[week_hour].append(jam)

    return p_utah_alerts, p_utah_jams, p_ohio_alerts, p_ohio_jams


per_file_results = Parallel(n_jobs=4)(delayed(filter_day)(folder) for folder in tqdm(folders))

for i in range(168):
    for ut_alerts, ut_jams, oh_alerts, oh_jams in per_file_results:
        filtered['UT']['alerts'][i].extend(ut_alerts[i])
        filtered['UT']['jams'][i].extend(ut_jams[i])
        filtered['OH']['alerts'][i].extend(oh_alerts[i])
        filtered['OH']['jams'][i].extend(oh_jams[i])

for state in filtered:
    for record_type in filtered[state]:
        for hour in range(len(filtered[state][record_type])):
            with open("/".join([args.destination, state, record_type]) + f"/{hour}.json", "w") as f:
                json.dump(filtered[state][record_type][hour], f)

