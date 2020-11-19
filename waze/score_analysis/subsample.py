
import json
import numpy
from matplotlib import pyplot
from tqdm import tqdm

STATE = 'Utah'
COUNTY = 'Salt Lake'

f = open('historical3.jsonl', 'r')


# so I can score based on isochron fraction
def score(x):
	if x >= 1.1:
		y = 10

	elif 1 <= x < 1.1:
		y = 5*x + 4.5

	elif 0.9 <= x < 1:
		y = 25*x - 15.5

	elif 0.7 <= x < 0.9:
		y = 10*x - 2

	elif 0 <= x < 0.7:
		y = 7.14*x

	else:
		raise ValueError("x out of range:", x)

	return y



all_scores = [] # for the chosen county, that is
n_county_hours = 0
counts = numpy.zeros(3)

for line in tqdm(f):
	record = json.loads(line)

	#if record['state_name'] == STATE and record['county_name'] == COUNTY:
	#	n_county_hours += 1

	values = [] # because Josh changed the record format a few times, there are a few different things values could be
	for point_name, v in record['query_location_scores']['query_scores'].items():
		if (point_name[4:6] == '||' and len(point_name) == 16): # only grab PoI or geographic grid points
			values.append(v)

	# most recent case
	if 'dict' in str(type(values[0])):
		all_scores.append([p['normalized_score'] for p in values])
		counts[0] += 1
		pass

	# intermediate case
	elif numpy.mean(values) > 1:
		all_scores.append(values)
		counts[1] += 1
		pass

	# oldest case
	elif numpy.mean(values) <= 1:
		#all_scores += [score(v) for v in values]
		#counts[2] += 1
		pass

	else:
		raise ValueError("unexpected json format")


all_scores_flat = [x for hour_scores in all_scores for x in hour_scores]

print("number of times",COUNTY,",",STATE,"shows up in the data:", n_county_hours)
print("total number of scores:", len(all_scores_flat))
print("min, max:", min(all_scores_flat), max(all_scores_flat))
print("newest, med, oldest format counts:", counts)

pyplot.figure(1)
pyplot.hist(all_scores_flat, bins=300)
pyplot.title('histogram of scores over all hours, just grid points')
pyplot.ylabel('number of PoIs falling in buckets')
pyplot.xlabel('0-10 score')
pyplot.show()

"""
pyplot.figure(2)
pyplot.hist(all_scores[-1], bins=300)
pyplot.title('histogram of scores over last hour')
pyplot.ylabel('number of PoIs falling in buckets')
pyplot.xlabel('0-10 score')
"""

"""

scatters = []
domain = range(len(all_scores[-1]), 9, -25)

for m in tqdm(domain):
	m_scatters = [] # all means for this m for all hours

	for hour_scores in all_scores:
		hour_m_scatters = []

		for i in range(100):
			subsample = numpy.random.choice(hour_scores, size=(m,), replace=False)

			hour_m_scatters.append(subsample.mean()) # accumulate bunch of mean scores

		m_scatters.append(hour_m_scatters) # each hour's means for this m go in a list, split by hour

	scatters.append(m_scatters) # all hour-average-samples, split by hour, go in master scatters



fig, ax = pyplot.subplots()

# I want average score for each sample size here. I'm choosing to average not just
# over samples, but over time.
means = numpy.array([numpy.mean(numpy.array(m)) for m in scatters])
pyplot.plot(domain, means)

# standard deviation is a little trickier, because I don't want to include notion of
# standard deviation over time, just within particular hours, so I really need the
# mean of standard devations for each hour at each m.
stddevs = numpy.array([numpy.mean([numpy.std(h) for h in m ]) for m in scatters])
pyplot.fill_between(domain, means-stddevs, means+stddevs, color='gray', alpha=0.2)

ax.set_xlim(max(domain), min(domain))
pyplot.title('subsample noise for '+COUNTY+', '+STATE)
pyplot.xlabel('subsample size m')
pyplot.ylabel('score')

pyplot.show()
"""



