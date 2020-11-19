
import json
import numpy
from matplotlib import pyplot
from tqdm import tqdm

f = open('historical3.jsonl', 'r')

all_isochron_fractions = []


# so I can recover isochron fraction from scores
def inv_score(y):
	if y >= 10:
		x = 1.1

	elif 9.5 <= y < 10:
		x = (y-4.5)/5

	elif 7 <= y < 9.5:
		x = (y+15.5)/25

	elif 5 <= y < 7:
		x = (y+2)/10

	elif 0 <= y < 5:
		x = y/7.14

	else:
		raise ValueError("y out of range")

	return x


counts = numpy.zeros(3)

for line in tqdm(f):
	record = json.loads(line)

	#if record['state_name'] != 'Utah':
	#	print(record['state_name'])

	values = [] # because Josh changed the record format a few times, there are a few different things values could be
	for point_name, v in record['query_location_scores']['query_scores'].items():
		#if (point_name[4:6] == '||' and len(point_name) == 16):
		values.append(v)

	if len(values) > 500:
		print(record['state_name'], record['county_name'], len(values))

	# most recent case
	if 'dict' in str(type(values[0])):
		#for p in values:
		#	if p['current_area']/p['baseline_area'] > 2:
		#		print(p)

		all_isochron_fractions += [p['current_area']/p['baseline_area'] for p in values]
		counts[0] += 1
		pass

	# intermediate case
	elif numpy.mean(values) > 1:
		#all_isochron_fractions += [inv_score(y) for y in values]
		#counts[1] += 1
		pass

	# oldest case
	elif numpy.mean(values) <= 1:
		#all_isochron_fractions += values
		#counts[2] += 1
		pass

	else:
		raise ValueError("unexpected json format")

print("total number of isochron fractions:", len(all_isochron_fractions))
print("min, max:", min(all_isochron_fractions), max(all_isochron_fractions))
print("newest, med, oldest format counts:", counts)

pyplot.hist(all_isochron_fractions, bins=300)
pyplot.title('histogram of isochron area : baseline area ratios, \nonly points with truly both areas, only (macro) points')
pyplot.ylabel('number of isochrons falling in buckets')
pyplot.xlabel('A_current / A_baseline fraction')
pyplot.show()

with open('franz_vector.csv', 'w') as out:
	s = all_isochron_fractions.__str__().replace(" ", "")
	out.write(s[1:-1])

