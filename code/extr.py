# Utility functions for temperature conversion and percentile calculations

import numpy as np

def conv_to_degreescelcius(data):
    """
    Convert temperature from Kelvin to Celsius.
    Args:
        data (pd.DataFrame): DataFrame containing temperature data in Kelvin.
    """
    data.t2m = data.t2m - 273.15

def calc_percentile(a_list):
    """
    Calculate the 99th percentile of a list.
    Args:
        a_list (list): Input list of values.
    Returns:
        float: 99th percentile value.
    """
    return np.percentile(a_list, 99)

def calc_perc(lst):
    """
    Flatten a nested list and calculate the 99th percentile.
    Args:
        lst (list of lists): Nested list of values.
    Returns:
        float: 99th percentile value.
    """
    flat_list = [item for sublist in lst for item in sublist]
    return calc_percentile(flat_list)