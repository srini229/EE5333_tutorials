#!/usr/bin/env python3

import random

class Clause:
  def __init__(self, vl):
    self._vars = [v for v in vl]
    self._vact = [True for v in vl]
    self._nact = len(self._vars)
    self._val  = None # None for not decided; False/True for evaled to False/True

  def eval(self, m):
    return None

  def getUnitVal(self):
    if self._nact == 1:
      for i in range(len(self._vars)):
        if self._vact[i]:
          return self._vars[i]
    return None
  
  def propagate(self, m):
    self._vact = [True for v in self._vars]
    self._val = self.eval(m)
    return self._val

  def __repr__(self):
    return '[' + str(self._vars) + ' ' + str(self._vact) + ' ' + str(self._nact) + ' ' + str(self._val) + ']'


def unitClauses(f):
  return [c for c in f if 1 == c._nact]
        

def pureLiterals(f, m):
  plc = [i for i in range(1, len(m)) if None == m[i]]
  
  p = []

  return p


def pickBranchingLiteral(m):
  l = [i for i in range(1, len(m)) if None == m[i]]
  return l[0] if len(l) else None
#return random.choice(l)

def dpll(f, m):
  mc = [i for i in m]
  return False, None


def loadCNFFile(fn):
  numvars = 0
  numclauses = 0
  clauses = []
  with open(fn, 'r') as fs:
    for line in fs:
      if line[0] == '%': break
      # p is the description line
      if line[0] == 'p':
        numvars = int(line.split()[2])
        numclauses = int(line.split()[3])
        continue
      # c is a comment
      if line[0] == 'c': continue
      if numvars > 0:
        tmp = line.split()
        tmp = [int(tmp[i]) for i in range(len(tmp) - 1)]
        clauses.append(Clause(tmp))
        assert abs(tmp[0]) <= numvars and abs(tmp[1]) <= numvars and abs(tmp[2]) <= numvars
  assert len(clauses) == numclauses
  return numvars, clauses



if __name__ == '__main__':
  import argparse

  ap = argparse.ArgumentParser()
  ap.add_argument("-c", "--cnf", type=str, default="", help='<cnf file>')
  args = ap.parse_args()
  if args.cnf != "":
    print(f"CNF file  : {args.cnf}")
    numvars, clauses = loadCNFFile(args.cnf)
    m = [None for i in range(numvars + 1)]
    ret, m = (dpll(clauses, m))
    print([(i if m[i] == True else -i) for i in range(1, len(m))])
