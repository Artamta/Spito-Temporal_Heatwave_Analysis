"""
Heatwave Detection Script
This script processes temperature data to detect extreme heat events and heatwaves.
It includes:
- Conversion of NetCDF data to a pandas DataFrame using xarray
- Calculation of thresholds for extreme heat days
- Identification of heatwaves based on spatial and temporal criteria
- Saving results to CSV files for further analysis
"""

### Imports ###
import xarray as xr
import numpy as np
import pandas as pd
import deepgraph as dg
import cppv
import gc

### Utility Functions ###
def calculate_percentile(data, percentile):
    """Calculate the given percentile of a list."""
    return np.percentile(data, percentile)

def calculate_magnitude(row):
    """Calculate the magnitude of an extreme heat event."""
    if row.t2m > row.t2m_amax_perc25:
        return (row.t2m - row.t2m_amax_perc25) / (row.t2m_amax_perc75 - row.t2m_amax_perc25)
    return 0

def convert_to_celsius(data):
    """Convert temperature from Kelvin to Celsius."""
    data['t2m'] = data['t2m'] - 273.15

### Core Functions ###
def preprocess_temperature_data(file_path):
    """Load and preprocess temperature data from a NetCDF file."""
    print("Loading data...")
    dataset = xr.open_dataset(file_path)
    
    # Create integer-based coordinates
    dataset['x'] = (('longitude'), np.arange(len(dataset.longitude)))
    dataset['y'] = (('latitude'), np.arange(len(dataset.latitude)))
    print("Integer-based coordinates created.")
    
    # Convert to pandas DataFrame
    data = dataset.to_dataframe().reset_index()
    del dataset
    gc.collect()
    print("Data converted to DataFrame.")
    
    # Add day of the year
    data['ytime'] = data['time'].apply(lambda x: x.dayofyear)
    
    # Convert temperature to Celsius
    convert_to_celsius(data)
    print("Temperature converted to Celsius.")
    
    return data

def calculate_thresholds(data):
    """Calculate daily thresholds for extreme heat events."""
    print("Calculating thresholds...")
    first = np.arange(350, 366)
    second = np.arange(1, 366)
    third = np.arange(1, 16)
    time_window = np.concatenate((first, second, third), axis=None)
    
    g_t = dg.DeepGraph(data)
    cpv_t, gv_t = g_t.partition_nodes(['x', 'y', 'ytime'], return_gv=True)
    cpv_t['t2m'] = gv_t['t2m'].apply(list)
    cpv_t.reset_index(inplace=True)
    
    thresholds = pd.DataFrame(columns=['x', 'y', 'ytime', 'thresh'])
    for i in range(366):
        g = dg.DeepGraph(cpv_t)
        k = time_window[i:i+31]
        g.filter_by_values_v('ytime', k)
        tmp, tmp_p = g.partition_nodes(['x', 'y'], return_gv=True)
        tmp['t2m'] = tmp_p['t2m'].apply(list)
        tmp.reset_index(inplace=True)
        tmp['thresh'] = tmp['t2m'].apply(lambda x: calculate_percentile(x, 99))
        tmp.drop(['t2m'], axis=1, inplace=True)
        tmp['ytime'] = i + 1
        thresholds = pd.concat([thresholds, tmp])
    
    result = pd.merge(data, thresholds, on=["ytime", "x", 'y'])
    print("Thresholds calculated.")
    return result

def detect_extreme_events(data):
    """Detect extreme heat events based on thresholds."""
    print("Detecting extreme events...")
    data["keep"] = np.where(data["t2m"] >= data["thresh"], True, False)
    extreme_events = data.loc[data['keep'] == True].drop(columns=['keep'])
    print("Extreme events detected.")
    return extreme_events

def calculate_heatwave_magnitudes(data, extreme_events):
    """Calculate magnitudes of extreme heat events."""
    print("Calculating magnitudes...")
    f_funcs = {'t2m': [np.max]}
    gg = dg.DeepGraph(data)
    gg_t = gg.partition_nodes(['x', 'y', 'year'], f_funcs)
    gg_t.reset_index(inplace=True)
    
    feature_funcs = {'t2m_amax': [lambda x: calculate_percentile(x, 75), lambda x: calculate_percentile(x, 25)]}
    ggt = dg.DeepGraph(gg_t)
    ggg = ggt.partition_nodes(['x', 'y'], feature_funcs)
    
    merged = pd.merge(extreme_events, ggg, on=['x', 'y'])
    merged['magnitude'] = merged.apply(calculate_magnitude, axis=1)
    print("Magnitudes calculated.")
    return merged

def create_heatwaves(extreme_events, min_grid_cells):
    """Group extreme events into heatwaves based on spatial and temporal criteria."""
    print("Creating heatwaves...")
    g, cpg, cpv = cppv.create_cpv(extreme_events, min_grid_cells)
    print("Heatwaves created.")
    return g, cpg, cpv

### Main Workflow ###
def main():
    # File paths
    input_file = "/path/to/your/input_file.nc"
    threshold_output = "/path/to/your/threshold_output.csv"
    extreme_output = "/path/to/your/extreme_output.csv"
    heatwave_output = "/path/to/your/heatwave_output.csv"
    
    # Parameters
    min_grid_cells = 100  # Minimum grid cells for a heatwave
    
    # Step 1: Preprocess temperature data
    data = preprocess_temperature_data(input_file)
    
    # Step 2: Calculate thresholds
    threshold_data = calculate_thresholds(data)
    threshold_data.to_csv(threshold_output, index=False)
    
    # Step 3: Detect extreme events
    extreme_events = detect_extreme_events(threshold_data)
    extreme_events.to_csv(extreme_output, index=False)
    
    # Step 4: Calculate magnitudes
    magnitudes = calculate_heatwave_magnitudes(data, extreme_events)
    magnitudes.to_csv(extreme_output, index=False)
    
    # Step 5: Create heatwaves
    _, _, heatwaves = create_heatwaves(magnitudes, min_grid_cells)
    heatwaves.to_csv(heatwave_output, index=False)
    print("Processing complete.")

if __name__ == "__main__":
    main()