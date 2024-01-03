#include <vector>
#include "coin/CbcModel.hpp"
#include "coin/OsiClpSolverInterface.hpp"
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
  OsiClpSolverInterface solver;
  std::vector<double> objective(N, 1.), lb(N, 0.), ub(N, 1.);
  std::vector<int> rowindofcol[N], starts, indices;
  std::vector<double> constrvalues[N], values;

  solver.messageHandler()->setLogLevel(0);

  // add edge constraints; rhs is a constant 1 for each constraint
  for (int i = 0; i < len(E); ++i) {
    py::tuple e = py::extract<py::tuple>(E[i]);
    rowindofcol[(int)py::extract<int>(e[0])].push_back(i);
    rowindofcol[(int)py::extract<int>(e[1])].push_back(i);
    constrvalues[(int)py::extract<int>(e[0])].push_back(1.);
    constrvalues[(int)py::extract<int>(e[1])].push_back(1.);
  }

  // transform constraint matrix to COIN starts/indices format
  starts.push_back(0);
  for (int i = 0; i < N; ++i) {
    starts.push_back(starts.back() + rowindofcol[i].size());
    indices.insert(indices.end(), rowindofcol[i].begin(), rowindofcol[i].end());
    values.insert(values.end(), constrvalues[i].begin(), constrvalues[i].end());
  }
  // all constraints are >=; hence lb is 1. and ub is \infty
  std::vector<double> rhslb(len(E), 1.), rhsub(len(E), solver.getInfinity());

  solver.loadProblem(N, len(E), starts.data(), indices.data(), values.data(), lb.data(), ub.data(), objective.data(), rhslb.data(), rhsub.data());
  // make all variables as integers
  for (int i = 0; i < N; ++i) {
    solver.setInteger(i);
  }
  CbcModel model(solver);
  //for(int i = 0; i < N; ++i) {
  //  std::string nm = "x_" + std::to_string(i);
  //  solver.setColName(i, nm.c_str());
  //}
  //solver.writeLp("mvc");
  model.setLogLevel(0);
  const char* argv[] = {"", "-log", "0", "-solve"};
  CbcMain(4, argv, model);
  py::list vertexCover;
  if (model.status() == 0) {
    double* var = model.bestSolution();
    for (int i = 0; i < model.getNumCols(); ++i) {
      if (var[i] >= 0.9) vertexCover.append(i);
    }
  }
  return vertexCover;
}

// expose min_vertex_cover as module with the function findMinVertexCover to Python
BOOST_PYTHON_MODULE(min_vertex_cover)
{
  py::def("findMinVertexCover", findMinVertexCover);
};
