### Imports ###
import xarray
import argparse
import numpy as np
import pandas as pd
import deepgraph as dg
import plotting as plot
import con_sep as cs
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from sklearn.cluster import KMeans

### Argparser ###
def make_argparser():
    """
    Create argument parser for command-line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Path to the original dataset to be worked on.", type=str)
    parser.add_argument("-u", "--upgma_clusters", help="Number of UPGMA clusters.", type=int)
    parser.add_argument("-i", "--family", help="Number of the family.", type=int)
    return parser

parser = make_argparser()
args = parser.parse_args()
gv = pd.read_csv(args.data)
no_clusters = args.upgma_clusters
i = args.family
gv['time'] = pd.to_datetime(gv['time'])
g = dg.DeepGraph(gv)

# Create supernodes from the deep graph by partitioning the nodes by 'cp'
feature_funcs = {
    'time': [np.min, np.max],
    't2m': [np.mean, np.max],
    'magnitude': [np.sum],
    'latitude': [np.mean],
    'longitude': [np.mean],
    'ytime': [np.mean]
}
cpv, ggv = g.partition_nodes('cp', feature_funcs, return_gv=True)

# Append additional features to the supernodes table
cpv['g_ids'] = ggv['g_id'].apply(set)  # Geographical ID sets
cpv['n_unique_g_ids'] = cpv['g_ids'].apply(len)  # Cardinality of geographical ID sets
cpv['dt'] = cpv['time_amax'] - cpv['time_amin']  # Time spans
cpv['timespan'] = cpv.dt.dt.days + 1  # Duration in days
cpv.rename(columns={'magnitude_sum': 'HWMId_magnitude'}, inplace=True)

gvv = dg.DeepGraph(gv)
cpg = dg.DeepGraph(cpv)

# Create edges for the graph
cpg.create_edges(
    connectors=[cs.cp_node_intersection, cs.cp_intersection_strength],
    no_transfer_rs=['intsec_card'],
    logfile='create_cpe',
    step_size=1e7
)

# Create condensed distance matrix
dv = 1 - cpg.e.intsec_strength.values
del cpg.e

# Create linkage matrix
lm = linkage(dv, method='average', metric='euclidean')
del dv

# Form flat clusters and append their labels to 'cpv'
cpv['F_upgma'] = fcluster(lm, no_clusters, criterion='maxclust')

# Relabel families by size
f = cpv['F_upgma'].value_counts().index.values
fdic = {j: i for i, j in enumerate(f)}
cpv['F_upgma'] = cpv['F_upgma'].apply(lambda x: fdic[x])

# Create 'F_upgma' column in the nodes table
gv['F_upgma'] = np.ones(len(gv), dtype=int) * -1
gcpv = cpv.groupby('F_upgma')
it = gcpv.apply(lambda x: x.index.values)

for F in range(len(it)):
    cp_index = gvv.v.cp.isin(it.iloc[F])
    gvv.v.loc[cp_index, 'F_upgma'] = F

# Define feature functions for family-g_id intersection graph
def n_cp_nodes(cp):
    return len(cp.unique())

feature_funcs = {
    'magnitude': [np.sum],
    'latitude': np.min,
    'longitude': np.min,
    'cp': n_cp_nodes
}

# Create family-g_id intersection graph
fgv = gvv.partition_nodes(['F_upgma', 'g_id'], feature_funcs=feature_funcs)
fgv.rename(columns={'cp_n_cp_nodes': 'n_cp_nodes', 'longitude_amin': 'longitude', 'latitude_amin': 'latitude'}, inplace=True)

# Save updated 'cpv' and 'gv' tables
cpv.to_csv(f"add_your_path_here/cpv_fam{i}.csv", index=False)  # Replace with your path
gv.to_csv(f"add_your_path_here/gv_fam{i}.csv", index=False)  # Replace with your path

# Plot families and hits
plot.plot_families(no_clusters, fgv, gv, f'Family_{i}')
plot.plot_hits(no_clusters, fgv, gv, f'Family_{i}')