# heatwave_frequency_map.py
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import os

def make_argparser():
    parser = argparse.ArgumentParser(description="Create heatwave frequency maps")
    parser.add_argument("-d", "--data", help="Path to the nodes dataset (gv file)", type=str, required=True)
    parser.add_argument("-o", "--output", help="Output directory", type=str, default="results/frequency_analysis")
    return parser

def main():
    args = make_argparser().parse_args()
    
    print("Loading data...")
    gv = pd.read_csv(args.data)
    os.makedirs(args.output, exist_ok=True)
    
    print("Creating heatwave frequency analysis...")
    print(f"Total data points: {len(gv)}")
    print(f"Unique locations: {gv['g_id'].nunique()}")
    print(f"Unique heatwave events: {gv['cp'].nunique()}")
    
    # Count heatwaves per grid cell
    frequency_data = gv.groupby(['g_id', 'latitude', 'longitude']).agg({
        'cp': 'nunique',  # Number of unique heatwave events
        'magnitude': ['count', 'sum', 'mean']  # Total days, total magnitude, avg magnitude
    }).reset_index()
    
    # Flatten column names
    frequency_data.columns = ['g_id', 'latitude', 'longitude', 'n_heatwaves', 
                             'total_days', 'total_magnitude', 'avg_magnitude']
    
    print(f"Processed {len(frequency_data)} unique locations")
    
    # Create comprehensive frequency maps
    fig = plt.figure(figsize=(24, 16))
    
    # Map projection settings
    kwds_basemap = {'llcrnrlon': gv.longitude.min() - 1,
                    'urcrnrlon': gv.longitude.max() + 1,
                    'llcrnrlat': gv.latitude.min() - 1,
                    'urcrnrlat': gv.latitude.max() + 1,
                    'resolution': 'c'}
    
    # Plot 1: Number of heatwave events
    ax1 = plt.subplot(2, 2, 1)
    m1 = Basemap(ax=ax1, **kwds_basemap)
    x1, y1 = m1(frequency_data.longitude.values, frequency_data.latitude.values)
    
    scatter1 = ax1.scatter(x1, y1, s=20, c=frequency_data.n_heatwaves.values, 
                          cmap='Reds', alpha=0.8, edgecolors='none')
    
    m1.drawcoastlines(linewidth=0.8, color='black')
    m1.drawcountries(linewidth=0.5, color='gray')
    m1.drawparallels(range(-50, 50, 10), linewidth=0.2, labels=[1,0,0,0])
    m1.drawmeridians(range(0, 360, 10), linewidth=0.2, labels=[0,0,0,1])
    ax1.set_title('A) Heatwave Event Frequency', fontsize=14, fontweight='bold')
    
    cb1 = plt.colorbar(scatter1, ax=ax1, fraction=0.046, pad=0.04, shrink=0.8)
    cb1.set_label('Number of Heatwave Events', fontsize=12)
    
    # Plot 2: Total heatwave days
    ax2 = plt.subplot(2, 2, 2)
    m2 = Basemap(ax=ax2, **kwds_basemap)
    x2, y2 = m2(frequency_data.longitude.values, frequency_data.latitude.values)
    
    scatter2 = ax2.scatter(x2, y2, s=20, c=frequency_data.total_days.values, 
                          cmap='OrRd', alpha=0.8, edgecolors='none')
    
    m2.drawcoastlines(linewidth=0.8, color='black')
    m2.drawcountries(linewidth=0.5, color='gray')
    m2.drawparallels(range(-50, 50, 10), linewidth=0.2, labels=[1,0,0,0])
    m2.drawmeridians(range(0, 360, 10), linewidth=0.2, labels=[0,0,0,1])
    ax2.set_title('B) Total Heatwave Days', fontsize=14, fontweight='bold')
    
    cb2 = plt.colorbar(scatter2, ax=ax2, fraction=0.046, pad=0.04, shrink=0.8)
    cb2.set_label('Total Heatwave Days', fontsize=12)
    
    # Plot 3: Total magnitude
    ax3 = plt.subplot(2, 2, 3)
    m3 = Basemap(ax=ax3, **kwds_basemap)
    x3, y3 = m3(frequency_data.longitude.values, frequency_data.latitude.values)
    
    scatter3 = ax3.scatter(x3, y3, s=20, c=frequency_data.total_magnitude.values, 
                          cmap='plasma', alpha=0.8, edgecolors='none')
    
    m3.drawcoastlines(linewidth=0.8, color='black')
    m3.drawcountries(linewidth=0.5, color='gray')
    m3.drawparallels(range(-50, 50, 10), linewidth=0.2, labels=[1,0,0,0])
    m3.drawmeridians(range(0, 360, 10), linewidth=0.2, labels=[0,0,0,1])
    ax3.set_title('C) Cumulative Heat Magnitude', fontsize=14, fontweight='bold')
    
    cb3 = plt.colorbar(scatter3, ax=ax3, fraction=0.046, pad=0.04, shrink=0.8)
    cb3.set_label('Total Heat Magnitude', fontsize=12)
    
    # Plot 4: Average magnitude
    ax4 = plt.subplot(2, 2, 4)
    m4 = Basemap(ax=ax4, **kwds_basemap)
    x4, y4 = m4(frequency_data.longitude.values, frequency_data.latitude.values)
    
    scatter4 = ax4.scatter(x4, y4, s=20, c=frequency_data.avg_magnitude.values, 
                          cmap='viridis', alpha=0.8, edgecolors='none')
    
    m4.drawcoastlines(linewidth=0.8, color='black')
    m4.drawcountries(linewidth=0.5, color='gray')
    m4.drawparallels(range(-50, 50, 10), linewidth=0.2, labels=[1,0,0,0])
    m4.drawmeridians(range(0, 360, 10), linewidth=0.2, labels=[0,0,0,1])
    ax4.set_title('D) Average Heat Intensity', fontsize=14, fontweight='bold')
    
    cb4 = plt.colorbar(scatter4, ax=ax4, fraction=0.046, pad=0.04, shrink=0.8)
    cb4.set_label('Average Heat Magnitude', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(f'{args.output}/heatwave_frequency_comprehensive.png', dpi=300, bbox_inches='tight')
    print(f"Saved: {args.output}/heatwave_frequency_comprehensive.png")
    plt.show()
    
    # Create summary statistics
    plt.figure(figsize=(15, 10))
    
    # Histogram subplots
    plt.subplot(2, 3, 1)
    plt.hist(frequency_data.n_heatwaves, bins=30, color='skyblue', alpha=0.8, edgecolor='black')
    plt.xlabel('Number of Events')
    plt.ylabel('Frequency')
    plt.title('Distribution of Event Counts')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 3, 2)
    plt.hist(frequency_data.total_days, bins=30, color='lightcoral', alpha=0.8, edgecolor='black')
    plt.xlabel('Total Days')
    plt.ylabel('Frequency')
    plt.title('Distribution of Total Days')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 3, 3)
    plt.hist(frequency_data.total_magnitude, bins=30, color='lightgreen', alpha=0.8, edgecolor='black')
    plt.xlabel('Total Magnitude')
    plt.ylabel('Frequency')
    plt.title('Distribution of Total Magnitude')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 3, 4)
    plt.scatter(frequency_data.n_heatwaves, frequency_data.total_days, alpha=0.6, s=30)
    plt.xlabel('Number of Events')
    plt.ylabel('Total Days')
    plt.title('Events vs Total Days')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 3, 5)
    plt.scatter(frequency_data.n_heatwaves, frequency_data.avg_magnitude, alpha=0.6, s=30)
    plt.xlabel('Number of Events')
    plt.ylabel('Average Magnitude')
    plt.title('Events vs Average Intensity')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 3, 6)
    plt.scatter(frequency_data.total_days, frequency_data.avg_magnitude, alpha=0.6, s=30)
    plt.xlabel('Total Days')
    plt.ylabel('Average Magnitude')
    plt.title('Duration vs Intensity')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{args.output}/frequency_statistics.png', dpi=300, bbox_inches='tight')
    print(f"Saved: {args.output}/frequency_statistics.png")
    plt.show()
    
    # Print detailed statistics
    print("\n" + "="*60)
    print("HEATWAVE FREQUENCY ANALYSIS SUMMARY")
    print("="*60)
    print(f"Total unique locations analyzed: {len(frequency_data)}")
    print(f"Total heatwave events: {gv['cp'].nunique()}")
    print(f"Total heatwave days: {len(gv)}")
    print()
    print("Event Frequency Statistics:")
    print(f"  Max events per location: {frequency_data.n_heatwaves.max()}")
    print(f"  Average events per location: {frequency_data.n_heatwaves.mean():.1f}")
    print(f"  Locations with >10 events: {(frequency_data.n_heatwaves > 10).sum()}")
    print()
    print("Duration Statistics:")
    print(f"  Max total days per location: {frequency_data.total_days.max()}")
    print(f"  Average total days per location: {frequency_data.total_days.mean():.1f}")
    print()
    print("Intensity Statistics:")
    print(f"  Max total magnitude per location: {frequency_data.total_magnitude.max():.2f}")
    print(f"  Average total magnitude per location: {frequency_data.total_magnitude.mean():.2f}")
    print(f"  Average intensity per location: {frequency_data.avg_magnitude.mean():.2f}")
    
    # Save summary data
    frequency_data.to_csv(f'{args.output}/frequency_summary_data.csv', index=False)
    print(f"\nSummary data saved to: {args.output}/frequency_summary_data.csv")

if __name__ == "__main__":
    main()