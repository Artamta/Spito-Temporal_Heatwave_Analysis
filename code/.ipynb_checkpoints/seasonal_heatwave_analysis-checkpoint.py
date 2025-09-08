# individual_characteristics_plots.py
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os

def make_argparser():
    parser = argparse.ArgumentParser(description="Create individual heatwave characteristics plots")
    parser.add_argument("-cpv", "--cpv", help="Path to the supernodes dataset", type=str, required=True)
    parser.add_argument("-o", "--output", help="Output directory", type=str, default="results/individual_characteristics")
    return parser

def main():
    args = make_argparser().parse_args()
    
    print("Loading data for individual characteristics plots...")
    cpv = pd.read_csv(args.cpv)
    os.makedirs(args.output, exist_ok=True)
    
    # Prepare data
    cpv['time_amin'] = pd.to_datetime(cpv['time_amin'])
    cpv['time_amax'] = pd.to_datetime(cpv['time_amax'])
    cpv['duration'] = (cpv['time_amax'] - cpv['time_amin']).dt.days + 1
    cpv['year'] = cpv['time_amin'].dt.year
    
    # Plot 1: Duration Distribution
    print("Creating duration distribution...")
    plt.figure(figsize=(12, 8))
    duration_data = cpv['duration'].dropna()
    plt.hist(duration_data, bins=30, alpha=0.8, edgecolor='black', color='skyblue')
    plt.xlabel('Duration (days)', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)
    plt.title('Heatwave Duration Distribution', fontsize=16, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # Add statistics
    mean_val = duration_data.mean()
    median_val = duration_data.median()
    plt.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.1f} days')
    plt.axvline(median_val, color='blue', linestyle='--', linewidth=2, label=f'Median: {median_val:.1f} days')
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.savefig(f'{args.output}/duration_distribution.png', dpi=300, bbox_inches='tight')
    print(f"Saved: {args.output}/duration_distribution.png")
    plt.show()
    
    # Plot 2: Magnitude Distribution
    if 'HWMId_magnitude' in cpv.columns:
        print("Creating magnitude distribution...")
        plt.figure(figsize=(12, 8))
        magnitude_data = cpv['HWMId_magnitude'].dropna()
        plt.hist(magnitude_data, bins=30, alpha=0.8, edgecolor='black', color='lightcoral')
        plt.xlabel('Heat Magnitude Index', fontsize=14)
        plt.ylabel('Frequency', fontsize=14)
        plt.title('Heatwave Intensity Distribution', fontsize=16, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        mean_val = magnitude_data.mean()
        median_val = magnitude_data.median()
        plt.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
        plt.axvline(median_val, color='blue', linestyle='--', linewidth=2, label=f'Median: {median_val:.2f}')
        plt.legend(fontsize=12)
        plt.tight_layout()
        plt.savefig(f'{args.output}/magnitude_distribution.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {args.output}/magnitude_distribution.png")
        plt.show()
    
    # Plot 3: Spatial Extent Distribution
    if 'n_unique_g_ids' in cpv.columns:
        print("Creating spatial extent distribution...")
        plt.figure(figsize=(12, 8))
        spatial_data = cpv['n_unique_g_ids'].dropna()
        plt.hist(spatial_data, bins=30, alpha=0.8, edgecolor='black', color='lightgreen')
        plt.xlabel('Spatial Extent (grid cells)', fontsize=14)
        plt.ylabel('Frequency', fontsize=14)
        plt.title('Heatwave Spatial Extent Distribution', fontsize=16, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        mean_val = spatial_data.mean()
        median_val = spatial_data.median()
        plt.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.1f}')
        plt.axvline(median_val, color='blue', linestyle='--', linewidth=2, label=f'Median: {median_val:.1f}')
        plt.legend(fontsize=12)
        plt.tight_layout()
        plt.savefig(f'{args.output}/spatial_extent_distribution.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {args.output}/spatial_extent_distribution.png")
        plt.show()
    
    # Plot 4: Duration vs Magnitude Scatter
    if 'HWMId_magnitude' in cpv.columns:
        print("Creating duration vs magnitude scatter plot...")
        plt.figure(figsize=(12, 8))
        plt.scatter(cpv['duration'], cpv['HWMId_magnitude'], alpha=0.6, s=50, color='purple')
        plt.xlabel('Duration (days)', fontsize=14)
        plt.ylabel('Heat Magnitude Index', fontsize=14)
        plt.title('Duration vs Intensity Relationship', fontsize=16, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        # Add correlation
        valid_data = cpv[['duration', 'HWMId_magnitude']].dropna()
        if len(valid_data) > 2:
            corr, p_value = stats.pearsonr(valid_data['duration'], valid_data['HWMId_magnitude'])
            plt.text(0.05, 0.95, f'Correlation: r = {corr:.3f}\np-value = {p_value:.3f}', 
                    transform=plt.gca().transAxes, bbox=dict(boxstyle="round", facecolor='white', alpha=0.8),
                    fontsize=12, verticalalignment='top')
        
        plt.tight_layout()
        plt.savefig(f'{args.output}/duration_vs_magnitude.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {args.output}/duration_vs_magnitude.png")
        plt.show()
    
    # Plot 5: Duration vs Spatial Extent Scatter
    if 'n_unique_g_ids' in cpv.columns:
        print("Creating duration vs spatial extent scatter plot...")
        plt.figure(figsize=(12, 8))
        plt.scatter(cpv['duration'], cpv['n_unique_g_ids'], alpha=0.6, s=50, color='orange')
        plt.xlabel('Duration (days)', fontsize=14)
        plt.ylabel('Spatial Extent (grid cells)', fontsize=14)
        plt.title('Duration vs Spatial Extent Relationship', fontsize=16, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        # Add correlation
        valid_data = cpv[['duration', 'n_unique_g_ids']].dropna()
        if len(valid_data) > 2:
            corr, p_value = stats.pearsonr(valid_data['duration'], valid_data['n_unique_g_ids'])
            plt.text(0.05, 0.95, f'Correlation: r = {corr:.3f}\np-value = {p_value:.3f}', 
                    transform=plt.gca().transAxes, bbox=dict(boxstyle="round", facecolor='white', alpha=0.8),
                    fontsize=12, verticalalignment='top')
        
        plt.tight_layout()
        plt.savefig(f'{args.output}/duration_vs_spatial_extent.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {args.output}/duration_vs_spatial_extent.png")
        plt.show()
    
    # Plot 6: Duration Categories
    print("Creating duration categories plot...")
    plt.figure(figsize=(12, 8))
    duration_categories = pd.cut(cpv['duration'], bins=[0, 3, 7, 14, 30, float('inf')], 
                                labels=['Short\n(1-3d)', 'Medium\n(4-7d)', 'Long\n(8-14d)', 
                                       'Very Long\n(15-30d)', 'Extreme\n(>30d)'])
    duration_counts = duration_categories.value_counts()
    bars = plt.bar(range(len(duration_counts)), duration_counts.values, 
                   color='skyblue', alpha=0.8, edgecolor='black')
    plt.xlabel('Duration Category', fontsize=14)
    plt.ylabel('Number of Events', fontsize=14)
    plt.title('Heatwave Duration Categories', fontsize=16, fontweight='bold')
    plt.xticks(range(len(duration_counts)), duration_counts.index)
    plt.grid(True, alpha=0.3)
    
    # Add percentage labels
    total = duration_counts.sum()
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{height}\n({height/total*100:.1f}%)', 
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{args.output}/duration_categories.png', dpi=300, bbox_inches='tight')
    print(f"Saved: {args.output}/duration_categories.png")
    plt.show()
    
    # Plot 7: Magnitude Categories (fixed)
    if 'HWMId_magnitude' in cpv.columns:
        print("Creating magnitude categories plot...")
        plt.figure(figsize=(10, 10))
        magnitude_data = cpv['HWMId_magnitude'].dropna()
        
        # Use quantiles to avoid duplicate edges
        percentiles = magnitude_data.quantile([0.2, 0.4, 0.6, 0.8]).values
        
        # Ensure unique bins
        unique_percentiles = []
        prev_val = magnitude_data.min()
        for p in percentiles:
            if p > prev_val:
                unique_percentiles.append(p)
                prev_val = p
        
        if len(unique_percentiles) >= 2:
            bins = [magnitude_data.min()] + unique_percentiles + [magnitude_data.max()]
            labels = ['Low', 'Moderate', 'High', 'Very High', 'Extreme'][:len(bins)-1]
            
            magnitude_categories = pd.cut(magnitude_data, bins=bins, labels=labels, include_lowest=True)
            magnitude_counts = magnitude_categories.value_counts()
            
            colors = plt.cm.Reds(np.linspace(0.3, 1, len(magnitude_counts)))
            plt.pie(magnitude_counts.values, labels=magnitude_counts.index, autopct='%1.1f%%', 
                    startangle=90, colors=colors, textprops={'fontsize': 12})
            plt.title('Heatwave Intensity Categories', fontsize=16, fontweight='bold')
            plt.savefig(f'{args.output}/magnitude_categories.png', dpi=300, bbox_inches='tight')
            print(f"Saved: {args.output}/magnitude_categories.png")
            plt.show()
        else:
            print("Skipping magnitude categories - insufficient unique values")
    
    print(f"\nAll individual characteristics plots saved to: {args.output}/")

if __name__ == "__main__":
    main()