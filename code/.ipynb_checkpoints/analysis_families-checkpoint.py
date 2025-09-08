# analysis_families.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
import os
import argparse

def make_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="Output directory", type=str, default="results/family_analysis")
    return parser

def analyze_family(family_id, cpv_path, gv_path, output_dir):
    print(f"Analyzing Family {family_id}...")
    
    # Load data
    cpv = pd.read_csv(cpv_path)
    gv = pd.read_csv(gv_path)
    
    # Prepare data
    cpv['time_amin'] = pd.to_datetime(cpv['time_amin'])
    cpv['time_amax'] = pd.to_datetime(cpv['time_amax'])
    cpv['duration'] = (cpv['time_amax'] - cpv['time_amin']).dt.days + 1
    cpv['start_year'] = cpv['time_amin'].dt.year
    cpv['start_month'] = cpv['time_amin'].dt.month
    cpv['start_doy'] = cpv['time_amin'].dt.dayofyear
    
    # Create family output directory
    fam_dir = f"{output_dir}/family_{family_id}"
    os.makedirs(fam_dir, exist_ok=True)
    
    # Plot 1: Duration Distribution
    plt.figure(figsize=(10, 6))
    plt.hist(cpv['duration'], bins=20, alpha=0.7, edgecolor='black')
    plt.xlabel('Duration (days)')
    plt.ylabel('Frequency')
    plt.title(f'Family {family_id}: Duration Distribution')
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{fam_dir}/duration_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Plot 2: Magnitude Distribution
    if 'HWMId_magnitude' in cpv.columns:
        plt.figure(figsize=(10, 6))
        plt.hist(cpv['HWMId_magnitude'], bins=20, alpha=0.7, edgecolor='black', color='red')
        plt.xlabel('Heat Magnitude Index')
        plt.ylabel('Frequency')
        plt.title(f'Family {family_id}: Magnitude Distribution')
        plt.grid(True, alpha=0.3)
        plt.savefig(f'{fam_dir}/magnitude_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    # Plot 3: Seasonal Distribution
    plt.figure(figsize=(12, 6))
    monthly_counts = cpv['start_month'].value_counts().sort_index()
    plt.bar(monthly_counts.index, monthly_counts.values, alpha=0.7, color='green')
    plt.xlabel('Month')
    plt.ylabel('Number of Events')
    plt.title(f'Family {family_id}: Seasonal Distribution')
    plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{fam_dir}/seasonal_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Plot 4: Yearly Trends
    plt.figure(figsize=(12, 6))
    yearly_counts = cpv['start_year'].value_counts().sort_index()
    plt.plot(yearly_counts.index, yearly_counts.values, 'o-', linewidth=2)
    plt.xlabel('Year')
    plt.ylabel('Number of Events')
    plt.title(f'Family {family_id}: Temporal Trends')
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{fam_dir}/yearly_trends.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Plot 5: Spatial Extent Distribution
    if 'n_unique_g_ids' in cpv.columns:
        plt.figure(figsize=(10, 6))
        plt.hist(cpv['n_unique_g_ids'], bins=20, alpha=0.7, edgecolor='black', color='orange')
        plt.xlabel('Spatial Extent (grid cells)')
        plt.ylabel('Frequency')
        plt.title(f'Family {family_id}: Spatial Extent Distribution')
        plt.grid(True, alpha=0.3)
        plt.savefig(f'{fam_dir}/spatial_extent_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"Family {family_id} analysis complete!")
    return cpv, gv

def main():
    args = make_argparser().parse_args()
    os.makedirs(args.output, exist_ok=True)
    
    # Analyze each family
    all_families = []
    for family_id in range(4):
        cpv_path = f"results/clustering_step1/cpv_fam{family_id}.csv"
        gv_path = f"results/clustering_step1/gv_fam{family_id}.csv"
        
        if os.path.exists(cpv_path) and os.path.exists(gv_path):
            cpv, gv = analyze_family(family_id, cpv_path, gv_path, args.output)
            cpv['family_id'] = family_id
            all_families.append(cpv)
        else:
            print(f"Files for family {family_id} not found!")
    
    # Save combined results
    if all_families:
        combined = pd.concat(all_families, ignore_index=True)
        combined.to_csv(f'{args.output}/combined_families.csv', index=False)
        print(f"Combined data saved to {args.output}/combined_families.csv")

if __name__ == "__main__":
    main()