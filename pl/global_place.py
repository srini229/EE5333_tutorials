import LEFDEFParser
import numpy as np
from math import sqrt
import time

# Solve linear system of equations using conjugate gradient method
# Use RMS of residue within a margin of eps to stop
def solveUsingCG(A, b, eps = 1e-4):
    x    = np.zeros(b.shape)
    r    = b # residue
    d    = r # direction
    rTr   = r.T @ r
    for i in range(A.shape[0]):
        Ad       = A @ d
        alpha    = rTr / (d.T @ Ad)
        x        = x + alpha * d
        r        = r - alpha * Ad
        rTr_prev = rTr
        rTr = r.T @ r
        if sqrt(rTr) <= eps: return x
        beta   = rTr / rTr_prev
        d      = r + beta * d
    return x

# Class to hold neighbours and pins connected to each standard cell
class Vertex:
    def __init__(self, c):
        self._comp = c
        self._nbrs = []
        self._pinNbrs = []
        self._bin = None
        self._index = -1
        
    def __repr__(self):
        return self._comp.name() + f' {self._nbrs} {self._pinNbrs}'

# Frame A, b_x and b_y matrices and solve for x and y coordinates of each cell
def solve(Vertices):
    for i in range(len(Vertices)):
        Vertices[i]._comp.setLocation(0, 0)
    A = np.zeros((len(Vertices), len(Vertices)))
    bx = np.zeros(len(Vertices))
    by = np.zeros(len(Vertices))
    for i in range(len(Vertices)):
        A[i][i] += (len(Vertices[i]._nbrs) + len(Vertices[i]._pinNbrs))*1.
        for nbr in Vertices[i]._nbrs:
            A[Vertices[i]._index][nbr._index] -= 1
        for p in Vertices[i]._pinNbrs:
            bx[Vertices[i]._index] += p.x
            by[Vertices[i]._index] += p.y
    assert(np.all(A.T == A))
    t = time.time()
    solx = solveUsingCG(A, bx)
    soly = solveUsingCG(A, by)
    print('runtime :', time.time() - t)
    for i in range(len(Vertices)):
        Vertices[i]._comp.setLocation(int(solx[i]), int(soly[i]))

# Bin class that holds the vertices belonging to a bin and virtual pins
class Bin:
    def __init__(self, index, bb):
        self._index = index
        self._vertices = []
        self._bbox = bb
        hw = (bb[1][0] - bb[0][0])/2.
        hh = (bb[1][1] - bb[0][1])/2.
        # create virtual pins on the boundary of each bin; one each for the 8 directions 
        self._vpins = [LEFDEFParser.Point(int(bb[0][0] + hw), int(bb[0][1])),      #0 South pin
                      LEFDEFParser.Point(int(bb[0][0] + hw), int(bb[1][1])),      #1 North pin
                      LEFDEFParser.Point(int(bb[1][0]),      int(bb[0][1])),      #2 South East pin
                      LEFDEFParser.Point(int(bb[0][0]),      int(bb[0][1])),      #3 South West pin
                      LEFDEFParser.Point(int(bb[0][0]),      int(bb[0][1] + hh)), #4 East pin
                      LEFDEFParser.Point(int(bb[1][0]),      int(bb[0][1] + hh)), #5 West pin
                      LEFDEFParser.Point(int(bb[1][0]),      int(bb[1][1])),      #6 North East pin
                      LEFDEFParser.Point(int(bb[0][0]),      int(bb[1][1]))       #7 North West pin
                      ]

    def build(self):
        for i in range(len(self._vertices)):
            self._vertices[i]._index = i
            totalNbrs = len(self._vertices[i]._pinNbrs) + len(self._vertices[i]._nbrs)
            pnbrs = list()
            for pi in range(len(self._vertices[i]._pinNbrs)):
                p = self._vertices[i]._pinNbrs[pi]
                if p.x >= self._bbox[0][0] and p.x <= self._bbox[1][0] and p.y >= self._bbox[0][1] and p.y <= self._bbox[1][1]:
                    pnbrs.append(p)
                else:
                    if p.x < self._bbox[0][0]:
                        if p.y < self._bbox[0][1]: # south west
                            pnbrs.append(self._vpins[3])
                        elif p.y > self._bbox[0][1]: # north west
                            pnbrs.append(self._vpins[7])
                        else: #west
                            pnbrs.append(self._vpins[5])
                    elif p.x > self._bbox[1][0]:
                        if p.y < self._bbox[0][1]: # south east
                            pnbrs.append(self._vpins[2])
                        elif p.y > self._bbox[0][1]: # north east
                            pnbrs.append(self._vpins[6])
                        else: #east
                            pnbrs.append(self._vpins[4])
                    elif p.y < self._bbox[0][1]:#south
                        pnbrs.append(self._vpins[0])
                    elif p.y > self._bbox[1][1]:#north
                        pnbrs.append(self._vpins[1])
            self._vertices[i]._pinNbrs = pnbrs
            actNbrs = list() # remove neighbours not in this bin and add a connection to the corresponding pin at the boundary
            for nbr in self._vertices[i]._nbrs:
                index = self._index
                nBinIndex = nbr._bin._index
                if nBinIndex != index:
                    if nBinIndex[1] == index[1]: # east or west
                        if nBinIndex[0] < index[0]: #west
                            self._vertices[i]._pinNbrs.append(self._vpins[5])
                        else:
                            self._vertices[i]._pinNbrs.append(self._vpins[4])
                    elif nBinIndex[0] == index[0]: # south or north
                        if nBinIndex[1] < index[1]: #south
                            self._vertices[i]._pinNbrs.append(self._vpins[0])
                        else:
                            self._vertices[i]._pinNbrs.append(self._vpins[1])
                    elif nBinIndex[0] < index[0]: # south west or north west
                        if nBinIndex[1] < index[1]: #south
                            self._vertices[i]._pinNbrs.append(self._vpins[3])
                        else:
                            self._vertices[i]._pinNbrs.append(self._vpins[7])
                    elif nBinIndex[0] > index[0]: # south east or north east
                        if nBinIndex[1] < index[1]: #south
                            self._vertices[i]._pinNbrs.append(self._vpins[2])
                        else:
                            self._vertices[i]._pinNbrs.append(self._vpins[6])
                else:
                    actNbrs.append(nbr)
            self._vertices[i]._nbrs = actNbrs
            assert(totalNbrs == len(self._vertices[i]._pinNbrs) + len(self._vertices[i]._nbrs))
            #self._vertices[i]._pinNbrs = list(set(self._vertices[i]._pinNbrs))
        return

# bins : quadrisection
# create bins from the previous iterations solution
def createBins(Vertices, bbox):
    w = (bbox[1][0] - bbox[0][0])/2.
    h = (bbox[1][1] - bbox[0][1])/2.
    bins = [[None, None], [None, None]]
    for i in range(2):
        for j in range(2):
            bins[i][j] = Bin((i, j), ((bbox[0][0] + i * w, bbox[0][1] + j * h), (bbox[0][0] + (i + 1) * w, bbox[0][1] + (j + 1)*h)))

    Vertices.sort(key=lambda v: v._comp.location().x)
    for xi in range(2):
        if 0 == xi: vec = Vertices[0:int(len(Vertices)/2)]
        else:       vec = Vertices[int(len(Vertices)/2):]
        vec.sort(key=lambda v:v._comp.location().y)
        for yi in range(2):
            if 0 == yi: bins[xi][yi]._vertices = vec[0:int(len(vec)/2)]
            else:       bins[xi][yi]._vertices = vec[int(len(vec)/2):]
            for v in bins[xi][yi]._vertices:
                v._bin = bins[xi][yi]
    for i in range(len(bins)):
        for j in range(len(bins[i])):
            bins[i][j].build()
    return bins

# Iteratively quadrisection and solve
def solveIter(V, bbox, outfile, d, Numiter):
    print(f'solving : level 0')
    solve(V)
    savedSol = [(np.array([v._comp.location().x for v in V]), np.array([v._comp.location().y for v in V]))]
    d.writeDEF(f'{outfile}_iter0.def')
    bins = [createBins(V, bbox)]

    for niter in range(1, Numiter):
        print(f'solving : level {niter}')
        binstmp = []
        for i in range(len(bins)):
            for j in range(len(bins[i])):
                for k in range(len(bins[i][j])):
                    solve(bins[i][j][k]._vertices)
                    binstmp.append(createBins(bins[i][j][k]._vertices, bins[i][j][k]._bbox))
        savedSol.append((np.array([v._comp.location().x for v in V]),np.array([v._comp.location().y for v in V])))
        d.writeDEF(f'{outfile}_iter{niter}.def')
        bins = binstmp
    return savedSol

# load the DEF file and build the connectivity graph using the Vertex class
# Boundary pins have the name PIN followed by the pinName
def place(deffile, outfile, Numiter):
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
    
    bb = ((chip_bbox.ll.x, chip_bbox.ll.y),(chip_bbox.ur.x, chip_bbox.ur.y))
    plot(solveIter(V, bb, outfile, d, Numiter), bb)

def plot(sol, bb):
    import matplotlib.pyplot as plt
    from matplotlib.widgets import Button, Slider

    fig, ax = plt.subplots()
    ax.plot(sol[0][0], sol[0][1], 'o')
    ax.set_xlim([bb[0][0], bb[1][0]])
    ax.set_ylim([bb[0][1], bb[1][1]])
    fig.subplots_adjust(bottom=0.25)

    iterax = fig.add_axes([0.25, 0.1, 0.65, 0.03])
    iter_slider = Slider(ax=iterax, label='Iter', valmin=0, valmax=(len(sol)-1), valstep=1, valinit=0)

    def update(val):
        ax.clear()
        ax.plot(sol[val][0], sol[val][1], 'o')
        ax.set_xlim([bb[0][0], bb[1][0]])
        ax.set_ylim([bb[0][1], bb[1][1]])
        fig.canvas.draw_idle()

    iter_slider.on_changed(update)

    plt.show()

#place('sample/sample.def', 'sample/sample_', 5)
place('sample/dma.def', 'sample/dma_', 4)
