class Vertex:
    def __init__(self, i, part):
        self._id = i
        self._part = part
        self._nbrs = []
        self._ea = 0
        self._eb = 0
        self._d  = 0

    def __str__(self):
        return '(' + str(self._id) + ',' + str(self._part) + ',' + str(self._ea) + ',' + str(self._eb) + ',' + str(self._d) + ',' + str([i._id for i in self._nbrs]) + ')'

    def __repr__(self):
        return str(self)

def reset(V, A, B):
    for j in range(2):
        part = A if (0 == j) else B
        for i in part:
            V[i]._part = j
            V[i]._ea = 0
            V[i]._eb = 0
            V[i]._d  = 0
    for v in V:
        assert(v._part == 0 or v._part == 1)
        for n in v._nbrs:
            if n._part == 0:
                v._ea += 1
            else:
                v._eb += 1
    for v in V:
        v._d = (v._ea - v._eb) if (v._part == 1) else (v._eb - v._ea)

def findMaxGain(V, Ap, Bp, E):
    (amax, bmax, gmax) = (-1, -1, -2 * len(E) - 1)
    for a in Ap:
        for b in Bp:
            g = V[a]._d + V[b]._d - (2 if (min(a,b), max(a,b)) in E else 0)
            if gmax < g:
                amax = a
                bmax = b
                gmax = g
    assert(amax >= 0 and bmax >= 0)
    return (amax, bmax, gmax)

def updateED(V, a, b):
    V[a]._part = 1
    V[b]._part = 0
    for i in [a,b]:
        for n in V[i]._nbrs:
            if i == a:
                n._ea -= 1
                n._eb += 1
            else:
                n._ea += 1
                n._eb -= 1
            n._d = (n._ea - n._eb) if (n._part == 1) else (n._eb - n._ea)

def KLPart(N, E):
    if N%2: N+= 1 # make N even if its odd by adding a single no-neighbour vertex
    V = [Vertex(i, -1) for i in range(N)]
    for e in E:
        if e[0] > e[1]: e = (e[1], e[0])
        else: e = (e[0], e[1])
    E = set(E)
    for e in E:
        V[e[0]]._nbrs.append(V[e[1]])
        V[e[1]]._nbrs.append(V[e[0]])
    import random
    Vc = V[:]
    random.shuffle(Vc)
    A = {Vc[i]._id for i in range(N//2)}
    B = {Vc[i]._id for i in range(N//2, N)}

    maxGain = 1
    it = 0
    prevGain = 1
    while maxGain >= 0:
        it += 1
        Ap = A.copy()
        Bp = B.copy()
        reset(V, A, B)
        G = []
        S = []
        for p in range(N//2):
            (a, b, g) = findMaxGain(V, Ap, Bp, E)
            updateED(V, a, b)
            Ap.remove(a)
            Bp.remove(b)
            G.append(g)
            S.append((a, b))
        for i in range(1, len(G)):
            G[i] += G[i-1]
        prevGain = maxGain
        maxGain = max(G)
        maxIndex = G.index(maxGain)
        if maxGain > 0:
            for (a, b) in S[0:maxIndex + 1]:
                A.remove(a)
                B.remove(b)
                A.add(b)
                B.add(a)
        if prevGain == 0 and maxGain == 0:
            break

    cut = 0
    for a in A:
        for b in B:
            if (min(a, b), max(a,b)) in E:
                cut += 1
    return (A, B, cut)
