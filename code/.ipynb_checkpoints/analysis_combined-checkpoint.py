# analysis_combined.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
import os
import argparse

def make_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="Output directory", type=str, default="results/combined_analysis")
    return parser

def load_all_families():
    all_families = []
    
    for family_id in range(4):
        cpv_path = f"results/clustering_step1/cpv_fam{family_id}.csv"
        
        if os.path.exists(cpv_path):
            cpv = pd.read_csv(cpv_path)
            cpv['family_id'] = family_id
            cpv['time_amin'] = pd.to_datetime(cpv['time_amin'])
            cpv['time_amax'] = pd.to_datetime(cpv['time_amax'])
            cpv['duration'] = (cpv['time_amax'] - cpv['time_amin']).dt.days + 1
            cpv['start_year'] = cpv['time_amin'].dt.year
            cpv['start_month'] = cpv['time_amin'].dt.month
            cpv['start_doy'] = cpv['time_amin'].dt.dayofyear
            all_families.append(cpv)
        else:
            print(f"Family {family_id} not found!")
    
    return pd.concat(all_families, ignore_index=True) if all_families else None

def create_comparative_analysis(combined_data, output_dir):
    # Family Comparison Plots
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Duration comparison
    sns.boxplot(x='family_id', y='duration', data=combined_data, ax=axes[0,0])
    axes[0,0].set_title('Duration Distribution by Family')
    axes[0,0].set_ylabel('Duration (days)')
    
    # Magnitude comparison
    if 'HWMId_magnitude' in combined_data.columns:
        sns.boxplot(x='family_id', y='HWMId_magnitude', data=combined_data, ax=axes[0,1])
        axes[0,1].set_title('Magnitude Distribution by Family')
        axes[0,1].set_ylabel('Magnitude')
    
    # Seasonal distribution heatmap
    season_counts = combined_data.groupby(['family_id', 'start_month']).size().unstack(fill_value=0)
    sns.heatmap(season_counts, annot=True, cmap='YlOrRd', ax=axes[0,2])
    axes[0,2].set_title('Seasonal Distribution by Family')
    axes[0,2].set_ylabel('Family ID')
    axes[0,2].set_xlabel('Month')
    
    # Geographic distribution
    sns.scatterplot(x='longitude_mean', y='latitude_mean', hue='family_id', 
                   data=combined_data, alpha=0.6, ax=axes[1,0])
    axes[1,0].set_title('Geographic Distribution by Family')
    
    # Yearly trends
    yearly_counts = combined_data.groupby(['family_id', 'start_year']).size().unstack(fill_value=0)
    for family in range(4):
        if family in yearly_counts.index:
            axes[1,1].plot(yearly_counts.columns, yearly_counts.loc[family], 
                          label=f'Family {family}', marker='o')
    axes[1,1].set_title('Family Frequency Over Time')
    axes[1,1].set_xlabel('Year')
    axes[1,1].set_ylabel('Number of Events')
    axes[1,1].legend()
    
    # Spatial extent comparison
    if 'n_unique_g_ids' in combined_data.columns:
        sns.boxplot(x='family_id', y='n_unique_g_ids', data=combined_data, ax=axes[1,2])
        axes[1,2].set_title('Spatial Extent by Family')
        axes[1,2].set_ylabel('Grid Cells')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/family_comparison_comprehensive.png', dpi=300, bbox_inches='tight')
    plt.close()

def statistical_analysis(combined_data, output_dir):
    print("\n=== STATISTICAL ANALYSIS ===")
    
    # Family profiles
    family_profiles = combined_data.groupby('family_id').agg({
        'duration': ['count', 'mean', 'std', 'min', 'max'],
        'HWMId_magnitude': ['mean', 'std', 'min', 'max'] if 'HWMId_magnitude' in combined_data.columns else 'count',
        'start_month': lambda x: x.mode().iloc[0],
        'n_unique_g_ids': ['mean', 'std'] if 'n_unique_g_ids' in combined_data.columns else 'count',
        'latitude_mean': ['mean', 'std'],
        'longitude_mean': ['mean', 'std']
    }).round(3)
    
    print("Family Profiles:")
    print(family_profiles)
    
    # Save profiles
    family_profiles.to_csv(f'{output_dir}/family_profiles.csv')
    
    # ANOVA tests
    families = [combined_data[combined_data['family_id'] == i] for i in range(4)]
    
    # Duration ANOVA
    durations = [fam['duration'] for fam in families if len(fam) > 0]
    if len(durations) > 1:
        f_stat, p_val = stats.f_oneway(*durations)
        print(f"\nDuration ANOVA: F={f_stat:.3f}, p={p_val:.3f}")
    
    # Magnitude ANOVA
    if 'HWMId_magnitude' in combined_data.columns:
        magnitudes = [fam['HWMId_magnitude'] for fam in families if len(fam) > 0]
        if len(magnitudes) > 1:
            f_stat, p_val = stats.f_oneway(*magnitudes)
            print(f"Magnitude ANOVA: F={f_stat:.3f}, p={p_val:.3f}")

def main():
    args = make_argparser().parse_args()
    os.makedirs(args.output, exist_ok=True)
    
    print("Loading all families...")
    combined_data = load_all_families()
    
    if combined_data is not None:
        print(f"Loaded {len(combined_data)} total events from {combined_data['family_id'].nunique()} families")
        
        create_comparative_analysis(combined_data, args.output)
        statistical_analysis(combined_data, args.output)
        
        # Save combined dataset
        combined_data.to_csv(f'{args.output}/all_families_combined.csv', index=False)
        print(f"Analysis complete! Results saved to {args.output}/")
    else:
        print("No family data found!")

if __name__ == "__main__":
    main()