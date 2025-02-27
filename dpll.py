#!/usr/bin/env python3

import random

class Clause:
  def __init__(self, vl):
    self._vars = [v for v in vl]
    self._vact = [True for v in vl]
    self._nact = len(self._vars)
    self._val  = None # None for not decided; False/True for evaled to False/True

  def eval(self, m):
    cnt = 0
    for v in self._vars:
      if (True == m[abs(v)] and v > 0) or (False == m[abs(v)] and v < 0):
        return True
      if None != m[abs(v)]:
        cnt += 1
    if len(self._vars) == cnt:
      return False

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
    if True == self._val:
      self._vact = [False for v in self._vars]
      self._nact = 0
      return True
    elif False == self._val:
      return False
    for i in range(len(self._vact)):
      if self._vact[i] and None != m[abs(self._vars[i])]:
        self._vact[i] = False
    self._nact = self._vact.count(True)
    return self._val

  def __repr__(self):
    return '[' + str(self._vars) + ' ' + str(self._vact) + ' ' + str(self._nact) + ' ' + str(self._val) + ']'


def unitClauses(f):
  return [c for c in f if 1 == c._nact]
        

def pureLiterals(f, m):
  plc = [i for i in range(1, len(m)) if None == m[i]]
  
  p = []
  for l in plc:
    t = None
    for c in f:
      if l in c._vars:
        if None == t or True == t:
          t = True
        else:
          t = None
          break
      if -l in c._vars:
        if None == t or False == t:
          t = False
        else:
          t = None
          break
    if None != t:
      p.append(l if t else -l)
  return p


def pickBranchingLiteral(m):
  l = [i for i in range(1, len(m)) if None == m[i]]
  return l[0] if len(l) else None
#return random.choice(l)

def dpll(f, m):
  mc = [i for i in m]
  for c in f:
    if False == c.propagate(mc):
      return False, None
  if all([c._val == True for c in f]):
    m = [i for i in mc]
    return True, m
  while True:
    uC = unitClauses(f)
    p = pureLiterals(f, mc)
    for c in uC:
      v = c.getUnitVal()
      if None != v:
        val = True if v > 0 else False
        if None != mc[abs(v)] and val != mc[abs(v)]:
          return False, None # conflict
        mc[abs(v)] = val
    for v in p:
      val = True if v > 0 else False
      if None != mc[abs(v)] and val != mc[abs(v)]:
        return False, None # conflict
      mc[abs(v)] = val

    if len(uC) > 0 or len(p) > 0:
      for c in f:
        if False == c.propagate(mc):
          return False, None
    else: break
  l = pickBranchingLiteral(mc)
  if None != l:
    for assgn in [True, False]:
      mc[l] = assgn
      ret, mx = dpll(f, mc)
      if ret:
        m = mx
        return True, m
  else:
    return True, m
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
