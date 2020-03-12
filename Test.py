# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 12:43:49 2020
Used to check the results - 2-65 in the textbook - or check NIST
@author: manga
"""
import numpy as np
import LE_funcs as le

Temp = np.arange(-5, 46)
Temp_K = Temp + 273.15
#es
es = le.sat_vapor(Temp)*1e3

delta = le.del_solve(Temp)

delta2 = le.del_solve_2nd(Temp)

#test delta2 with finate difference
del_test = np.diff(delta)
results = del_test - delta2[:-1]