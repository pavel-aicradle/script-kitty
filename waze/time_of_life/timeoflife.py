
import json
import os
import numpy
from matplotlib import pyplot
from collections import defaultdict
from tqdm import tqdm
from pickle import dump

choice = 'raw'

files = [f for f in os.listdir('output/'+choice) if f.endswith('.json')]

uuids = defaultdict(set)

all_minutes = set()

for file in tqdm(files):
	with open('output/'+choice+'/'+file) as f:
		records = json.load(f)

		minute = file[11:15]
		all_minutes.add(minute)

		for record in records['alerts']:
			#if record['uuid']=='47d1c056-bcbc-3cbd-a668-1f549c9b48f2':
			#	if minute not in uuids['47d1c056-bcbc-3cbd-a668-1f549c9b48f2']:
			#		print(record)

			uuids[record['uuid']].add(minute)

print(sorted(list(all_minutes)))
for iden in ['e2f85dd9-f632-36a7-8a2d-34086dd6a78b', '08cb37f2-ab39-3639-950e-5f0d6498631d', 'e28d8e30-dbac-35f0-a775-332326b416a7']:
	print('-----------')
	print(all_minutes - uuids[iden])

for k,v in uuids.items(): # convert from sets to just counts
	uuids[k] = len(v)

max_time = max(uuids.values())
print(max_time)
#dump(uuids, open('uuids.pkl', 'wb'))

print([k for k,v in uuids.items() if v==max_time-2][:3])

lengths = numpy.zeros(max_time)

for uuid, n_minutes in uuids.items():
	lengths[n_minutes-1] += 1

pyplot.bar(range(1, max_time+1), lengths)
pyplot.title('time of life of active Waze updates')
pyplot.xlabel('minutes')
pyplot.ylabel('number of uuids with that time of life')
pyplot.show()