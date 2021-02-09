# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 16:08:35 2021

@author: LI Zhengyang
"""

"""
Cutting Stock Problem
The length of a raw pipe is 218cm. Now the client wants 44 pipes of 81cm, 3 pipes of 70cm, 48 pipes of 68cm, what is the best cutting plan?

Column generation algorithm:
    Description:
        The column generation will decompose the original problem in to a restricted master problem (RMP) and a subproblem (SP),
        and solve RMP and SP iteratively until the optimal solution is obtained.

    parameters:
        a(ij): the number of pipes i that can obtain from a raw pipe in cutting plan j.
        l(i): the length of pipe i.
        L: the length of a raw pipe.
        b(i): the required number of pipes i.
        pi(i): the dual price of constraint i in the RMP.
        
    Variables:
        x(j): the number of implement times of cutting plan j.
        y(i): the number of pipes i that can obtain from a raw pipe in the new cutting plan. 
    
    model:
    RMP (output the dual price p(i) to check whether we can find a better cutting plan):
        min = sum_j [ x(j) ]
        s.t.
        sum_j [ a(ij) * x(j) ] >= b(i)       for i in I (Set of pipes' types)
        x(j) are continuous variables
        
        Note: In order to get p(i), we can also solve the dual of RMP, where p(i) will be the solution vector. Acutally, solving the dual of RMP is a better way since
        the number of variables in RMP dual will not increase. 
        
    SP (output a better cutting plan y(i), and resolve the RMP):
        max = 1 - sum_i [p(i) * y(i)]
        s.t.
        sum_i [ l(i) * y(i) ] <= L          for j in J (Set of cutting plan)
        y(i) are integer variables
        
    Stopping criteria:
        The RMP and SP will be iteratively implemented until the objective value of SP is less than 0. That means, no better cutting plan exisits. Dude, let's stop.
"""

import sys
import numpy as np
import gurobipy as gp
from gurobipy import GRB
import time

timeStart = time.time()

class Material:
    def __init__(self, name, length):
        self.name = name
        self.length = length
        self.num = float("inf")

class Demand:
    def __init__(self, name, length, num):
        self.name = name
        self.length = length
        self.num = num
    
matSet = {}
demSet = {}

matSet[1] = Material('rawPipe', 218)
demSet[1] = Demand('pipe1', 81, 44)
demSet[2] = Demand('pipe2', 70, 3)
demSet[3] = Demand('pipe3', 68, 48)

def init_solution():
    """
    provide a initial cutting plan for the RMP
    """
    c = np.ones(3)
    A = np.identity(3)
    b = []
    for i in demSet:
        b.append(demSet[i].num)
    b = np.array(b)
    return c,A,b

def solver_RMP(c,A,b):
    m = gp.Model("CG")
    x = m.addMVar(len(c), vtype='C', name="x")
    m.setObjective(c @ x, GRB.MINIMIZE)
    m.addConstr(A @ x >= b)
    m.optimize()
    sol = x.X
    return m.objVal, sol, m.Pi

def sp(dualPrice):
    """
    generate the model parameters for sp
    """
    c = np.array(dualPrice)
    A = []
    for i in demSet:
        A.append(demSet[i].length)
    A = np.array(A)
    b = np.array([matSet[1].length])
    return c, A, b

def solver_SP(c,A,b):
    m = gp.Model("CG")
    x = m.addMVar(len(c), vtype='I', name="x")
    m.setObjective(c @ x, GRB.MAXIMIZE)
    m.addConstr(A @ x <= b)
    m.optimize()
    sol = x.X
    return m.objVal, sol

#initialization
spObj = float("inf")
iter = 0
rmpC,rmpA,rmpB = init_solution()

while 1-spObj < 0 and iter < 500:
    iter = iter + 1

    rmpObj, rmpSol, rmpDual = solver_RMP(rmpC,rmpA,rmpB)

    c,A,b = sp(rmpDual)
    spObj, spSol = solver_SP(c,A,b)

    print('           ')
    print('Iter=', iter)
    print('Obj=',rmpObj)
    print('Cutting plan (each column is a plan):')
    print(rmpA)
    print('Number of implementation times for each cutting plan:')
    print(rmpSol)

    """
    Generation a new column in the RMP problem
    """
    rmpC = np.ones(len(demSet)+iter)
    rmpA = np.hstack([ rmpA , np.reshape(np.array(spSol),(len(demSet),1)) ])

timeEnd = time.time()
print('Optimal cutting plan found !')
print('Running time =', timeEnd-timeStart)
