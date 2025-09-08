# analysis_sub_fam.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import argparse

def make_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="Output directory", type=str, default="results/subfamily_analysis")
    return parser

def analyze_subfamily(family_id, cpv_path, gv_path, output_dir):
    print(f"Analyzing Subfamily Family {family_id}...")
    
    # Load data
    cpv = pd.read_csv(cpv_path)
    gv = pd.read_csv(gv_path)
    
    # Prepare data
    cpv['time_amin'] = pd.to_datetime(cpv['time_amin'])
    cpv['time_amax'] = pd.to_datetime(cpv['time_amax'])
    cpv['duration'] = (cpv['time_amax'] - cpv['time_amin']).dt.days + 1
    cpv['start_year'] = cpv['time_amin'].dt.year
    cpv['start_month'] = cpv['time_amin'].dt.month
    
    # Create subfamily output directory
    subfam_dir = f"{output_dir}/subfamily_fam{family_id}"
    os.makedirs(subfam_dir, exist_ok=True)
    
    # Check if subfamily column exists
    if 'subfamily' in cpv.columns:
        subfamilies = cpv['subfamily'].unique()
        n_subfam = len(subfamilies)
        
        # Plot 1: Subfamily Duration Comparison
        plt.figure(figsize=(12, 6))
        sns.boxplot(x='subfamily', y='duration', data=cpv)
        plt.title(f'Family {family_id}: Duration by Subfamily')
        plt.xlabel('Subfamily')
        plt.ylabel('Duration (days)')
        plt.savefig(f'{subfam_dir}/duration_by_subfamily.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 2: Subfamily Magnitude Comparison
        if 'HWMId_magnitude' in cpv.columns:
            plt.figure(figsize=(12, 6))
            sns.boxplot(x='subfamily', y='HWMId_magnitude', data=cpv)
            plt.title(f'Family {family_id}: Magnitude by Subfamily')
            plt.xlabel('Subfamily')
            plt.ylabel('Magnitude')
            plt.savefig(f'{subfam_dir}/magnitude_by_subfamily.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # Plot 3: Subfamily Spatial Distribution
        plt.figure(figsize=(12, 8))
        sns.scatterplot(x='longitude_mean', y='latitude_mean', hue='subfamily', data=cpv, s=60)
        plt.title(f'Family {family_id}: Geographic Distribution by Subfamily')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.savefig(f'{subfam_dir}/spatial_by_subfamily.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 4: Subfamily Seasonal Patterns
        plt.figure(figsize=(14, 8))
        seasonal_data = cpv.groupby(['subfamily', 'start_month']).size().unstack(fill_value=0)
        sns.heatmap(seasonal_data, annot=True, cmap='YlOrRd', fmt='d')
        plt.title(f'Family {family_id}: Seasonal Distribution by Subfamily')
        plt.xlabel('Month')
        plt.ylabel('Subfamily')
        plt.savefig(f'{subfam_dir}/seasonal_by_subfamily.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Subfamily analysis for Family {family_id} complete! Found {n_subfam} subfamilies.")
    else:
        print(f"No subfamily column found for Family {family_id}")

def main():
    args = make_argparser().parse_args()
    os.makedirs(args.output, exist_ok=True)
    
    # Analyze each family's subfamilies
    for family_id in range(4):
        cpv_path = f"results/clustering_step2/cpv_fam{family_id}.csv"
        gv_path = f"results/clustering_step2/gv_fam{family_id}.csv"
        
        if os.path.exists(cpv_path) and os.path.exists(gv_path):
            analyze_subfamily(family_id, cpv_path, gv_path, args.output)
        else:
            print(f"Subfamily files for family {family_id} not found!")

if __name__ == "__main__":
    main()