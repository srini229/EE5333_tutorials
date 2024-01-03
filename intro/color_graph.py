# N is num. vertices; vertices are indexed {0,1,...,(N-1)}
# E is a list of edges; each edge is an unordered pair of vertices
# C is list of color costs : C[i] is the cost of color i
#                            color ranges from [0,1,...,len(C)-1]
# Return value : list of colors if colorable empty list otherwise;
#                ith color in the list is for the ith vertex
def colorGraph(N, E, C):

