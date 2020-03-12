# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 11:58:55 2020
Has the function for the saturation vapor pressure solver. 
@author: manga
"""
import numpy as np

def MJ_conv(x):
    #takes either Rn or G and converts from W m-2 to MJ m-2
    x = x*1e-6  
    return(x)

def lamba_calc(Ta):
    lamda = 2.501 - 0.002361*Ta #MJ kg-1
    return(lamda)
    
def pressure_calc(z):
    P = ((101.3*(293-0.0065*z))/293)**5.26 #kPa
    return(P)
    
def gamma_calc(Ta, z):
    lamda = lamba_calc(Ta)
    P = pressure_calc(z)
    gamma = 0.00163*P / lamda  #Pschrometric constant (kPa deg C-1)
    return(gamma)
    
def ro_calc(z, Ta):
    Rd = 287e-6   #gas constant for dry air in MJ kg-1 K-1
    P = pressure_calc(z)  #in kPa
    Tv = (1.01)*(Ta+273.15)  #in K
    ro = P/(Tv*Rd)  #kPa/ (MJ kg-1)
    return(ro)
    
def sat_vapor(Ta):
    es = 0.6108*np.exp((17.27*Ta)/(Ta+237.3))  #kPa
    return(es)

def del_solve(Ta):
    es = sat_vapor(Ta)
    delta = (4098.171*es)/(Ta + 237.2)**2
    return(delta)
    
def del_solve_2nd(Ta):
    a = 4098.171
    b = 474.6
    es = sat_vapor(Ta)
    delta2 = es* (a*(a - 2*Ta - b))/(Ta + 237.3)**4 
    return(delta2)

def ETo_calc(Rn, G, ea, U, Ta, z):
    es = sat_vapor(Ta)
    Cd = 24
    Cn = 37
    gamma = gamma_calc(Ta, z)
    delta = del_solve(Ta)
    lamda = lamba_calc(Ta)  #in MJ kg-1
    
    #convert Rn and G into MJ m-2 hr-1
    Rn = MJ_conv(Rn)
    G = MJ_conv(G)
    
    bot = delta + (gamma*(1+Cd*U))
    top2 = (gamma*Cn) / (Ta+273.15)
    
    ETo = (delta*(Rn-G))/(lamda*(bot)) + (top2*U*(es - ea))/(bot)
    return(ETo)

def ETo_calc_2(Ta, Ts, ea, Rc, Ra, z, Cp):
    """
    This calculates the LE based on the LE equation. 
    """
    es = sat_vapor(Ts)  #saturation vapor pressure of the surface
    ro = ro_calc(z, Ta)
    lamba = lamba_calc(Ta)   #latent heat of vaporaization (MJ kg-1)
    grad = es - ea  #gradident
    
    ETo2 = ro*Cp/lamba * (grad/(Rc + Ra))
    return(ETo2)
    
def poly_solve(Ta, Rn, G, es, ea, Ra, Rc, z):
    """
    Import: 
        Ta = air temperature
        Rn = net radiation
        G = ground heat flux
        es = saturation vapor pressure
        ea = actural vapor pressure of air
        Rc = canopy resistance
        Ra = aerodynamic resistance
        z = height of measurement 
    """
    #constants: 
    Cp = 1004.67  #specific heat of air

    ro = ro_calc(Ta, z)
    gamma = gamma_calc(Ta, z)
    
    delta1 = del_solve(Ta)
    delta2 = del_solve_2nd(Ta)

    #Solve for the surface temperature: 
    a = -Ra/(2*gamma*(Rc+Ra))*delta2
    b = -(1+((delta1*Ra)/(gamma*(Rc+Ra))))
    c = Ra*((Rn-G)/(ro*Cp)-((es-ea)/(gamma*(Rc+Ra))))
    d = (b**2) - 4*a*c  #solve discrimant 
    
    #calculate solutions (For Ts - Ta)
    sol1 = (-b-np.sqrt(d))/(2*a)
    sol2 = (-b+np.sqrt(d))/(2*a)
    #based on 1 year of data - sol 1 seems more reasonable. That will be used going forward.

    return(sol1)
    