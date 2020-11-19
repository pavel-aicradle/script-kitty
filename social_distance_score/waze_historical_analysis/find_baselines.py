# @author Pavel

# This script iterates records produced by filter_and_sort.py to create a map from
# (state, county) -> 168 week-hours. Each week-hour has multiple numbers associated:
# |alerts|, sum(rating(alerts)), sum(reliability(alerts)), |jams|,
# sum(length(jams)), sum(delay(jams)), sum(speed(jams))
# This is to give us maximum flexibility, because we're not yet sure which of these
# or what weighted combination of them is most informative.

import os
import numpy
import json
import pickle
from argparse import ArgumentParser
from tqdm import tqdm
from joblib import Parallel, delayed
from pandas import DataFrame
from collections import defaultdict
from datetime import date

parser = ArgumentParser()
parser.add_argument('--folder', required=True, help='a folder containing alert and jam json files')
parser.add_argument('--n_jobs', required=True, type=int, help='number of processes to spawn to parallelize this task')
args = parser.parse_args()

alerts_files = [f for f in os.listdir(args.folder) if f.endswith('_alerts.json')]
jams_files = [f for f in os.listdir(args.folder) if f.endswith('_jams.json')]


# standalone function for parallelization
def process_records(file, is_alerts):
	records = json.load(open(args.folder+'/'+file, 'r'))
	width = 3 if is_alerts else 4
	records_map = defaultdict(lambda: numpy.zeros((168,width), dtype='<f8')) # use 8 bytes so no danger of overflow

	for record in records:
		row = records_map[(record['state'], record['county'])][record['week_hour']] # the row of the table to update

		if is_alerts: # schema goes: |alerts|, sum(rating(alerts)), sum(reliability(alerts))
			row[0] += 1
			row[1] += record['reportRating'] # confidence based on other users' votes
			row[2] += record['reliability'] # ratings of the user https://support.google.com/waze/partners/answer/6324421?hl=en

		else: # schema goes |jams|, sum(length(jams)), sum(delay(jams)), sum(speed(jams))
			row[0] += 1
			row[1] += record['length']
			row[2] += record['delay']
			row[3] += record['speed']

	return records_map

alerts_maps = Parallel(n_jobs=args.n_jobs)(delayed(process_records)(f, True) for f in tqdm(alerts_files))
jams_maps = Parallel(n_jobs=args.n_jobs)(delayed(process_records)(f, False) for f in tqdm(jams_files))


# join together the counts. I'm just doing this in memory with the parallel results, because the return values should
# be fairly lightweight.
joined_map = defaultdict(lambda: numpy.zeros((168,7), dtype='<f8'))
for m in alerts_maps:
	for state_county, counts in m.items():
		joined_map[state_county][:,:3] += counts
for m in jams_maps:
	for state_county, counts in m.items():
		joined_map[state_county][:,3:] += counts

# normalize the counts. We have 89 days here, so that's something like 12 of each kind of day, 13 for some
n_weekday = numpy.zeros(7)
for f in alerts_files:
	n_weekday[date(int(f[:4]), int(f[5:7]), int(f[8:10])).weekday()] += 1 # pull out the date and get day number from it

for state_county, counts in joined_map.items(): # counts is a *pointer* to a numpy array here, so modifying it updates the dictionary
	for day in range(7):
		counts[day*24:(day+1)*24] /= n_weekday[day]

# convert all those numpy arrays to DataFrames so the fields are labeled, and make this a normal dict
# rather than defaultdict of a lambda, because Python can't pickle the latter.
baselines_map = {state_county: DataFrame(data=counts, columns=['n_alerts', 'rating_alerts',
		'reliability_alerts', 'n_jams', 'length_jams', 'delay_jams', 'speed_jams'])
		for state_county, counts in joined_map.items()}
pickle.dump(baselines_map, open('baselines_map.pkl', 'wb'))

