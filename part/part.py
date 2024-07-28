class Vertex:
  def __init__(self, name, area, nbrs):
    self._name = name
    self._area = area
    self._nbrs = nbrs
  def __repr__(self):
    return self._name + f" ({round(self._area,2)})"

def loadNetlist(leffile = None, deffile = None):
  import LEFDEFParser as LDP
  l = LDP.LEFReader()
  areaLookup = dict()
  if leffile:
    l.readLEF(leffile)
    areaLookup = {m.name():(m.xdim()*m.ydim()*1.e-6) for m in l.macros()}
  vertices = dict()
  edges = dict()
  if deffile:
    d = LDP.DEFReader()
    d.readDEF(deffile)
    vertices = {c.name() : Vertex(c.name(), areaLookup.get(c.macro(), None), list()) for c in d.components()}
    edges = {n.name():[vertices[p[0]] for p in n.pins() if p[0] != 'PIN'] for n in d.nets()}
  delE = list()
  for e in edges:
    if len(edges[e]) <= 1:
      delE.append(e)
  for e in delE: del edges[e]
  return vertices, edges

"""## $k$-way hypergraph partitioning using ILP
+ Hypergraph $H(V,E)$
+ $x_{v,i}$ is the indicator variable for $v$ being in partition $V_i$
+ $x_{e,i}$ is the indicator variable for $e\in E$ being contained in $V_i$

+ Objective: $\max\limits_{x_{e,i}} \sum\limits_{e\in E}\sum\limits_{i=1}^k x_{e,i}$
+ Subject to constraints:
<ul>
$\begin{align}
x_{v,i} &\in \{0, 1\}, &\forall v \in V, \forall i \in \{1,2,\ldots, k\}\\
x_{e,i} &\in \{0, 1\}, &\forall e \in E, \forall i \in \{1,2,\ldots, k\}\\
\sum\limits_{i=1}^k x_{v,i} &=1 , &\forall v \in V\\
\sum_{v\in V} area(v)\cdot x_{v,i}&\leq Area_{max} &\forall v \in V\\
\sum_{v\in V} area(v)\cdot x_{v,i}&\geq Area_{min} &\forall v \in V\\
x_{e,i} &\leq x_{v,i}, &\forall e \in E, \forall v~\text{connected by}~e\\
\end{align}$
</ul>
"""

def partition(V, E, k, Amin, Amax):
  import mip
  model = mip.Model(f"{k}-way partition")
  x = {u:[model.add_var(f"x_{u}_{i}", var_type = mip.BINARY) for i in range(k)] for u in V}
  x_e = {e:[model.add_var(f"x_{e}_{i}", var_type = mip.BINARY) for i in range(k)] for e in E}
  model.verbose = 0
  model.objective = mip.maximize(mip.xsum(x_e[e][i] for e in E for i in range(k)))

  for u in V:
    model += mip.xsum(x[u]) == 1

  for i in range(k):
    model += mip.xsum(V[u]._area*x[u][i] for u in V) >= Amin
    model += mip.xsum(V[u]._area*x[u][i] for u in V) <= Amax

  for e in E:
    for i in range(k):
      for v in E[e]:
        model += x_e[e][i] <= x[v._name][i]

  model.write(f"partition{k}.lp")
  model.optimize()
  sol = [list() for i in range(k)]

  if model.status == mip.OptimizationStatus.OPTIMAL:
    for u in V:
      for i in range(k):
        if round(x[u][i].x) == 1: sol[i].append(V[u])

    return (sol, len(E)- model.objective.x)
  return None

import time
k=2
V,E = loadNetlist('Nangate.lef', 'example.def')
Atotal = sum(V[u]._area for u in V)
maxCellArea = max(V[u]._area for u in V)
print(Atotal, round(maxCellArea,2))
t = time.time()
sol, numcuts = partition(V, E, k, Atotal/k - maxCellArea/6, Atotal/k + maxCellArea/6)
print("runtime :", time.time() - t)
print("number of cuts :", round(numcuts))
for part in sol:
  print(part, sum([x._area for x in part]))

!cat example.def
!cat partition2.lp

import time
k=2
V,E = loadNetlist('sample.lef', 'sample.def')
Atotal = sum(V[u]._area for u in V)
maxCellArea = max(V[u]._area for u in V)
print(Atotal, round(maxCellArea,2))
t = time.time()
sol, numcuts = partition(V, E, k, Atotal/k - maxCellArea/6, Atotal/k + maxCellArea/6)
print("runtime :", time.time() - t)
print("number of cuts :", round(numcuts))
for part in sol:
  print(part, sum([x._area for x in part]))
