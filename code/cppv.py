# Module for creating CPV datasets (partitioning nodes based on spatio-temporal neighborhoods)

### Imports ###
import numpy as np
import deepgraph as dg
import pandas as pd
import con_sep as cs

def create_cpv(extr_data, b):
    """
    Create CPV dataset by partitioning nodes based on their spatio-temporal neighborhood.

    Args:
        extr_data (pd.DataFrame): Extreme dataset to build a deep graph.
        b (int): Spatial threshold - minimum unique grid cells required for a heatwave.

    Returns:
        tuple: 
            g (DeepGraph): Nodes table.
            gv (pd.DataFrame): Grouped nodes table.
            cpv (pd.DataFrame): Supernodes table.
    """
    # Convert time column to datetime and sort by time
    extr_data['time'] = pd.to_datetime(extr_data['time'])
    extr_data.sort_values('time', inplace=True)

    # Create the deep graph
    g = dg.DeepGraph(extr_data)

    # Create edges based on neighboring grids in a 3D dataset
    g.create_edges_ft(
        ft_feature=('itime', 1),
        connectors=[cs.grid_2d_dx, cs.grid_2d_dy],
        selectors=[cs.s_grid_2d_dx, cs.s_grid_2d_dy],
        r_dtype_dic={'ft_r': np.bool, 'dx': np.int8, 'dy': np.int8},
        max_pairs=1e7
    )

    # Rename edge column
    g.e.rename(columns={'ft_r': 'dt'}, inplace=True)

    # Consolidate singular components under label 0
    g.append_cp(consolidate_singles=True)

    # Delete edges to save memory
    del g.e

    # Define feature functions for supernodes (heatwaves)
    feature_funcs = {
        'time': [np.min, np.max],
        'itime': [np.min, np.max],
        't2m': [np.mean, np.max],
        'magnitude': [np.sum],
        'latitude': [np.mean],
        'longitude': [np.mean],
        'ytime': [np.mean]
    }

    # Ensure integer types for specific columns
    g.v['ytime'] = g.v.ytime.astype(int)
    g.v['x'] = g.v.x.astype(int)
    g.v['y'] = g.v.y.astype(int)

    # Partition nodes table based on component membership
    cpv, gv = g.partition_nodes('cp', feature_funcs, return_gv=True)

    # Append additional features to supernodes table
    cpv['g_ids'] = gv['g_id'].apply(set)  # Geographical ID sets
    cpv['n_unique_g_ids'] = cpv['g_ids'].apply(len)  # Cardinality of geographical ID sets
    cpv['ytimes'] = gv['ytime'].apply(set)  # Day of year sets
    cpv['dt'] = cpv['time_amax'] - cpv['time_amin']  # Time spans
    cpv['timespan'] = cpv.dt.dt.days + 1  # Duration in days
    cpv.rename(columns={'magnitude_sum': 'HWMId_magnitude'}, inplace=True)

    # Convert time spans to timedelta
    cpv['dt'] = pd.to_timedelta(cpv['dt'])

    # Filter out small heatwaves (shorter than 3 days or fewer than b grid cells)
    min_duration = pd.Timedelta(days=1)
    cpv["keep"] = np.where((cpv.dt > min_duration) & (cpv.n_unique_g_ids > b), True, False)
    cpv = cpv[cpv.keep].drop(columns=['keep'])

    # Filter out small events from the graph
    cpv.reset_index(inplace=True)
    cps = set(cpv.cp)
    g.filter_by_values_v('cp', cps)

    # Append component column to CPV
    cpv['cpp'] = cpv['cp']
    cpv.set_index('cpp', inplace=True)

    return g, gv, cpv