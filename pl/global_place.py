import LEFDEFParser
import numpy as np
from math import sqrt
import time

def conjugate_gradient(A, b, eps = 1e-2):
    x    = np.zeros(b.shape)
    r    = b #- A @ x # residue
    d    = r # direction
    rTr   = r.T @ r
    for i in range(A.shape[0]):
        Ad       = A @ d
        alpha    = rTr / (d.T @ Ad)
        x        = x + alpha * d
        r        = r - alpha * Ad
        rTr_prev = rTr
        rTr = r.T @ r
        #print('err : ', sqrt(rTr))
        if sqrt(rTr) <= eps: return x
        beta   = rTr / rTr_prev
        d      = r + beta * d
    return x

class Vertex:
    def __init__(self, c):
        self._comp = c
        self._nbrs = []
        self._pinNbrs = []
        self._bin = None
        self._index = -1
        
    def __repr__(self):
        return self._comp.name() + f' {self._nbrs} {self._pinNbrs}'
        
def solve(Vertices):
    A = np.zeros((len(Vertices), len(Vertices)))
    bx = np.zeros((len(Vertices), 1))
    by = np.zeros((len(Vertices), 1))
    for i in range(len(Vertices)):
        A[i][i] += (len(Vertices[i]._nbrs) + len(Vertices[i]._pinNbrs))*1.
        for nbr in Vertices[i]._nbrs:
            A[Vertices[i]._index][nbr._index] -= 1
        for p in Vertices[i]._pinNbrs:
            bx[Vertices[i]._index] += p.x
            by[Vertices[i]._index] += p.y
    assert(np.all(A.T == A))
    print('solving')
    t = time.time()
    solx = conjugate_gradient(A, bx)
    soly = conjugate_gradient(A, by)
    print('runtime :', time.time() - t)
    for i in range(len(Vertices)):
        Vertices[i]._comp.setLocation(int(solx[i]), int(soly[i]))
    return (np.median(solx), np.median(soly))


class Bin:
    def __init__(self, index, bb):
        self._index = index
        self._vertices = []
        self._bbox = bb
        hw = (bb[1][0] - bb[0][0])/2.
        hh = (bb[1][1] - bb[0][1])/2.
        self._pins = [LEFDEFParser.Point(int(bb[0][0] + hw), int(bb[0][1])),      #0 South pin
                      LEFDEFParser.Point(int(bb[0][0] + hw), int(bb[1][1])),      #1 North pin
                      LEFDEFParser.Point(int(bb[1][0]),      int(bb[0][0])),      #2 South East pin
                      LEFDEFParser.Point(int(bb[0][0]),      int(bb[0][0])),      #3 South West pin
                      LEFDEFParser.Point(int(bb[0][0]),      int(bb[0][1] + hh)), #4 East pin
                      LEFDEFParser.Point(int(bb[1][0]),      int(bb[0][1] + hh)), #5 West pin
                      LEFDEFParser.Point(int(bb[1][0]),      int(bb[1][1])),      #6 North East pin
                      LEFDEFParser.Point(int(bb[0][0]),      int(bb[1][1]))       #7 North West pin
                      ]

    def rebuild(self):
        for i in range(len(self._vertices)):
            self._vertices[i]._index = i
            actNbrs = list()
            for pi in range(len(self._vertices[i]._pinNbrs)):
                p = self._vertices[i]._pinNbrs[pi]
                if p.x < self._bbox[0][0]:
                    if p.y < self._bbox[0][1]: # south west
                        self._vertices[i]._pinNbrs[pi] = self._pins[3]
                    elif p.y > self._bbox[0][1]: # north west
                        self._vertices[i]._pinNbrs[pi] = self._pins[7]
                    else: #west
                        self._vertices[i]._pinNbrs[pi] = self._pins[5]
                elif p.x > self._bbox[1][0]:
                    if p.y < self._bbox[0][1]: # south east
                        self._vertices[i]._pinNbrs[pi] = self._pins[2]
                    elif p.y > self._bbox[0][1]: # north east
                        self._vertices[i]._pinNbrs[pi] = self._pins[6]
                    else: #east
                        self._vertices[i]._pinNbrs[pi] = self._pins[4]
                elif p.y < self._bbox[0][1]:#south
                    self._vertices[i]._pinNbrs[pi] = self._pins[0]
                elif p.y > self._bbox[1][1]:#north
                    self._vertices[i]._pinNbrs[pi] = self._pins[1]
            for nbr in self._vertices[i]._nbrs:
                if nbr._bin != self._index:
                    index = self._index
                    nBinIndex = nbr._bin._index
                    if nBinIndex[1] == index[1]: # east or west
                        if nBinIndex[0] < index[0]: #west
                            self._vertices[i]._pinNbrs.append(self._pins[5])
                        else:
                            self._vertices[i]._pinNbrs.append(self._pins[4])
                    elif nBinIndex[0] == index[0]: # south or north
                        if nBinIndex[1] < index[1]: #south
                            self._vertices[i]._pinNbrs.append(self._pins[0])
                        else:
                            self._vertices[i]._pinNbrs.append(self._pins[1])
                    elif nBinIndex[0] < index[0]: # south west or north west
                        if nBinIndex[1] < index[1]: #south
                            self._vertices[i]._pinNbrs.append(self._pins[3])
                        else:
                            self._vertices[i]._pinNbrs.append(self._pins[7])
                    elif nBinIndex[0] > index[0]: # south east or north east
                        if nBinIndex[1] < index[1]: #south
                            self._vertices[i]._pinNbrs.append(self._pins[2])
                        else:
                            self._vertices[i]._pinNbrs.append(self._pins[6])
                else:
                    actNbrs.append(nbr)
            self._vertices[i]._nbrs = actNbrs
        return

def createBins(med, Vertices, bbox):
    w = (bbox[1][0] - bbox[0][0])/2.
    h = (bbox[1][1] - bbox[0][1])/2.
    bins = [[None, None], [None, None]]
    for i in range(2):
        for j in range(2):
            bins[i][j] = Bin((i, j), ((bbox[0][0] + i * w, bbox[0][1] + j * h), (bbox[0][0] + (i + 1) * w, bbox[0][1] + (j + 1)*h)))
    for i in range(len(Vertices)):
        xi = 0 if Vertices[i]._comp.location().x <= med[0] else 1
        yi = 0 if Vertices[i]._comp.location().y <= med[1] else 1
        bins[xi][yi]._vertices.append(Vertices[i])
        Vertices[i]._bin = bins[xi][yi]
    for i in range(len(bins)):
        for j in range(len(bins[i])):
            bins[i][j].rebuild()
    return bins

def solveIter(V, bbox, outfile, d):
    med = solve(V)
    d.writeDEF(f'{outfile}_iter0.def')
    bins = createBins(med, V, bbox)
    med = []
    for i in range(len(bins)):
        med.append([])
        for j in range(len(bins[i])):
            med[i].append(solve(bins[i][j]._vertices))
    d.writeDEF(f'{outfile}_iter1.def')
    '''
    for i in range(len(bins)):
        for j in range(len(bins[i])):
            bins2 = createBins(med[i][j], bins[i][j]._vertices, bins[i][j]._bbox)
            for k in range(len(bins2)):
                for l in range(len(bins2)):
                    solve(bins2[i][j]._vertices)
    d.writeDEF('sample/sample_iter2.def')
    '''

def place(deffile, outfile):
    d = LEFDEFParser.DEFReader()
    d.readDEF(deffile)
    chip_bbox = d.bbox()
    V = [Vertex(c) for c in d.components()]
    for i in range(len(V)):
        V[i]._index = i
    Vdict = {V[i]._comp.name():i for i in range(len(V))}
    
    P = [p.origin() for p in d.pins()]
    Pdict = {d.pins()[i].name():P[i] for i in range(len(P))}
    
    for n in d.nets():
        u = list()
        pins = list()
        for p in n.pins():
            if p[0] != 'PIN':
                assert(p[0] in Vdict)
                u.append(Vdict[p[0]])
            else:
                assert(p[1] in Pdict)
                pins.append(Pdict[p[1]])
        for i in range(len(u)):
            for p in pins:
              V[u[i]]._pinNbrs.append(p)
            for j in range(i + 1, len(u)):
                V[u[i]]._nbrs.append(V[u[j]])
                V[u[j]]._nbrs.append(V[u[i]])
    
    solveIter(V, ((chip_bbox.ll.x, chip_bbox.ll.y),(chip_bbox.ur.x, chip_bbox.ur.y)), outfile, d)

place('sample/sample.def', 'sample/sample_')
