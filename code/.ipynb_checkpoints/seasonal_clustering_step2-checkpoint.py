### Imports ###
import xarray
import argparse
# the usual
import numpy as np
import pandas as pd
import deepgraph as dg
import plotting as plot
import con_sep as cs
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from sklearn.cluster import KMeans

### SEASONAL FUNCTIONS ###
def get_meteorological_season(day_of_year):
    """Convert day of year to meteorological season"""
    if day_of_year >= 335 or day_of_year <= 59:
        return 0  # DJF (Winter)
    elif 60 <= day_of_year <= 151:
        return 1  # MAM (Spring)
    elif 152 <= day_of_year <= 243:
        return 2  # JJA (Summer)
    elif 244 <= day_of_year <= 334:
        return 3  # SON (Fall)
    else:
        return -1  # Error case

def season_name(season_code):
    """Convert season code to name"""
    season_names = {0: 'DJF_Winter', 1: 'MAM_Spring', 2: 'JJA_Summer', 3: 'SON_Fall'}
    return season_names.get(season_code, 'Unknown')

### Argparser ###
def make_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Give the path to the original dataset to be worked on.",
                        type=str)
    parser.add_argument("-u", "--upgma_clusters", help="Give the number of upgma clusters",
                        type=int)
    parser.add_argument("-s", "--season", help="Give the season number (0=DJF, 1=MAM, 2=JJA, 3=SON)",
                        type=int)
    return parser

parser = make_argparser()
args = parser.parse_args()
gv = pd.read_csv(args.data)
no_clusters = args.upgma_clusters
season_num = args.season
gv['time']=pd.to_datetime(gv['time'])

# SEASONAL FILTERING - NEW SECTION
print(f"🌡️ Processing {season_name(season_num)} heatwaves...")

# Assign seasons if not already present
if 'F_season' not in gv.columns:
    gv['F_season'] = gv['ytime'].apply(get_meteorological_season)

# Filter to specific season
gv_seasonal = gv[gv['F_season'] == season_num].copy()
print(f"✅ Filtered to {len(gv_seasonal)} {season_name(season_num)} events")

if len(gv_seasonal) == 0:
    print(f"❌ No events found for {season_name(season_num)}!")
    exit()

# Create DeepGraph with seasonal data
g = dg.DeepGraph(gv_seasonal)

# create supernodes from deep graph by partitioning the nodes by cp
# feature functions applied to the supernodes
feature_funcs = {'time': [np.min, np.max],
                 't2m': [np.mean],
                 'magnitude': [np.sum],
                 'latitude': [np.mean],
                 'longitude': [np.mean], 
                 't2m': [np.max],'ytime':[np.mean],}

# partition graph
cpv, ggv = g.partition_nodes('cp', feature_funcs, return_gv=True)

# append neccessary stuff
# append geographical id sets
cpv['g_ids'] = ggv['g_id'].apply(set)
# append cardinality of g_id sets
cpv['n_unique_g_ids'] = cpv['g_ids'].apply(len)
# append time spans
cpv['dt'] = cpv['time_amax'] - cpv['time_amin']
# append time spans
cpv['timespan'] = cpv.dt.dt.days+1
cpv.rename(columns={'magnitude_sum': 'HWMId_magnitude'}, inplace=True)

print(f"📊 Found {len(cpv)} heatwaves in {season_name(season_num)}")

gvv = dg.DeepGraph(gv_seasonal)  # Use seasonal data
cpg = dg.DeepGraph(cpv)

# create edges
cpg.create_edges(connectors=[cs.cp_node_intersection, 
                             cs.cp_intersection_strength],
                             no_transfer_rs=['intsec_card'],
                             logfile=f'create_cpe_{season_name(season_num)}',
                             step_size=1e7)

# create condensed distance matrix
dv = 1 - cpg.e.intsec_strength.values
del cpg.e

# create linkage matrix
lm = linkage(dv, method='average', metric='euclidean')
del dv
    
# form flat clusters and append their labels to cpv
cpv['F_upgma'] = fcluster(lm, no_clusters, criterion='maxclust')
# relabel families by size
f = cpv['F_upgma'].value_counts().index.values
fdic = {j: i for i, j in enumerate(f)}
cpv['F_upgma'] = cpv['F_upgma'].apply(lambda x: fdic[x])

# create F col
gv_seasonal['F_upgma'] = np.ones(len(gv_seasonal), dtype=int) * -1
gcpv = cpv.groupby('F_upgma')
it = gcpv.apply(lambda x: x.index.values)

for F in range(len(it)):
    cp_index = gvv.v.cp.isin(it.iloc[F])
    gvv.v.loc[cp_index, 'F_upgma'] = F
    
# feature funcs
def n_cp_nodes(cp):
  return len(cp.unique())

feature_funcs = {'magnitude': [np.sum],
                     'latitude': np.min,
                     'longitude': np.min,
                     'cp': n_cp_nodes}

# create family-g_id intersection graph
fgv = gvv.partition_nodes(['F_upgma', 'g_id'], feature_funcs=feature_funcs)
fgv.rename(columns={'cp_n_cp_nodes': 'n_cp_nodes', 'longitude_amin':'longitude','latitude_amin':'latitude'}, inplace=True)

# MODIFIED SAVE PATHS - Use season name instead of family number
import os
os.makedirs('results/seasonal_clustering_step2', exist_ok=True)

# save updated cpv and gv table
cpv.to_csv(path_or_buf = f"results/seasonal_clustering_step2/cpv_{season_name(season_num)}_clusters.csv", index=False)
gv_seasonal.to_csv(path_or_buf = f"results/seasonal_clustering_step2/gv_{season_name(season_num)}_clusters.csv", index=False)

plot.plot_families(no_clusters,fgv,gv_seasonal,f'{season_name(season_num)}_SubClusters')
# uncomment if you want to plot the number of hits and not only the number of heat waves at every grid cell
plot.plot_hits(no_clusters,fgv,gv_seasonal,f'{season_name(season_num)}_SubClusters')

print(f"🎉 {season_name(season_num)} clustering completed!")
print(f"📁 Results saved in: results/seasonal_clustering_step2/")
print(f"📊 Created {no_clusters} sub-clusters within {season_name(season_num)} season")