# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 15:20:46 2020

Code to convert the names and units of the CIMIS data 
Adpated from Matt (new version includes all of the data and Rn)

@author: manga
"""

import pandas as pd

# Program used to convert raw, metric data from CIMIS to a more usable form

def parse_dates(yr_m_d, hr, doy):
    '''
    Date parser for pandas.read_csv when yr_m_d and hour are the columns
    '''
    yr = yr_m_d[-4:]
    if '2400' in hr:
        hr = '000'
        return pd.datetime.strptime(f'{yr}{(int(doy)+1):03}{int(hr):04}', '%Y%j%H%M')
    else:
        return pd.datetime.strptime(f'{yr}{int(doy):03}{int(hr):04}', '%Y%j%H%M')

# Variables (other than dates) to convert names and subset to
var_dict = {'Air Temp (C)': 'Tair',
            'Rel Hum (%)': 'RH',
            'Wind Speed (m/s)': 'WS',
            'Wind Dir (0-360)': 'WD',
            'Soil Temp (C)': 'STemp',
            'Sol Rad (W/sq.m)': 'SRad',
            'Net Rad (W/sq.m)': 'Rn',
            'ETo (mm)': 'ETo',
            'Vap Pres (kPa)': 'Ea',
            'Dew Point (C)': 'Td',
            'Precip (mm)': 'Precip',
            'PM ETo (mm)': 'ETo_PM'
            }

# Set file paths
in_data_fp = "G:/My Drive/Classes/ATM 233/ATM233 Final/Data/CIMIS/hourly_2015_20.csv"
out_data_fp = "G:/My Drive/Classes/ATM 233/ATM233 Final/Data/CIMIS/Davis_2015_20_hourly_all.csv"

# Read in data, parse out times (set hour 24 = 0), and subset to renamed variables
data = pd.read_csv(in_data_fp, parse_dates={'TIMESTAMP':[3, 4, 5]}, date_parser=parse_dates,
                   index_col='TIMESTAMP').rename(columns=var_dict)[list(var_dict.values())]

# Save data to out_data_fp
data.to_csv(out_data_fp)
