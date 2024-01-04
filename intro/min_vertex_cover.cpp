#include "CbcInterface.h"
#include <boost/python.hpp>
#include <boost/python/list.hpp>
#include <boost/python/tuple.hpp>
#include <boost/python/extract.hpp>

namespace py = boost::python;

// N is the number of vertices; vertices are indexed {0,1,...(N-1)}
// E is a list of edges; each edge is an unordered pair of vertices
// Return value : list of vertices in the minimum vertex cover
py::list findMinVertexCover(const int N, const py::list& E)
{
  std::vector<double> objective(N, 1.), lb(N, 0.), ub(N, 1.);
  std::vector<int> rowindofcol[N], starts, indices;
  std::vector<double> constrvalues[N], values;

  CbcIF::SolverInterface solver(N);

  // add edge constraints; rhs is a constant 1 for each constraint
  for (int i = 0; i < len(E); ++i) {
    py::tuple e = py::extract<py::tuple>(E[i]);
    CbcIF::VCVector vc; // vector of (variable, coefficient) pairs
                        // e.g. a0 x[0] + a2 x[2] <= c1 will correspond to
                        // vc.emplace_back(0, a0);
                        // vc.emplace_back(2, a2)
    vc.emplace_back((int)py::extract<int>(e[0]), 1.);
    vc.emplace_back((int)py::extract<int>(e[1]), 1.);
    solver.addConstraint(vc, 1., solver.getInfinity());
  }
  solver.setObjective(objective);

  for (int i = 0; i < N; ++i) {
    solver.setInteger(i);
    solver.setBounds(i, 0., 1.);
  }

  py::list vertexCover;
  auto sol = solver.getSolution();
  solver.writeLp("minvertexcover");
  if (!sol.empty()) {
    for (int i = 0; i < N; ++i) {
      if (sol[i] >= 0.9) vertexCover.append(i);
    }
  }
  return vertexCover;
}

// expose min_vertex_cover as module with the function findMinVertexCover to Python
BOOST_PYTHON_MODULE(min_vertex_cover)
{
  py::def("findMinVertexCover", findMinVertexCover);
};
