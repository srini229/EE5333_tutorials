# N : number of vertices; vertices in {0,1,...(N-1)}
# S : list of tuples
# Return value : set cover as a list of tuples
def findSetCover(N, S):
    import mip
    model = mip.Model("SetCover")
    model.verbose = 0 # turn off Cbc console logs
    x = [model.add_var(var_type=mip.BINARY,\
        name=f"x_{s}") for s in range(len(S))]
    model.objective = mip.minimize(mip.xsum(x))
    occ = [[] for _ in range(N)]
    for i in range(len(S)):
      for j in S[i]: # store the set indices to which i belongs
        occ[j].append(i)
    for xi in occ:
      model += mip.xsum(x[i] for i in xi) >= 1
    model.optimize()
    if model.status == mip.OptimizationStatus.OPTIMAL:
        return [S[i] for i in range(len(S)) if x[i].x >= 0.9]
    return []
