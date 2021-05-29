

# https://math.stackexchange.com/questions/4012751/how-to-find-standard-deviation-error-bound-from-variance-error-bound/4012779#4012779
# cookierobotics.com/007 

import numpy
from scipy import linalg
from matplotlib import pyplot

def get_ellipse_outline(xc: float, yc: float, P: numpy.ndarray):
	"""Get a list of xy coordinates that form the outline of an ellipse centered at (xc, yc) and with with a covariance
	matrix P

	:param xc: the x-coordinate of the ellipse's center
	:param yc: the y-coordinate of the ellipse's center
	:param P: the 2D rotation matrix for the ellipse direction
	:return: the array of x-y coordinates that make up the ellipse's outline
	"""
	t = numpy.linspace(-numpy.pi, numpy.pi, 50)
	xy = numpy.vstack((numpy.cos(t), numpy.sin(t)))

	return numpy.dot(P, xy) + numpy.array([[xc], [yc]])

M2 = numpy.array([[1,2],[2,4]])
l, v = numpy.linalg.eig(M2)

print(v[:,0].dot(v[:,1]))

M = v * numpy.sqrt(l)

ellipse1 = get_ellipse_outline(0,0,M)
ellipse2 = get_ellipse_outline(0,0,M2)
pyplot.plot(ellipse1[0], ellipse1[1], ':b')
pyplot.plot(ellipse2[0], ellipse2[1], ':r')



"""
#A = the matrix such that AA.T = B
A = numpy.array([[ 0.76641471, -0.17036945, -0.00558343],
				 [-1.94279268, -0.06720926,  0.0141535 ],
				 [-0.16535958,  0.        , -0.19216628]])
B = numpy.array([[ 0.61644844, -1.47761351, -0.12566107],
				 [-1.47761351,  3.77916079,  0.31853956],
				 [-0.12566107,  0.31853956,  0.06427167]])

B_l, B_v = numpy.linalg.eig(B)
L = B_v * numpy.sqrt(B_l)

print(A)
print(L)

assert numpy.allclose(numpy.dot(L, L.T), B)

ellipseA = get_ellipse_outline(0,0,A[:2,:2])
ellipseB = get_ellipse_outline(0,0,B[:2,:2])
ellipseL = get_ellipse_outline(0,0,L[:2,:2])

pyplot.plot(ellipseA[0], ellipseA[1], ':b')
pyplot.plot(ellipseB[0], ellipseB[1], ':r')
pyplot.plot(ellipseL[0], ellipseL[1], ':g')
"""

pyplot.axis('equal')
pyplot.show()


