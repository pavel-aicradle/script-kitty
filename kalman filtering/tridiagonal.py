
import numpy
from numpy.linalg import inv

def symmetric_block_tridiagonal_solve(D, C, b):
	Q = [None for i in range(len(D))]
	w = [None for i in range(len(D))]
	U = [None for i in range(len(D)-1)]
	x = [None for i in range(len(D))]

	Q[0] = D[0] # Q_0
	w[0] = inv(Q[0]).dot(b[0])

	for i in range(1, len(D)):
		U[i-1] = inv(Q[i-1]).dot(C[i-1].T)
		Q[i] = D[i] - C[i-1].dot(U[i-1])
		w[i] = inv(Q[i]).dot(b[i] - C[i-1].dot(w[i-1]))

	print("Q", Q)
	print("U", U)
	print("w", w)

	x[-1] = w[-1]

	for i in range(len(D)-2, -1, -1):
		x[i] = w[i] - U[i].dot(x[i+1])

	return x


def make_blocks(A, F, y):
	# A is MxN and F is NxN
	N = F.shape[0]
	M = A.shape[0]

	rows = len(y)//M

	if rows % 2 == 0: # half step
		height = rows//2*N + rows//2*M
	else:
		height = rows//2*N + (rows//2 + 1)*M
	width = (rows//2 + 1)*N

	AA = numpy.zeros((height, width))

	h = 0
	w = 0
	for i in range(rows):
		if i % 2 == 0: # A block row
			AA[h:h+M, w:w+N] = A
			h += M
		else: # F and -I block row
			AA[h:h+N, w:w+N] = F
			AA[h:h+N, w+N:w+2*N] = -numpy.eye(N)
			h += N
			w += N

	print(AA)
	AAAA = AA.T.dot(AA)
	print(AAAA) # my code is starting to look surprised

	D = [AAAA[:N,:N]]
	C = []
	for i in range(1, AAAA.shape[0]//N):
		D.append(AAAA[i*N:(i+1)*N, i*N:(i+1)*N])
		C.append(AAAA[i*N:(i+1)*N, (i-1)*N:i*N])

	bb = AA.T.dot(y)
	print(bb)
	b = [bb[i*N:(i+1)*N] for i in range(AAAA.shape[0]//N)]

	return D, C, b


A = numpy.array([[2, 0], [0, 1]])
F = numpy.array([[1, 0.5], [0, 1]])
y = numpy.array([1, 1, 0, 0, 2, 2, 0, 0, 3, 3, 0, 0])

D, C, b = make_blocks(A, F, y)

print("----------")
print(D)
print(C)
print(b)
print("----------")

x = symmetric_block_tridiagonal_solve(D, C, b)

print("----------")
print(x)


