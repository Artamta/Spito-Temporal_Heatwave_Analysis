### Imports ###
import argparse
import numpy as np
import pandas as pd
import deepgraph as dg
import plotting as plot
import con_sep as cs
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
import matplotlib.cm as cm
import os

### Functions ###

def get_meteorological_season(day_of_year):
    """
    Convert day of year to meteorological season
    DJF (Winter): Dec, Jan, Feb (335-365, 1-59)
    MAM (Spring): Mar, Apr, May (60-151) 
    JJA (Summer): Jun, Jul, Aug (152-243)
    SON (Fall): Sep, Oct, Nov (244-334)
    """
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

def season_label(season_code):
    """Convert season code to short label"""
    season_labels = {0: 'DJF', 1: 'MAM', 2: 'JJA', 3: 'SON'}
    return season_labels.get(season_code, 'UNK')

def plot_families(number_families, fgv, v, plot_title):
    """Plot heat wave families/seasons on maps"""
    families = np.arange(number_families)
    for F in families:
        try:
            # Create new DeepGraph instance for each season
            gt = dg.DeepGraph(fgv.loc[F])
            
            # Configure map projection
            kwds_basemap = {'llcrnrlon': v.longitude.min() - 1,
                           'urcrnrlon': v.longitude.max() + 1,
                           'llcrnrlat': v.latitude.min() - 1,
                           'urcrnrlat': v.latitude.max() + 1}
            
            # Configure scatter plots
            kwds_scatter = {'s': 1,
                           'c': gt.v.n_cp_nodes.values,
                           'cmap': 'viridis_r',
                           'edgecolors': 'none'}
            
            # Create scatter plot on map
            obj = gt.plot_map(lat='latitude', lon='longitude', 
                             kwds_basemap=kwds_basemap, 
                             kwds_scatter=kwds_scatter)
            
            # Configure plots
            obj['m'].drawcoastlines(linewidth=.8)
            obj['m'].drawparallels(range(-50, 50, 20), linewidth=.2)
            obj['m'].drawmeridians(range(0, 360, 20), linewidth=.2)
            cb = obj['fig'].colorbar(obj['pc'], fraction=.022, pad=.02)
            cb.set_label('Number of Heatwaves', fontsize=15)
            obj['ax'].set_title(f'{season_name(F)} Heatwaves')
            
            # Save figure with updated path
            os.makedirs('results/seasonal_clustering_step1', exist_ok=True)
            obj['fig'].savefig(f'results/seasonal_clustering_step1/{plot_title}_Season_{F}_{season_name(F)}.png',
                              dpi=300, bbox_inches='tight')
            plt.close(obj['fig'])
            
        except Exception as e:
            print(f"Warning: Could not plot season {season_name(F)}: {e}")
            continue

def plot_seasonal_distribution(gv, seasons_present):
    """Plot day of year distribution for each season"""
    plt.figure(figsize=(18, 7))
    colors = ['blue', 'green', 'red', 'orange']
    
    for season in seasons_present:
        season_data = gv[gv['F_season'] == season]
        if len(season_data) > 0:
            plt.hist(season_data.ytime, bins=175, 
                    label=f'{season_label(season)} ({len(season_data)} events)', 
                    alpha=0.5, color=colors[season])
    
    plt.title("Day of Year Distribution of the Seasonal Heatwave Families", fontsize=16)
    plt.xlabel('Day of year', fontsize=12)
    plt.ylabel('Occurrences', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Add season boundaries
    season_boundaries = [59.5, 151.5, 243.5, 334.5]
    season_names_plot = ['Winter/Spring', 'Spring/Summer', 'Summer/Fall', 'Fall/Winter']
    
    for i, boundary in enumerate(season_boundaries):
        plt.axvline(x=boundary, color='black', linestyle='--', alpha=0.5)
        if i < len(season_names_plot):
            plt.text(boundary + 5, plt.ylim()[1] * 0.9, season_names_plot[i], 
                    rotation=90, fontsize=10, alpha=0.7)
    
    os.makedirs('results/seasonal_clustering_step1', exist_ok=True)
    plt.savefig('results/seasonal_clustering_step1/day_of_year_distribution.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_seasonal_stats_table(cpv, gv):
    """Create comprehensive statistics table for each season"""
    seasonal_stats = []
    
    for season in range(4):
        season_heatwaves = cpv[cpv['F_season'] == season]
        season_events = gv[gv['F_season'] == season]
        
        if len(season_heatwaves) > 0:
            stats = {
                'Season': season_name(season),
                'Season_Code': season_label(season),
                'N_Heatwaves': len(season_heatwaves),
                'N_Events': len(season_events),
                'Avg_Duration': season_heatwaves['timespan'].mean(),
                'Max_Duration': season_heatwaves['timespan'].max(),
                'Avg_Magnitude': season_heatwaves['HWMId_magnitude'].mean(),
                'Max_Magnitude': season_heatwaves['HWMId_magnitude'].max(),
                'Avg_Spatial_Extent': season_heatwaves['n_unique_g_ids'].mean(),
                'Max_Spatial_Extent': season_heatwaves['n_unique_g_ids'].max(),
                'Avg_Peak_Temp': season_heatwaves['t2m_amax'].mean() if 't2m_amax' in season_heatwaves.columns else 0,
                'Max_Peak_Temp': season_heatwaves['t2m_amax'].max() if 't2m_amax' in season_heatwaves.columns else 0,
                'Peak_Day_Range': f"{season_events['ytime'].min()}-{season_events['ytime'].max()}"
            }
            seasonal_stats.append(stats)
    
    stats_df = pd.DataFrame(seasonal_stats)
    return stats_df

### Argparser ###
def make_argparser():
    parser = argparse.ArgumentParser(description='Analyze heatwaves by meteorological seasons')
    parser.add_argument("-d", "--data", 
                       help="Give the path to the original dataset to be worked on (gv file).",
                       type=str, required=True)
    parser.add_argument("--min_events", 
                       help="Minimum number of events per season to analyze", 
                       type=int, default=5)
    parser.add_argument("--create_dendrograms", 
                       help="Create hierarchical clustering dendrograms for each season",
                       action='store_true')
    return parser

### Main Script ###
if __name__ == "__main__":
    
    print("🌡️ Starting Seasonal Heatwave Analysis...")
    
    # Parse arguments
    parser = make_argparser()
    args = parser.parse_args()
    
    # Create results directory
    os.makedirs('results/seasonal_clustering_step1', exist_ok=True)
    
    print(f"📂 Loading data from {args.data}")
    
    # Load data
    gv = pd.read_csv(args.data)
    gv['time'] = pd.to_datetime(gv['time'])
    g = dg.DeepGraph(gv)
    
    print(f"✅ Loaded {len(gv)} extreme events")
    
    # Create supernodes from deep graph by partitioning the nodes by cp
    # Feature functions applied to the supernodes
    feature_funcs = {'time': [np.min, np.max],
                     't2m': [np.mean],
                     'magnitude': [np.sum],
                     'latitude': [np.mean],
                     'longitude': [np.mean], 
                     't2m': [np.max],
                     'ytime': [np.mean]}
    
    # Partition graph
    cpv, ggv = g.partition_nodes('cp', feature_funcs, return_gv=True)
    
    # Append necessary stuff
    cpv['g_ids'] = ggv['g_id'].apply(set)
    cpv['n_unique_g_ids'] = cpv['g_ids'].apply(len)
    cpv['dt'] = cpv['time_amax'] - cpv['time_amin']
    cpv['timespan'] = cpv.dt.dt.days + 1
    cpv.rename(columns={'magnitude_sum': 'HWMId_magnitude'}, inplace=True)
    
    print(f"✅ Created {len(cpv)} heatwave summaries")
    print("🌍 Assigning meteorological seasons...")
    
    # Assign seasons to individual events
    gv['F_season'] = gv['ytime'].apply(get_meteorological_season)
    
    # Assign seasons to heatwaves based on mean day of year
    cpv['F_season'] = cpv['ytime_mean'].apply(get_meteorological_season)
    
    # Update the DeepGraph with season information
    g.v['F_season'] = gv['F_season']
    
    # Get present seasons
    seasons_present = sorted(gv['F_season'].unique())
    seasons_present = [s for s in seasons_present if s >= 0]  # Remove error cases
    
    print(f"📊 Found heatwaves in {len(seasons_present)} seasons: {[season_label(s) for s in seasons_present]}")
    
    # Print season distribution
    season_counts = gv['F_season'].value_counts().sort_index()
    for season in seasons_present:
        count = season_counts.get(season, 0)
        hw_count = len(cpv[cpv['F_season'] == season])
        print(f"   {season_label(season)}: {count} events, {hw_count} heatwaves")
    
    # Create seasonal distribution plot
    print("📈 Creating seasonal distribution plots...")
    plot_seasonal_distribution(gv, seasons_present)
    
    # Create comprehensive statistics
    print("📋 Computing seasonal statistics...")
    seasonal_stats = create_seasonal_stats_table(cpv, gv)
    seasonal_stats.to_csv('results/seasonal_clustering_step1/seasonal_statistics.csv', index=False)
    print("✅ Seasonal statistics saved to seasonal_statistics.csv")
    
    # Display key statistics
    print("\n📊 SEASONAL HEATWAVE STATISTICS:")
    print("=" * 60)
    for _, row in seasonal_stats.iterrows():
        print(f"{row['Season']} ({row['Season_Code']}):")
        print(f"  Heatwaves: {row['N_Heatwaves']}")
        print(f"  Events: {row['N_Events']}")
        print(f"  Avg Duration: {row['Avg_Duration']:.1f} days")
        print(f"  Avg Magnitude: {row['Avg_Magnitude']:.2f}")
        if row['Max_Peak_Temp'] > 0:
            print(f"  Peak Temperature: {row['Max_Peak_Temp']:.1f}°C")
        print()
    
    # Plot families on maps
    print("🗺️ Creating seasonal maps...")
    
    # Feature functions for mapping
    def n_cp_nodes(cp):
        return len(cp.unique())
    
    feature_funcs_map = {'magnitude': [np.sum],
                        'latitude': np.min,
                        'longitude': np.min,
                        'cp': n_cp_nodes}
    
    # Create season-location intersection graph
    fgv = g.partition_nodes(['F_season', 'g_id'], feature_funcs=feature_funcs_map)
    fgv.rename(columns={'cp_n_cp_nodes': 'n_cp_nodes', 
                       'longitude_amin': 'longitude',
                       'latitude_amin': 'latitude'}, inplace=True)
    
    plot_families(len(seasons_present), fgv, gv, 'Seasonal_Analysis')
    
    # HIERARCHICAL CLUSTERING - Create dendrograms for each season
    if args.create_dendrograms:
        print("🌳 Creating hierarchical clustering dendrograms...")
        
        for season in seasons_present:
            season_name_str = season_name(season)
            print(f"   Processing {season_name_str}...")
            
            # Filter to current season
            gvv = dg.DeepGraph(gv)
            gvv.filter_by_values_v('F_season', season)
            gv_season = gvv.v
            
            cpv_season = cpv[cpv['F_season'] == season]
            
            if len(cpv_season) < args.min_events:
                print(f"   Skipping {season_name_str}: only {len(cpv_season)} heatwaves (minimum: {args.min_events})")
                continue
            
            try:
                # Create DeepGraph for heatwaves in this season
                cpg = dg.DeepGraph(cpv_season)
                
                # Create edges based on spatial-temporal intersection
                cpg.create_edges(connectors=[cs.cp_node_intersection, 
                                           cs.cp_intersection_strength],
                               no_transfer_rs=['intsec_card'],
                               logfile=f'create_cpe_season_{season}',
                               step_size=1e7)
                
                if len(cpg.e) == 0:
                    print(f"   No edges found for {season_name_str}, skipping dendrogram")
                    continue
                
                # Create distance matrix
                dv = 1 - cpg.e.intsec_strength.values
                
                # Create linkage matrix
                lm = linkage(dv, method='average', metric='euclidean')
                del dv
                
                # Create dendrogram
                plt.figure(figsize=(60, 40))
                plt.title(f'UPGMA Heatwave Clustering - {season_name_str}')
                plt.xlabel('heatwave index')
                plt.ylabel('distance')
                
                dendrogram(lm,
                          leaf_rotation=90.,
                          leaf_font_size=8.)
                
                plt.savefig(f'results/seasonal_clustering_step1/dendrogram_{season_name_str}.png', 
                           dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"   ✅ Dendrogram saved for {season_name_str}")
                
            except Exception as e:
                print(f"   ❌ Error creating dendrogram for {season_name_str}: {e}")
                continue
    
    # Save seasonal datasets
    print("💾 Saving seasonal datasets...")
    
    for season in seasons_present:
        season_name_str = season_name(season)
        
        # Filter data for this season
        cpv_season = cpv[cpv['F_season'] == season]
        gv_season = gv[gv['F_season'] == season]
        
        # Save files with F_season column
        cpv_season.to_csv(f'results/seasonal_clustering_step1/cpv_{season_name_str}.csv', index=False)
        gv_season.to_csv(f'results/seasonal_clustering_step1/gv_{season_name_str}.csv', index=False)
        
        print(f"   ✅ {season_name_str}: {len(cpv_season)} heatwaves, {len(gv_season)} events")
    
    # Save combined dataset with season labels
    gv.to_csv('results/seasonal_clustering_step1/gv_with_seasons.csv', index=False)
    cpv.to_csv('results/seasonal_clustering_step1/cpv_with_seasons.csv', index=False)
    
    print("\n🎉 SEASONAL ANALYSIS COMPLETED!")
    print("📁 Results saved in: results/seasonal_clustering_step1/")
    print("📊 Files created:")
    print("   - seasonal_statistics.csv (summary statistics)")
    print("   - day_of_year_distribution.png (temporal distribution)")
    print("   - cpv_[Season].csv (heatwave summaries by season)")
    print("   - gv_[Season].csv (events by season)")
    print("   - Seasonal_Analysis_Season_[N]_[Season].png (spatial maps)")
    if args.create_dendrograms:
        print("   - dendrogram_[Season].png (hierarchical clustering)")
    print("   - gv_with_seasons.csv (all events with season labels)")
    print("   - cpv_with_seasons.csv (all heatwaves with season labels)")
    print("\n✨ Ready for detailed seasonal analysis!")