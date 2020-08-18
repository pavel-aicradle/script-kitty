
import os
import numpy
from scipy.optimize import linear_sum_assignment
from matplotlib import pyplot, patches, lines


def areaThresh(line):
	line = list(float(x) for x in line.split())
	class_ = line[0]
	left, top, right, bottom = line[-4:]
	
	A = (bottom - top) * (right - left)
	if A < 0: print("area problem")
	#if class_ == 0 and A < 400: return False
	#if class_ == 2 and A < 100: return False

	return True

def plotRects(f, row_ind, col_ind):

	_, axes = pyplot.subplots(1)

	max_width = 0
	max_height = 0

	i = 0
	for line1 in open('detections/' + f):
		if not areaThresh(line1): continue

		class1, conf1, top1, left1, bottom1, right1 = (float(x) for x in line1.split())
		max_height = max(max_height, bottom1)
		max_width = max(max_width, right1)

		c = 'g' if i in row_ind else 'r'

		axes.add_patch(patches.Rectangle((left1, top1), right1-left1, bottom1-top1,
			linewidth=1, edgecolor=c, facecolor='none'))

		i += 1

	j = 0
	for line2 in open('groundtruths/' + f):
		if not areaThresh(line2): continue

		class2, top2, left2, bottom2, right2 = (float(x) for x in line2.split())
		max_height = max(max_height, bottom2)
		max_width = max(max_width, right2)

		c = 'b' if j in col_ind else 'y'

		axes.add_patch(patches.Rectangle((left2, top2), right2-left2, bottom2-top2,
			linewidth=1, edgecolor=c, facecolor='none'))

		j += 1

	pyplot.axis([0, max_width+5, 0, max_height+5])
	
	axes.legend([lines.Line2D([0], [0], color='g', lw=1), lines.Line2D([0], [0], color='r', lw=1),
				lines.Line2D([0], [0], color='b', lw=1), lines.Line2D([0], [0], color='y', lw=1)],
				['matched detection', 'unmatched detection', 'matched groundtruth', 'unmatched groundtruth'])
	pyplot.gca().invert_yaxis()
	pyplot.title('Assignment Results')
	pyplot.show()


## Intersection over union
def IoU(line1, line2):
	# detections and ground truths come out in format: class_index confidence left top right bottom
	class1, conf1, left1, top1, right1, bottom1 = (float(x) for x in line1.split())
	class2, left2, top2, right2, bottom2 = (float(x) for x in line2.split())

	if top1 >= bottom1 or left1 >= right1: print("problem1")
	if top2 >= bottom2 or left2 >= right2: print("problem2")

	if class1 != class2:
		return 0 # no utility

	# 0,0 -------->
	#  |
	#  |   image top will be < image bottom, and image left < image right
	#  v
	A1 = (bottom1 - top1) * (right1 - left1)
	A2 = (bottom2 - top2) * (right2 - left2)
	if A1 <= 0 or A2 <= 0: print("area problem")

	intersection_height = min(bottom1, bottom2) - max(top1, top2)
	intersection_width = min(right1, right2) - max(left1, left2)
	if intersection_height <=0 or intersection_width <=0:
		return 0

	I = intersection_height * intersection_width

	U = A1 + A2 - I

	if I/U > 1: print("IoU problem")
	return I/U


aggomerated_IoUs = []

for k, f in enumerate(os.listdir('groundtruths')):
	if f[-4:] != '.txt': continue

	# I need to match detections to the optimal groundtruths, which can be formulated as bipartite matching,
	# which can be solved with the Hungarian algorithm, an implementation of which comes in scipy.
	#
	# "C, where each C[i,j] is the cost of matching vertex i of the first partite set (a “worker”) and
	# vertex j of the second set (a “job”)."

	# start this off as a list, because I don't know a priori how many entries are in these files
	# also start off as U for utility instead of C for cost, because higher IoU is better
	print(f)
	U = []
	i = 0
	for line1 in open('detections/' + f):
		if areaThresh(line1):
			U.append([])
			for j, line2 in enumerate(open('groundtruths/' + f)):
				if areaThresh(line2):
					U[i].append(IoU(line1, line2))
			i += 1
	
	# convert to a numpy array for ease
	U = numpy.array(U)
	if U.size == 0: continue
	print("U.shape", U.shape)

	# The Hungarian algorithm is for minimizing cost, but here I want to maximize some utility (overlap).
	# The Hungarian algorithm is designed for a nonnegative cost matrix, so I have to follow this strategy:
	# https://www.youtube.com/watch?v=Zk2xI-GzJIs Subtract all entries of the utility matrix from the max entry,
	# so cost of the highest utility entry is 0, and it goes up from there. Notice my -1s now become +1s when
	# they're subtracted, making the cost of my dummy row/col entries higher.
	C = numpy.max(U) - U

	row_ind, col_ind = linear_sum_assignment(C)

	for l in range(U.shape[0]):
		if l < len(row_ind):
			#print(U[row_ind[l], col_ind[l]]) # these are in fact the positive entries
			aggomerated_IoUs.append(U[row_ind[l], col_ind[l]])
		else: aggomerated_IoUs.append(0)

	#if k == 2:
	#	plotRects(f, row_ind, col_ind)
	#	break

pyplot.hist(aggomerated_IoUs, bins=30)
pyplot.title('histogram of IoU')
pyplot.xlabel('detection IoU')
pyplot.ylabel('number of detections falling in buckets')
pyplot.show()





