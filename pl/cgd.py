import numpy as np
from math import sqrt
def conjugate_gradient(A, b, x, eps = 1.e-6):
    r    = b - A @ x # residue
    d    = r # direction
    rTr   = r.T @ r
    for i in range(A.shape[0]):
        Ad       = A @ d
        alpha    = rTr / (d.T @ Ad)
        x        = x + alpha * d
        r        = r - alpha * Ad
        rTr_prev = rTr
        if sqrt(r.T @ r) <= eps: return x
        rTr = r.T @ r
        beta   = rTr / rTr_prev
        d      = r + beta * d
    return x

#A=np.array([[1, -1], [-1, 2]])
#b=np.array([1, 0])
#print(conjugate_gradient(A, b, np.array([0.1, 0.1])))

N = 5000
a = np.random.rand(N, N)
A = np.dot(a, a.T)
b = np.random.rand(N,1)
import time
print('solving')
t = time.time()
sol = conjugate_gradient(A, b, np.random.rand(N, 1))
print('runtime :', time.time() - t)
