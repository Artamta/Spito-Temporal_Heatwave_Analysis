# Module for connectors and selectors used in deep graphs (e.g., heatwave analysis)

### Imports ###
import numpy as np

### Connectors and Selectors for Supernode (Heat Wave) Generation ###

def grid_2d_dx(x_s, x_t):
    """
    Calculate the distance between x-coordinates of two nodes.
    Args:
        x_s (float): Source x-coordinate.
        x_t (float): Target x-coordinate.
    Returns:
        float: Distance between x-coordinates.
    """
    return x_t - x_s

def grid_2d_dy(y_s, y_t):
    """
    Calculate the distance between y-coordinates of two nodes.
    Args:
        y_s (float): Source y-coordinate.
        y_t (float): Target y-coordinate.
    Returns:
        float: Distance between y-coordinates.
    """
    return y_t - y_s

def s_grid_2d_dx(dx, sources, targets):
    """
    Filter sources and targets based on x-coordinate distance.
    Args:
        dx (array): Array of x-coordinate distances.
        sources (array): Source nodes.
        targets (array): Target nodes.
    Returns:
        tuple: Filtered sources and targets.
    """
    dxa = np.abs(dx)
    sources = sources[dxa <= 1]
    targets = targets[dxa <= 1]
    return sources, targets

def s_grid_2d_dy(dy, sources, targets):
    """
    Filter sources and targets based on y-coordinate distance.
    Args:
        dy (array): Array of y-coordinate distances.
        sources (array): Source nodes.
        targets (array): Target nodes.
    Returns:
        tuple: Filtered sources and targets.
    """
    dya = np.abs(dy)
    sources = sources[dya <= 1]
    targets = targets[dya <= 1]
    return sources, targets

### Superedge Creation for Heatwave Clusters ###

def cp_node_intersection(g_ids_s, g_ids_t):
    """
    Compute the intersection of geographical locations between nodes.
    Args:
        g_ids_s (list of sets): Geographical IDs of source nodes.
        g_ids_t (list of sets): Geographical IDs of target nodes.
    Returns:
        array: Cardinality of intersections for each pair of nodes.
    """
    intsec = np.zeros(len(g_ids_s), dtype=object)
    intsec_card = np.zeros(len(g_ids_s), dtype=int)
    for i in range(len(g_ids_s)):
        intsec[i] = g_ids_s[i].intersection(g_ids_t[i])
        intsec_card[i] = len(intsec[i])
    return intsec_card

def cp_intersection_strength(n_unique_g_ids_s, n_unique_g_ids_t, intsec_card):
    """
    Compute the spatial overlap measure between clusters.
    Args:
        n_unique_g_ids_s (array): Number of unique geographical IDs in source clusters.
        n_unique_g_ids_t (array): Number of unique geographical IDs in target clusters.
        intsec_card (array): Cardinality of intersections between clusters.
    Returns:
        array: Intersection strength for each pair of clusters.
    """
    min_card = np.minimum(n_unique_g_ids_s, n_unique_g_ids_t).astype(np.float64)
    return intsec_card / min_card

### Temporal Distance Calculation ###

def time_dist(dtime_amin_s, dtime_amin_t):
    """
    Compute the temporal distance between clusters.
    Args:
        dtime_amin_s (array): Minimum time values for source clusters.
        dtime_amin_t (array): Minimum time values for target clusters.
    Returns:
        array: Temporal distances between clusters.
    """
    return dtime_amin_t - dtime_amin_s