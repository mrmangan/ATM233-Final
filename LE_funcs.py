# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 11:58:55 2020
Has the function for the saturation vapor pressure solver. 
@author: manga
"""
import numpy as np

def MJ_conv(x):
    #takes either Rn or G and converts from W m-2 to MJ m-2 hr-1
    x = 1e-6*x*3600   
    return(x)

def lamba_calc(Ta):
    lamda = 2.501 - 0.002361*Ta #MJ kg-1
    return(lamda)
    
def pressure_calc(z):
    P = 101.3*((293-0.0065*z)/293)**5.26 #kPa
    return(P)
    
def gamma_calc(Ta, z):
    lamda = lamba_calc(Ta)
    P = pressure_calc(z)
    gamma = 0.00163*P / lamda  #Pschrometric constant (kPa deg C-1)
    return(gamma)
    
def ro_calc(z, Ta):
    Rd = 287   #gas constant for dry air in J kg-1 K-1
    P = pressure_calc(z)*1000  #in Pa
    Tv = (1.01)*(Ta+273.15)  #in K
    ro = P/(Tv*Rd)  #Pa/ (MJ kg-1) = 
    return(ro)  #in kg/m3
    
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

def ETo_calc(Rn, G, ea, U, Ta, Ra, Rc, z):
    es = sat_vapor(Ta)
    #split the Cd and Cn by day and night:
    Cd = np.empty(len(Rn))
    for i in range(len(Rn)):
        if(Rn[i]) > 0:
            Cd[i] = 0.24
        else:
            Cd[i] = 0.96
    Cn = 37
    gamma = gamma_calc(Ta, z)
    delta = del_solve(Ta)
    lamda = lamba_calc(Ta)  #in MJ kg-1
    #ro = ro_calc(z, Ta)
    
    #convert Rn and G into MJ m-2 hr-1
    Rn = MJ_conv(Rn)
    G = MJ_conv(G)
    
    a = delta*(Rn-G)
    c = gamma * (Cn / (Ta+273.15)) * U *(es - ea)
    d = delta + gamma*(1 + Cd*U)
    
    #bot = delta + (gamma*(1+Cd*U))
    #top2 = (gamma*Cn) / (Ta+273.15)
    
    #ETo = (delta*(Rn-G))/(lamda*(bot)) + (top2*U*(es - ea))/(bot)
    ETo = a/(lamda*d) + c/d
    
    return(ETo)
    

def ETo_calc_2(Ta, Ts, ea, Rc, Ra, z, Cp):
    """
    This calculates the LE based on the LE equation. 
    Ingnore CIMIS units - and use SI units
    """
    es = sat_vapor(Ts)  #saturation vapor pressure of the surface (kPa)
    ro = ro_calc(z, Ta)      #kg m-3
    #lamba = lamba_calc(Ta)   #latent heat of vaporaization (MJ kg-1)
    gamma = gamma_calc(Ta, z)
    #gamma = 66   #Pa K-1
    grad = es - ea  #gradident
    
    ETo2 = ro*Cp/gamma * (grad/(Rc + Ra))  #in W m-2
    ETo2 = MJ_conv(ETo2) #convert from W m-2 to MJ  m-2 hr-1
    ETo2 = ETo2*0.408  #convert to mm hr-1
    
    return(ETo2)  #in mm hr-1
    
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
        
        NOTE: This is not working during the day.  The night values seem reasonable. 
    """
    #constants: 
    Cp = 1013  #specific heat of air (J kg-1 C-1)
 
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
    
def LE_calc(ET):
    ET = ET / 0.408   #convert to MJ m-2 hr-1
    LE = ET / (1e-6*3600)  #convert to W m-2)
    return(LE)
    
def H_calc(LE, Rn, G):
    #calculate H by energy budget residual
    H = Rn - G - LE
    return(H)
    
#def CIMIS(ea, RH, Rs, Ta, U, z):
#    alf = 0.3  #what do they use?
#    Tk = Ta + 273.15
#    es = sat_vapor(Ta)
#    VPD = es - ea
#    DEL = del_solve(Ta)
#    P = 101.3-0.0115*z + 5.44e-7 *z**2
#    GAM = 0.000646*(1+0.000946*Ta)*P
#    W = DEL/(DEL + GAM)
#    FU2 = np.empty(len(Rs))
#    for i in range(len(Rs)):
#        if(Rn[i]) > 0:
#            FU2[i] = 0.03 + 0.576*U
#        else:
#            FU2[i] = 0.125 + 0.439*U
#    Rn = (1-alf)