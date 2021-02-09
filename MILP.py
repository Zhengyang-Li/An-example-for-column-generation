# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 16:08:35 2021

@author: LI Zhengyang
"""

"""
Cutting Stock Problem
The length of a raw pipe is 218cm. Now the client wants 44 pipes of 81cm, 3 pipes of 70cm, 48 pipes of 68cm, what is the best cutting plan?

This problem can be formulated as an mixed integer linear programming (MILP) model:
    parameter:
        x(ni) the number of times item i is cut on roll n.
        y(n) = 1 if roll n is cut.
        l(i) the length of pipe i.
        L the length of a raw pipe.
        b(i) the required number of i type pipe.
    model:
        min = sum_n [ y(n) ]
        s.t.
        sum_n [ x(ni) ] >= b(i)                   for i in I (Set of different kinds of pipes)
        sum_i [ l(i) * x(ni) ] <= L * y(n)        for n in N (Set of stocks) 
        x(ni) are integers
        y(n) are binaries
"""

import sys
import numpy as np
import gurobipy as gp
from gurobipy import GRB
import time

timeStart = time.time()

class Material:
    def __init__(self, name, length, num):
        self.name = name
        self.length = length
        self.num = num

class Demand:
    def __init__(self, name, length, num):
        self.name = name
        self.length = length
        self.num = num
    
matSet = {}
demSet = {}
for i in range(1,201):
    matSet[i] = Material('pipe', 218, 1)
demSet[1] = Demand('pipe1', 81, 44)
demSet[2] = Demand('pipe2', 70, 3)
demSet[3] = Demand('pipe3', 68, 48)

def solver():
    m = gp.Model("MIP")
    x = m.addVars( demSet, matSet, vtype='I', name="x")
    y = m.addVars( matSet, vtype='B', name='y')
    m.setObjective(gp.quicksum(y[mat] for mat in matSet), GRB.MINIMIZE)
    m.addConstrs(gp.quicksum(x.select(dem,'*')) >= demSet[dem].num for dem in demSet.keys())
    m.addConstrs(gp.quicksum(demSet[dem].length * x[dem,mat] for dem in demSet) <= y[mat] * matSet[mat].length for mat in matSet.keys())
    m.optimize()
    sol = m.x
    return m.objVal

obj = solver()
print('Obj = ',obj)
# print('Cutting plan (each column is a plan):')
# print(A)
# print('Number of implementation times for each cutting plan:')
# print(sol)

timeEnd = time.time()
print('Optimal cutting plan found !')
print('running time =', timeEnd-timeStart)