# N : number of vertices; vertices in {0,1,...(N-1)}
# E : list of edges; edge = unordered pair of vertices
# Return value : minimum vertex cover as list
def findMatching(N, E):
    import mip
    model = mip.Model("Matching", solver_name='CBC')
    model.verbose = 0 # turn off Cbc console logs
    x = {e:model.add_var(var_type=mip.BINARY,\
        name=f"x_{e[0]}_{e[1]}") for e in E}
    model.objective = mip.maximize(mip.xsum(list(x.values())))
    for i in range(len(E)):
        e1 = E[i]
        for j in range(i + 1, len(E)):
            e2 = E[j]
            if (e1[0] == e2[0] or e1[1] == e2[0] or e1[0] == e2[1] or e1[1] == e2[1]):
                model += (x[e1] + x[e2] <= 1)
    model.optimize()
    model.write('1.lp')
    if model.status == mip.OptimizationStatus.OPTIMAL:
        return [i for i in E if x[i].x >= 0.9]
    return []
print(findMatching(4,[(0,1),(0,2),(1,2),(1,3)]))
print(findMatching(6,[(0,1),(1,2),(1,3),(1,4),(2,3),(2,5),(4,5)]))
print(findMatching(6,[(0,1),(1,2),(2,3),(0,4),(1,4),(2,4),(2,5),(4,5)]))
print(findMatching(6,[(0,1),(0,2),(1,2),(1,3),(2,4),(3,4),(3,5)]))
