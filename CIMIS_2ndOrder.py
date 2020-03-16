# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 10:19:32 2020
This file defines the variables for solving the first and second order approximations of the LE equation.

"""
#import libaries and functions
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import LE_funcs as le

#import the CIMIS data
#specify path to the corrected cimis station data- based on MRM file path:
mrm_path_out = "G:/My Drive/Classes/ATM 233/ATM233 Final/Data/CIMIS/Calc/Davis_EB_2019.csv"
mrm_path_in = 'G:/My Drive/Classes/ATM 233/ATM233 Final/Data/CIMIS/davis_hourly_2019.csv'
df = pd.read_csv(mrm_path_in)

"""
CIMIS Units: 
    ETo = mm
    precip = mm
    SolRad = W m-2 -> need to be in MJ m-2 hr-1 to use in the PM equation
    vapor pressure (es) = kPa 
    Air temp = deg C
    RH = %
    Td = deg C
    Wind speed = m s-1
    Wind dir = deg
    Soil Temp (STemp) = deg C
"""

#Define G (10% of Rn) - in W m-2 - during the day 
G = np.empty(len(df))
for i in range(len(df)):
    if(df['SRad'][i]) > 0:
        G[i] = np.array(df['SRad'][i]*0.1)
    else:
        G[i] = np.array(df['SRad'][i]*0.5)

#constants (depending on the surface): 
Rd = 287.   #gas constant for dry air 
Cp = 1013  #specific heat of air (J kg-1 C-1)
h = 0.12    #canopy height in meters
kap = 0.41   #von Karman coefficent
z = 2       #station height [m]

#Aerodynamic Residance - option to improve
d = (2/3)*h  #displacement height
z_om = 0.123*h  #roughness length of momentum
z_oh = 0.1 * h   #roughness length of heat
Ra = 208/df['WS']    #Aerodynamic residance in s m-1

#Canopy Residance - to do: pick nighttime Ri value and chose the value based on time
Ri_day = 100     #daytime stomatal resistance
LAI_active = 0.5*(24*h)  #active LAI
Rc = Ri_day/LAI_active

#saturation vapor pressure of the air temperature (es_ta) - in kPa
es = le.sat_vapor(df['Tair'])   #need to add this to the data frame

#1st dervertive of the es_ta
delta1 = le.del_solve(df['Tair'])

#2nd dervertive of es_ta
delta2 = le.del_solve_2nd(df['Tair'])

#solve ETo with first order PM (answer in mm): 
ETo_1 = le.ETo_calc(df['SRad'], G, df['Ea'], df['WS'], df['Tair'], Ra, Rc, z)

#calculate surface temperature
Ts = le.poly_solve(df['Tair'], df['SRad'], G, es, df['Ea'], Ra, Rc, z) + df['Tair']

#solve ETo for the second order approximation
ETo_2 = le.ETo_calc_2(df['Tair'], Ts, df['Ea'], Rc, Ra, z, Cp)
ET_test = le.ETo_calc_2(df['Tair'], df['STemp'], df['Ea'], Rc, Ra, z, Cp)


#Make the output data frame: 
df_out = pd.DataFrame(df)
df_out.insert(11, "G", G)
df_out.insert(12, "T_surf", Ts)
df_out.insert(13, "ETo_1PM", ETo_1)
df_out.insert(14, "ETo_2PM", ETo_2)

#Make output CSV
df_out.to_csv(mrm_path_out)


#############################################################################
#Diagnositics (can be commented out when code is correct)
test_ETo_PM = ETo_1 - df['ETo']   #the difference between our and CIMIS PM ETo
test_Ts = Ts- df['Tair']

plt.plot(test_ETo_PM[4319:(4319+48)])
plt.title('Calc ETo - CIMIS ETo')
plt.ylabel('mm')
plt.show()

plt.plot(test_Ts[4319:(4319+48)])
plt.title('Calc Ts - Air Temp')
plt.ylabel('Deg C')
plt.show()


plt.plot( df['ETo'][4319:(4319+48)], label = 'CIMIS ETo', color = 'red')
plt.plot( ETo_2[4319:(4319+48)], label = '2nd order', color = 'blue')
plt.plot(ETo_1[4319:(4319+48)], label = '1st order', color = 'green')
plt.title('All ETo')
plt.ylabel('mm hr-1')
plt.legend()
plt.show()
#Diagnositic plots
#plt.plot(df['TIMESTAMP'], ETo2)