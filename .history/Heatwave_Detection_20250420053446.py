# Heatwave Detection Script
# Converts NetCDF to pandas DataFrame, calculates thresholds, detects extreme heat events, and identifies heatwaves.

### Imports ###
import xarray as xr
import numpy as np
import pandas as pd
import deepgraph as dg
import cppv
import gc

### Utility Functions ###
def perc25(a_list):
    """Calculate the 25th percentile of a list."""
    return np.percentile(a_list, 25)

def perc75(a_list):
    """Calculate the 75th percentile of a list."""
    return np.percentile(a_list, 75)

def calc_mag(data):
    """Calculate the magnitude of an extreme heat event."""
    if data.t2m > data.t2m_amax_perc25:
        return (data.t2m - data.t2m_amax_perc25) / (data.t2m_amax_perc75 - data.t2m_amax_perc25)
    return 0

def conv_to_degreescelcius(data):
    """Convert temperature from Kelvin to Celsius."""
    data['t2m'] = data['t2m'] - 273.15

### Main Script ###
# Read NetCDF data
d = xr.open_dataset("add_your_path_here.nc")  # Add your input file path here
print("Data loaded.")

# Create integer-based coordinates
d['x'] = (('longitude'), np.arange(len(d.longitude)))
d['y'] = (('latitude'), np.arange(len(d.latitude)))
print("Integer-based coordinates created.")

# Convert to DataFrame and reset index
vt = d.to_dataframe().reset_index()
del d
gc.collect()
print("Data converted to DataFrame.")

# Add day of the year and convert temperature to Celsius
vt['ytime'] = vt['time'].apply(lambda x: x.dayofyear)
conv_to_degreescelcius(vt)
print("Day of year added and temperature converted.")

# Remove 366th day (leap years)
g_t = dg.DeepGraph(vt)
g_t.filter_by_values_v('ytime', np.arange(366))
print("Leap day removed.")

# Partition data and calculate thresholds
cpv_t, gv_t = g_t.partition_nodes(['x', 'y', 'ytime'], return_gv=True)
cpv_t['t2m'] = gv_t['t2m'].apply(list)
cpv_t.reset_index(inplace=True)

tmp2 = pd.DataFrame(columns=['x', 'y', 'ytime', 'thresh'])
time_window = np.concatenate((np.arange(350, 366), np.arange(1, 366), np.arange(1, 16)))
for i in range(366):
    g = dg.DeepGraph(cpv_t)
    g.filter_by_values_v('ytime', time_window[i:i+31])
    tmp, tmp_p = g.partition_nodes(['x', 'y'], return_gv=True)
    tmp['t2m'] = tmp_p['t2m'].apply(list)
    tmp.reset_index(inplace=True)
    tmp['thresh'] = tmp['t2m'].apply(lambda x: np.percentile(x, 99))
    tmp.drop(['t2m'], axis=1, inplace=True)
    tmp['ytime'] = i + 1
    tmp2 = pd.concat([tmp2, tmp])

result = pd.merge(vt, tmp2, on=["ytime", "x", 'y']).drop(columns=['n_nodes'])
print("Thresholds calculated.")

# Add geographical labels and save threshold dataset
result['g_id'] = result.groupby(['longitude', 'latitude']).grouper.group_info[0].astype(np.uint32)
result.to_csv("add_your_path_here/thresh_new.csv", index=False)  # Add your output path here
print("Threshold dataset saved.")

# Detect extreme heat events
result["keep"] = np.where(result["t2m"] >= result["thresh"], True, False)
extr = result.loc[result['keep']].drop(columns=['keep'])
print("Extreme heat events detected.")

# Add integer-based time and sort by time
times = pd.date_range(extr.time.min(), extr.time.max(), freq='D')
tdic = {time: itime for itime, time in enumerate(times)}
extr['itime'] = extr.time.apply(lambda x: tdic[x]).astype(np.uint16)
extr.sort_values('time', inplace=True)

# Calculate daily magnitudes
f_funcs = {'t2m': [np.max]}
gg = dg.DeepGraph(vt)
gg_t = gg.partition_nodes(['x', 'y', 'year'], f_funcs).reset_index()

feature_funcs = {'t2m_amax': [perc75, perc25]}
ggt = dg.DeepGraph(gg_t)
ggg = ggt.partition_nodes(['x', 'y'], feature_funcs)

rex = pd.merge(extr, ggg, on=['x', 'y'])
rex['magnitude'] = rex.apply(calc_mag, axis=1)
rex.drop(columns=['t2m_amax_perc25', 't2m_amax_perc75', 'thresh'], inplace=True)
rex.to_csv("add_your_path_here/extr_new.csv", index=False)  # Add your output path here
print("Extreme dataset saved.")

# Create heatwaves and save results
g, cpg, cpv = cppv.create_cpv(rex, 100)  # Replace 100 with your desired minimum grid size
cpv.to_csv("add_your_path_here/cpv_new.csv", index=False)  # Add your output path here
g.v.to_csv("add_your_path_here/gv_new.csv", index=False)  # Add your output path here
print("Heatwaves created and saved.")