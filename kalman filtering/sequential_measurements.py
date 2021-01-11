
import numpy
from scipy.linalg import block_diag

xprime = numpy.array([0,0,0])
Pprime = numpy.array([[0.1, 0.05, 0], [0.05, 0.1, 0.03], [0, 0.03, 0.2]])

H1 = numpy.array([[1,2,1],[3,2,0]])
H2 = numpy.array([[3,1,-1],[-5,0,2]])

yhat1 = numpy.array([540, 960])
yhat2 = numpy.array([560, 1000])

R1 = numpy.array([[0.5,0],[0,0.3]])
R2 = numpy.array([[0.4,0],[0,0.6]])

# simultaneous path

H = numpy.concatenate((H1, H2))
yhat = numpy.concatenate((yhat1, yhat2))
R = block_diag(R1, R2)

S = H.dot(Pprime).dot(H.T) + R
G = Pprime.dot(H.T).dot(numpy.linalg.inv(S))

x_simultaneous = xprime + G.dot(yhat - H.dot(xprime))
P_simultaneous = (numpy.eye(3) - G.dot(H)).dot(Pprime)

print(x_simultaneous)
print(P_simultaneous)

# sequential path

S1 = H1.dot(Pprime).dot(H1.T) + R1
G1 = Pprime.dot(H1.T).dot(numpy.linalg.inv(S1))

x1 = xprime + G1.dot(yhat1 - H1.dot(xprime))
P1 = (numpy.eye(3) - G1.dot(H1)).dot(Pprime)

S2 = H2.dot(P1).dot(H2.T) + R2
G2 = P1.dot(H2.T).dot(numpy.linalg.inv(S2))

x2 = x1 + G2.dot(yhat2 - H2.dot(x1))
P2 = (numpy.eye(3) - G2.dot(H2)).dot(P1)

print(x2)
print(P2)

print(numpy.allclose(x_simultaneous, x2))
print(numpy.allclose(P_simultaneous, P2))
