# research_analysis.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
import os
import argparse

def make_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="Output directory", type=str, default="results/research_analysis")
    return parser

def load_families_with_gv():
    all_data = []
    
    for family_id in range(4):
        cpv_path = f"results/clustering_step1/cpv_fam{family_id}.csv"
        gv_path = f"results/clustering_step1/gv_fam{family_id}.csv"
        
        if os.path.exists(cpv_path) and os.path.exists(gv_path):
            cpv = pd.read_csv(cpv_path)
            gv = pd.read_csv(gv_path)
            
            # Process CPV
            cpv['family_id'] = family_id
            cpv['time_amin'] = pd.to_datetime(cpv['time_amin'])
            cpv['time_amax'] = pd.to_datetime(cpv['time_amax'])
            cpv['duration'] = (cpv['time_amax'] - cpv['time_amin']).dt.days + 1
            cpv['start_year'] = cpv['time_amin'].dt.year
            cpv['start_month'] = cpv['time_amin'].dt.month
            
            # Process GV
            gv['family_id'] = family_id
            gv['time'] = pd.to_datetime(gv['time'])
            gv['year'] = gv['time'].dt.year
            gv['month'] = gv['time'].dt.month
            
            all_data.append({'cpv': cpv, 'gv': gv})
        else:
            print(f"Family {family_id} files not found!")
    
    return all_data

def climate_trends_analysis(family_data, output_dir):
    print("Analyzing climate trends...")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    for i, data in enumerate(family_data):
        cpv = data['cpv']
        family_id = cpv['family_id'].iloc[0]
        
        # Duration trends
        yearly_duration = cpv.groupby('start_year')['duration'].mean()
        if len(yearly_duration) > 2:
            slope, intercept, r_val, p_val, std_err = stats.linregress(yearly_duration.index, yearly_duration.values)
            axes[0,0].plot(yearly_duration.index, yearly_duration.values, 'o-', label=f'Family {family_id}')
            print(f"Family {family_id} Duration Trend: {slope:.3f} days/year (p={p_val:.3f})")
    
    axes[0,0].set_title('Duration Trends Over Time')
    axes[0,0].set_xlabel('Year')
    axes[0,0].set_ylabel('Mean Duration (days)')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    
    # Magnitude trends
    for i, data in enumerate(family_data):
        cpv = data['cpv']
        family_id = cpv['family_id'].iloc[0]
        
        if 'HWMId_magnitude' in cpv.columns:
            yearly_magnitude = cpv.groupby('start_year')['HWMId_magnitude'].mean()
            if len(yearly_magnitude) > 2:
                slope, intercept, r_val, p_val, std_err = stats.linregress(yearly_magnitude.index, yearly_magnitude.values)
                axes[0,1].plot(yearly_magnitude.index, yearly_magnitude.values, 's-', label=f'Family {family_id}')
                print(f"Family {family_id} Magnitude Trend: {slope:.3f} units/year (p={p_val:.3f})")
    
    axes[0,1].set_title('Magnitude Trends Over Time')
    axes[0,1].set_xlabel('Year')
    axes[0,1].set_ylabel('Mean Magnitude')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)
    
    # Frequency trends
    for i, data in enumerate(family_data):
        cpv = data['cpv']
        family_id = cpv['family_id'].iloc[0]
        
        yearly_count = cpv.groupby('start_year').size()
        if len(yearly_count) > 2:
            slope, intercept, r_val, p_val, std_err = stats.linregress(yearly_count.index, yearly_count.values)
            axes[1,0].plot(yearly_count.index, yearly_count.values, '^-', label=f'Family {family_id}')
            print(f"Family {family_id} Frequency Trend: {slope:.3f} events/year (p={p_val:.3f})")
    
    axes[1,0].set_title('Frequency Trends Over Time')
    axes[1,0].set_xlabel('Year')
    axes[1,0].set_ylabel('Number of Events')
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)
    
    # Spatial extent trends
    for i, data in enumerate(family_data):
        cpv = data['cpv']
        family_id = cpv['family_id'].iloc[0]
        
        if 'n_unique_g_ids' in cpv.columns:
            yearly_spatial = cpv.groupby('start_year')['n_unique_g_ids'].mean()
            if len(yearly_spatial) > 2:
                slope, intercept, r_val, p_val, std_err = stats.linregress(yearly_spatial.index, yearly_spatial.values)
                axes[1,1].plot(yearly_spatial.index, yearly_spatial.values, 'd-', label=f'Family {family_id}')
                print(f"Family {family_id} Spatial Extent Trend: {slope:.3f} cells/year (p={p_val:.3f})")
    
    axes[1,1].set_title('Spatial Extent Trends Over Time')
    axes[1,1].set_xlabel('Year')
    axes[1,1].set_ylabel('Mean Spatial Extent')
    axes[1,1].legend()
    axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/climate_trends_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def research_summary(family_data, output_dir):
    print("\n=== RESEARCH SUMMARY ===")
    
    summary = {
        'total_families': len(family_data),
        'family_characteristics': {}
    }
    
    for i, data in enumerate(family_data):
        cpv = data['cpv']
        gv = data['gv']
        family_id = cpv['family_id'].iloc[0]
        
        characteristics = {
            'n_events': len(cpv),
            'n_grid_points': len(gv),
            'analysis_period': f"{cpv['start_year'].min()}-{cpv['start_year'].max()}",
            'avg_duration': cpv['duration'].mean(),
            'avg_magnitude': cpv['HWMId_magnitude'].mean() if 'HWMId_magnitude' in cpv.columns else None,
            'peak_season': cpv['start_month'].mode().iloc[0] if len(cpv) > 0 else None,
            'geographic_center': {
                'lat': cpv['latitude_mean'].mean(),
                'lon': cpv['longitude_mean'].mean()
            },
            'spatial_extent_avg': cpv['n_unique_g_ids'].mean() if 'n_unique_g_ids' in cpv.columns else None
        }
        
        summary['family_characteristics'][f'family_{family_id}'] = characteristics
        
        print(f"\nFamily {family_id}:")
        print(f"  Events: {characteristics['n_events']}")
        print(f"  Period: {characteristics['analysis_period']}")
        print(f"  Avg Duration: {characteristics['avg_duration']:.1f} days")
        if characteristics['avg_magnitude']:
            print(f"  Avg Magnitude: {characteristics['avg_magnitude']:.2f}")
        print(f"  Peak Season: Month {characteristics['peak_season']}")
        print(f"  Geographic Center: {characteristics['geographic_center']['lat']:.2f}°, {characteristics['geographic_center']['lon']:.2f}°")
    
    # Save summary
    import json
    with open(f'{output_dir}/research_summary.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)

def main():
    args = make_argparser().parse_args()
    os.makedirs(args.output, exist_ok=True)
    
    print("Loading family data for research analysis...")
    family_data = load_families_with_gv()
    
    if family_data:
        print(f"Loaded {len(family_data)} families for analysis")
        
        climate_trends_analysis(family_data, args.output)
        research_summary(family_data, args.output)
        
        print(f"\nResearch analysis complete! Results saved to {args.output}/")
    else:
        print("No family data found!")

if __name__ == "__main__":
    main()