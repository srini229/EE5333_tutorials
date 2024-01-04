#include "CbcInterface.h"
#include <boost/python.hpp>
#include <boost/python/list.hpp>
#include <boost/python/tuple.hpp>
#include <boost/python/extract.hpp>

namespace py = boost::python;

// N : number of vertices; vertices in {0,1,...(N-1)}
// S : list of tuples
// Return value : set cover as a list of tuples
py::list findSetCover(const int N, const py::list& S)
{
  std::vector<int> occ[N];
  for (int i = 0; i < len(S); ++i) {
    py::tuple Si = py::extract<py::tuple>(S[i]);
    for (int j = 0; j < len(Si); ++j) {
      occ[(int)py::extract<int>(Si[j])].push_back(i);
    }
  }

  CbcIF::SolverInterface solver(len(S));
  solver.setObjective(std::vector<double>(len(S), 1.));
  for (int i = 0; i < N; ++i) {
    CbcIF::VCVector vc;
    for (auto& j : occ[i]) {
      vc.emplace_back(j, 1.);
    }
    solver.addConstraint(vc, 1., solver.getInfinity());
  }

  // make all variables as integers
  for (int i = 0; i < len(S); ++i) {
    solver.setInteger(i);
    solver.setBounds(i, 0., 1.);
  }
  py::list setCover;
  auto var = solver.getSolution();
  solver.writeLp("setcover.lp");
  for (int i = 0; i < len(S); ++i) {
    if (var[i] >= 0.9) setCover.append(S[i]);
  }
  return setCover;
}

// expose set_cover as module with the function findSetCover to Python
BOOST_PYTHON_MODULE(set_cover)
{
  py::def("findSetCover", findSetCover);
};
