# N : number of vertices; vertices in {0,1,...(N-1)}
# E : list of edges; edge = unordered pair of vertices
# Return value : minimum vertex cover as list
def findMinVertexCover(N, E):
    import mip
    model = mip.Model("VertexCover")
    model.verbose = 0 # turn off Cbc console logs
    x = [model.add_var(var_type=mip.BINARY,\
        name=f"x_{i}") for i in range(N)]
    model.objective = mip.minimize(mip.xsum(x))
    for e in E:
        model += (x[e[0]] + x[e[1]] >= 1)
    model.optimize()
    if model.status == mip.OptimizationStatus.OPTIMAL:
        return [i for i in range(N) if x[i].x >= 0.9]
    return []
