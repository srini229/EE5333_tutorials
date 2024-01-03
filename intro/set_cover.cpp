#include <vector>
#include "coin/CbcModel.hpp"
#include "coin/OsiClpSolverInterface.hpp"
#include <boost/python.hpp>
#include <boost/python/list.hpp>
#include <boost/python/tuple.hpp>
#include <boost/python/extract.hpp>
#include <set>

namespace py = boost::python;

// N : number of vertices; vertices in {0,1,...(N-1)}
// S : list of tuples
// Return value : set cover as a list of tuples
py::list findSetCover(const int N, const py::list& S)
{
  OsiClpSolverInterface solver;
  std::vector<double> objective(len(S), 1.), lb(len(S), 0.), ub(len(S), 1.);
  std::vector<int> rowindofcol[len(S)], starts, indices;
  std::vector<double> constrvalues[len(S)], values;

  solver.messageHandler()->setLogLevel(0);

  std::vector<int> occ[N];

  for (int i = 0; i < len(S); ++i) {
    py::tuple Si = py::extract<py::tuple>(S[i]);
    for (int j = 0; j < len(Si); ++j) {
      occ[(int)py::extract<int>(Si[j])].push_back(i);
    }
  }

  for (int i = 0; i < N; ++i) {
    for (auto& j : occ[i]) {
      rowindofcol[j].push_back(i);
      constrvalues[j].push_back(1.);
    }
  }

  // transform constraint matrix to COIN starts/indices format
  starts.push_back(0);
  for (int i = 0; i < len(S); ++i) {
    starts.push_back(starts.back() + rowindofcol[i].size());
    indices.insert(indices.end(), rowindofcol[i].begin(), rowindofcol[i].end());
    values.insert(values.end(), constrvalues[i].begin(), constrvalues[i].end());
  }
  // all constraints are >=; hence lb is 1. and ub is \infty
  std::vector<double> rhslb(N, 1.), rhsub(N, solver.getInfinity());

  solver.loadProblem(len(S), N, starts.data(), indices.data(), values.data(), lb.data(), ub.data(), objective.data(), rhslb.data(), rhsub.data());
  // make all variables as integers
  for (int i = 0; i < len(S); ++i) {
    solver.setInteger(i);
  }
  CbcModel model(solver);
  //for(int i = 0; i < N; ++i) {
  //  std::string nm = "x_" + std::to_string(i);
  //  solver.setColName(i, nm.c_str());
  //}
  //solver.writeLp("sc");
  model.setLogLevel(0);
  const char* argv[] = {"", "-log", "0", "-solve"};
  CbcMain(4, argv, model);
  py::list setCover;
  if (model.status() == 0) {
    double* var = model.bestSolution();
    for (int i = 0; i < model.getNumCols(); ++i) {
      if (var[i] >= 0.9) setCover.append(S[i]);
    }
  }
  return setCover;
}

// expose set_cover as module with the function findSetCover to Python
BOOST_PYTHON_MODULE(set_cover)
{
  py::def("findSetCover", findSetCover);
};
