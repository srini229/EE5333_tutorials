N = 8
E = [(0,1), (0,4), (0,5), (1,4), (1,5), (4,5), (2,3), (2,6), (2,7), (3,6), (3,7), (6,7), (2,5)]
from bipartition import bipartition
print(bipartition(N, E))
from partition import KLPart
print(KLPart(N, E))
