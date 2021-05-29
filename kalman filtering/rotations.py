
import numpy
from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D


def recover_angles(R):
	"""based on https://www.gregslabaugh.net/publications/euler.pdf
	
	psi = about x axis
	theta = about y axis
	phi = about z axis

	:param R: a 3D rotation matrix
	"""
	if R[2,0] != 1 and R[2,0] != -1:

		theta1 = -numpy.arcsin(R[2,0])
		#theta2 = numpy.pi - theta1
		c1 = numpy.cos(theta1)
		#c2 = numpy.cos(theta2)
		psi1 = numpy.arctan2(R[2,1]/c1, R[2,2]/c1)
		#psi2 = numpy.arctan2(R[2,1]/c2, R[2,2]/c2)
		phi1 = numpy.arctan2(R[1,0]/c1, R[0,0]/c1)
		#phi2 = numpy.arctan2(R[1,0]/c2, R[0,0]/c2)

		return psi1, theta1, phi1 #(psi2, theta2, phi2)

	else:
		phi = 0
		if  R[2,0] == -1:
			theta = numpy.pi/2
			psi = phi + numpy.arctan2(R[0,1],R[0,2])
		else:
			theta = -numpy.pi/2
			psi = -phi + numpy.arctan2(-R[0,1],-R[0,2])

		return psi, theta, phi

def R(roll, pitch, yaw):
	R_x = R_(roll, 'x')
	R_y = R_(pitch, 'y')
	R_z = R_(yaw, 'z')

	return R_z.dot(R_y).dot(R_x)

def R_(angle: float, axis: str) -> numpy.ndarray:
	"""Direct Cosine Matrix (DCM) to rotate single axis

	:param angle: angle being rotated (rad)
	:param axis: 1, 2, or 3 axis for rotation
	:return: DCM for rotation
	"""
	c = numpy.cos(angle)
	s = numpy.sin(angle)

	if axis == 'x':
		return numpy.array([[1, 0, 0], [0, c, -s], [0, s, c]])
	elif axis == 'y':
		return numpy.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
	elif axis == 'z':
		return numpy.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
	else:
		raise Exception('axis out of bounds')


D2R = numpy.pi/180
R2D = 180/numpy.pi

# Now say we're a camera in flipped UE4 frame. We're not rolled at all. We're facing southeast. And we're pitched
# downward 20 degrees. Our rotation can be described with

# phi keeps its sign
# theta and psi are negated

R_z = R_(-135*D2R, 'z')
R_y = R_(20*D2R, 'y')

RR = R_z.dot(R_y)

print(RR)

angles = recover_angles(RR)
for a in angles: print(a*R2D)

fig = pyplot.figure()
ax = fig.gca(projection='3d')
ax.plot([0,5],[0,0],[0,0],c='k')
ax.plot([0,0],[0,5],[0,0],c='k')
ax.plot([0,0],[0,0],[0,5],c='k')

ax.plot([0,RR[0,0]],[0,RR[1,0]],[0,RR[2,0]],c='r')
ax.plot([0,RR[0,1]],[0,RR[1,1]],[0,RR[2,1]],c='g')
ax.plot([0,RR[0,2]],[0,RR[1,2]],[0,RR[2,2]],c='b')

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
pyplot.show()







