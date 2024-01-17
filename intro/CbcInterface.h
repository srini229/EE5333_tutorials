/*
 * SolverInterface is a C++ interface to the Cbc solver
 * The main interface APIs to load a problem are: setObjective, setBounds, setInteger and addConstraint
 * The comments above each function describes the access and arguments
 * getSolution() returns the solution as a std::vector<double>
 */
#ifndef _CBC_INTERFACE_H_
#define _CBC_INTERFACE_H_

#define BOOST_BIND_GLOBAL_PLACEHOLDERS
#define BOOST_ALLOW_DEPRECATED_HEADERS

#include <vector>
#include <string>
#include <utility>
#include <cassert>
#include "coin/CbcModel.hpp"
#include "coin/OsiClpSolverInterface.hpp"

namespace CbcIF {
  typedef std::pair<int, double> VarCoeffPair; // pair of variable and its coeffecient in a constraint
  typedef std::vector<VarCoeffPair> VCVector; // vector of such pairs
  class SolverInterface {
    private:
      const int _numVars;
      int _numConstr;
      OsiClpSolverInterface _solver;
      std::vector<double> _obj;
      std::vector< std::vector<int> > _constrVars;
      std::vector< std::vector<double> > _constrCoeffs;
      std::vector< double > _varLb, _varUb, _constrLb, _constrUb;
      std::vector< int > _intVars;
    public:
      // constructor takes the number of variables in the problem as argument
      SolverInterface(const int N) : _numVars(N), _numConstr(0), _solver(), _obj(N, 0),\
                                  _constrVars(N, std::vector<int>()), \
                                  _constrCoeffs(N, std::vector<double>()), \
                                  _varLb(N, 0), _varUb(N, _solver.getInfinity()) {}

      const double getInfinity() const { return _solver.getInfinity(); }
      void setObjective(const std::vector<double>& obj) { _obj = obj; }

      // function to declare bounds of variables
      void setBounds(const int i, const double lb, const double ub) { _varLb[i] = lb; _varUb[i] = ub; }
      // function to declare variables as integers
      void setInteger(const int i) { if (i < _numVars) _intVars.push_back(i); }

      // example constraint a0 x[0] + a2 x[2] <= c1 
      // vc : vector of (variable, coefficient) pairs
      // vc.emplace_back(0, a0);
      // vc.emplace_back(2, a2)
      // lb is the lower bound of the constraint; in the e.g. 0 or -infinity
      // ub is the upper bound of the constraint; in the e.g. c1
      // to add the above constraint call: solver.addConstraint(vc, 0, c1);
      void addConstraint(const VCVector& vc, const double lb, const double ub)
      {
        for (auto& v : vc) {
          _constrVars[v.first].push_back(_numConstr);
          _constrCoeffs[v.first].push_back(v.second);
        }
        _constrLb.push_back(lb);
        _constrUb.push_back(ub);
        ++_numConstr;
      }

      void writeLp(const std::string& fn)
      {
        for(int i = 0; i < _numVars; ++i) {
          std::string nm = "x_" + std::to_string(i);
          _solver.setColName(i, nm.c_str());
        }
        _solver.writeLp(fn.c_str());
      }

      std::vector<double> getSolution()
      {
        assert(_numConstr == _constrLb.size() && _numConstr == _constrUb.size());

        std::vector<int> starts, indices;
        std::vector<double> values;
        starts.push_back(0);
        for (int i = 0; i < _numVars; ++i) {
          starts.push_back(starts.back() + _constrVars[i].size());
          indices.insert(indices.end(), _constrVars[i].begin(), _constrVars[i].end());
          values.insert(values.end(), _constrCoeffs[i].begin(), _constrCoeffs[i].end());
        }
        _solver.messageHandler()->setLogLevel(0);
        _solver.loadProblem(_numVars, _numConstr, starts.data(), indices.data(), values.data(),\
            _varLb.data(), _varUb.data(), _obj.data(), _constrLb.data(), _constrUb.data());
        for (auto& i : _intVars) _solver.setInteger(i); // variables are available only after loading problem

        CbcModel model(_solver);
        model.setLogLevel(0);
        const char* argv[] = {"", "-log", "0", "-solve"};
        CbcMain(4, argv, model);
        std::vector<double> sol;
        sol.reserve(_numVars);
        assert(_numVars == model.getNumCols());
        if (model.status() == 0) {
          double* var = model.bestSolution();
          if (var) {
            sol.insert(sol.end(), var, var + _numVars);
          }
        }
        return sol;
      }
  };
}

#endif
