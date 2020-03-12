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
            'ETo (mm)': 'ETo',
            'Vap Pres (kPa)': 'Ea',
            'Dew Point (C)': 'Td',
            'Precip (mm)': 'Precip'
            }

# Set file paths
in_data_fp = 'data/hourly_2019.csv'
out_data_fp = 'data/davis_hourly_2019.csv'

# Read in data, parse out times (set hour 24 = 0), and subset to renamed variables
data = pd.read_csv(in_data_fp, parse_dates={'TIMESTAMP':[3, 4, 5]}, date_parser=parse_dates,
                   index_col='TIMESTAMP').rename(columns=var_dict)[list(var_dict.values())]

# Save data to out_data_fp
data.to_csv(out_data_fp)







