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
# mrm_path_out = "G:/My Drive/Classes/ATM 233/ATM233 Final/Data/CIMIS/Calc/Davis_EB_2019.csv"
# mrm_path_in = 'G:/My Drive/Classes/ATM 233/ATM233 Final/Data/CIMIS/Davis_2019_hourly_all.csv'

# If looking at other stations, change station name and whatever file paths you have
station = 'ucr'
mrm_path_in = f"G:/My Drive/ATM233 Final/Data/CIMIS/preproc/{station}_hourly.csv"
mrm_path_out = f"G:/My Drive/ATM233 Final/Data/CIMIS/Calc/2015_2019_results/{station}_hourly_eb.csv"

df = pd.read_csv(mrm_path_in) 

"""
CIMIS Units: 
    ETo = mm
    precip = mm
    SolRad = W m-2 -> need to be in MJ m-2 hr-1 to use in the PM equation
    Rn = Net Radiation W m-2
    vapor pressure (es) = kPa 
    Air temp = deg C
    RH = %
    Td = deg C
    Wind speed = m s-1
    Wind dir = deg
    Soil Temp (STemp) = deg C
    ETo_PM = mm 
"""

#Define G (10% of Rn) - in W m-2 - during the day 
G = np.empty(len(df))
for i in range(len(df)):
    if(df['Rn'][i]) > 0:
        G[i] = np.array(df['Rn'][i]*0.1)
    else:
        G[i] = np.array(df['Rn'][i]*0.5)
df.insert(11, "G", G)
#constants (depending on the surface): 
Rd = 287.   #gas constant for dry air 
Cp = 1013.  #specific heat of air (J kg-1 C-1)
h = 0.12    #canopy height in meters
kap = 0.41   #von Karman coefficent
z = 2       #station height [m]

#Calculate CIMIS H and LE
df.insert(12, "LE_CIMIS", le.LE_calc(df['ETo']))
df.insert(13, "H_CIMIS", le.H_calc(df['LE_CIMIS'], df['Rn'], G))

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
ETo_1 = le.ETo_calc(df['Rn'], G, df['Ea'], df['WS'], df['Tair'], Ra, Rc, z)
LE_1 = le.LE_calc(ETo_1)
H_1 = le.H_calc(LE_1, df['Rn'], G)

#calculate surface temperature
Ts = le.poly_solve(df['Tair'], df['Rn'], G, es, df['Ea'], Ra, Rc, z) + df['Tair']

#solve ETo for the second order approximation
ETo_2 = le.ETo_calc_2(df['Tair'], Ts, df['Ea'], Rc, Ra, z, Cp)
LE_2 = le.LE_calc(ETo_2)
H_2 = le.H_calc(LE_2, df['Rn'], G)

#Make the output data frame: 
df_out = pd.DataFrame(df)
df_out.insert(14, "LE_1", LE_1)
df_out.insert(15, "H_1", H_1)
df_out.insert(16, "LE_2", LE_2)
df_out.insert(17, "H_2", H_2)
df_out.insert(18, "T_surf", Ts)
df_out.insert(19, "ETo_1PM", ETo_1)
df_out.insert(20, "ETo_2PM", ETo_2)

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
plt.plot( df['ETo_PM'][4319:(4319+48)], label = 'PM ETo (CIMIS)', color = 'purple')
plt.plot( ETo_2[4319:(4319+48)], label = '2nd order', color = 'blue')
plt.plot(ETo_1[4319:(4319+48)], label = '1st order', color = 'green')
plt.title('All ETo')
plt.ylabel('mm hr-1')
plt.legend()
plt.show()

#scatter plot
plt.scatter(df_out['ETo_1PM'], df_out['ETo_2PM'])
plt.ylabel('1st Order ETo [mm hr-1]')
plt.xlabel('2nd Order ETo [mm hr-1]')
plt.title('ETo Calculated')
plt.plot([0.0, 1.2], [0.0, 1.2], 'k-')
plt.grid()
plt.show()

#plt.scatter(df_out['ETo'], df_out['ETo_2PM'])
#plt.ylabel('CIMIS ETo [mm hr-1]')
#plt.xlabel('2nd Order ETo [mm hr-1]')
#plt.show()
#
#plt.scatter(df_out['ETo'], df_out['ETo_1PM'])
#plt.ylabel('CIMIS ETo [mm hr-1]')
#plt.xlabel('1st Order ETo [mm hr-1]')
#plt.show()

plt.scatter(df_out['ETo'], df_out['ETo_1PM'], label = '1st Order', color = 'green')
plt.scatter(df_out['ETo'], df_out['ETo_2PM'], label = '2nd Order', color = 'blue')
plt.ylabel('CIMIS ETo [mm hr-1]')
plt.xlabel('Calculated ETo [mm hr-1]')
plt.title('CIMIS ETo vs Calculated ETo')
plt.plot([0.0, 1.2], [0.0, 1.2], 'k-')
plt.legend(loc = 0)
plt.grid()
plt.show()

#plot full EB
plt.plot(df_out['Rn'][4319:(4319+48)], label = 'Rad', color = 'black')
plt.plot(df_out['LE_1'][4319:(4319+48)], label = 'LE', color = 'blue')
plt.plot(df_out['H_1'][4319:(4319+48)],label = 'H', color = 'red')
plt.plot(df_out['G'][4319:(4319+48)], label = 'G', color = 'brown')
plt.ylabel('W m-2')
plt.legend(loc = 0)
plt.title('Full Energy Budget (1st Order)')
plt.show()

plt.plot(df_out['Rn'][4319:(4319+48)], label = 'Rad', color = 'black')
plt.plot(df_out['LE_2'][4319:(4319+48)], label = 'LE', color = 'blue')
plt.plot(df_out['H_2'][4319:(4319+48)],label = 'H', color = 'red')
plt.plot(df_out['G'][4319:(4319+48)], label = 'G', color = 'brown')
plt.ylabel('W m-2')
plt.legend(loc = 0)
plt.title('Full Energy Budget (2nd Order)')
plt.show()

plt.plot(df_out['Rn'][4319:(4319+48)], label = 'Rad', color = 'black')
plt.plot(df_out['LE_CIMIS'][4319:(4319+48)], label = 'LE', color = 'blue')
plt.plot(df_out['H_CIMIS'][4319:(4319+48)],label = 'H', color = 'red')
plt.plot(df_out['G'][4319:(4319+48)], label = 'G', color = 'brown')
plt.ylabel('W m-2')
plt.legend(loc = 0)
plt.title('Full Energy Budget (CIMIS)')
plt.show()


