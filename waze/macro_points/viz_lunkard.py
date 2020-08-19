
import json
from matplotlib import pyplot

points = json.load(open('lunkard.json', 'r'))
print(len(points))

xx, yy = zip(*points)
#print(xx)
#print(yy)



pyplot.scatter(xx, yy, marker='.', linewidths=0.)
pyplot.show()