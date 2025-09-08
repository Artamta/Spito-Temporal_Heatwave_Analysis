"""
Comprehensive Plotting for Heatwave Families and Subfamilies Analysis
Reads from clustering_step1 (families) and clustering_step2 (subfamilies)
Saves results to results/Advanced_Analysis/
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import glob
import warnings
warnings.filterwarnings('ignore')

class FamilySubfamilyPlotter:
    def __init__(self):
        """Initialize with proper directory structure"""
        # Input directories
        self.families_dir = "results/clustering_step1/"      # Family CPV and GV files
        self.subfamilies_dir = "results/clustering_step2/"   # Subfamily CPV and GV files
        
        # Output directory
        self.output_dir = "results/Advanced_Analysis/"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Ask user for confirmation of paths
        self.confirm_paths()
        self.load_family_data()
    
    def confirm_paths(self):
        """Ask user to confirm the data paths"""
        print("=" * 60)
        print("HEATWAVE FAMILIES AND SUBFAMILIES PLOTTING ANALYSIS")
        print("=" * 60)
        print("\nConfirming data paths:")
        print(f"Families directory: {self.families_dir}")
        print(f"Subfamilies directory: {self.subfamilies_dir}")
        print(f"Output directory: {self.output_dir}")
        
        # Check if directories exist
        if not os.path.exists(self.families_dir):
            print(f"⚠️  Warning: Families directory '{self.families_dir}' not found!")
            custom_families = input("Enter families directory path: ").strip()
            if custom_families:
                self.families_dir = custom_families
        
        if not os.path.exists(self.subfamilies_dir):
            print(f"⚠️  Warning: Subfamilies directory '{self.subfamilies_dir}' not found!")
            custom_subfamilies = input("Enter subfamilies directory path: ").strip()
            if custom_subfamilies:
                self.subfamilies_dir = custom_subfamilies
        
        print(f"\n✓ Using families directory: {self.families_dir}")
        print(f"✓ Using subfamilies directory: {self.subfamilies_dir}")
        print(f"✓ Saving results to: {self.output_dir}")
        print()
    
    def load_family_data(self):
        """Load family and subfamily data from clustering results"""
        print("Loading family and subfamily data...")
        
        # Load family CPV files (cpv_famX.csv)
        cpv_family_pattern = os.path.join(self.families_dir, "cpv_fam*.csv")
        cpv_family_files = glob.glob(cpv_family_pattern)
        
        # Load family GV files (gv_famX.csv)  
        gv_family_pattern = os.path.join(self.families_dir, "gv_fam*.csv")
        gv_family_files = glob.glob(gv_family_pattern)
        
        print(f"Found {len(cpv_family_files)} CPV family files")
        print(f"Found {len(gv_family_files)} GV family files")
        
        # Load subfamily CPV files (cpv_famX_subY.csv or similar)
        cpv_subfamily_pattern = os.path.join(self.subfamilies_dir, "cpv_fam*_sub*.csv")
        cpv_subfamily_files = glob.glob(cpv_subfamily_pattern)
        
        # Also try alternative naming patterns
        if not cpv_subfamily_files:
            cpv_subfamily_pattern = os.path.join(self.subfamilies_dir, "cpv_fam*clust*.csv")
            cpv_subfamily_files = glob.glob(cpv_subfamily_pattern)
        
        print(f"Found {len(cpv_subfamily_files)} CPV subfamily files")
        
        # Load family CPV data
        self.cpv_families = {}
        for file in cpv_family_files:
            # Extract family ID from filename (e.g., cpv_fam0.csv -> 0)
            filename = os.path.basename(file)
            family_id = filename.replace('cpv_fam', '').replace('.csv', '')
            
            try:
                self.cpv_families[family_id] = pd.read_csv(file)
                print(f"✓ Loaded CPV Family {family_id}: {len(self.cpv_families[family_id])} events")
            except Exception as e:
                print(f"✗ Error loading {file}: {e}")
        
        # Load family GV data
        self.gv_families = {}
        for file in gv_family_files:
            filename = os.path.basename(file)
            family_id = filename.replace('gv_fam', '').replace('.csv', '')
            
            try:
                self.gv_families[family_id] = pd.read_csv(file)
                print(f"✓ Loaded GV Family {family_id}: {len(self.gv_families[family_id])} events")
            except Exception as e:
                print(f"✗ Error loading {file}: {e}")
        
        # Load subfamily CPV data
        self.cpv_subfamilies = {}
        for file in cpv_subfamily_files:
            filename = os.path.basename(file)
            
            # Parse subfamily filename (e.g., cpv_fam0_sub1.csv -> family=0, subfamily=1)
            try:
                if '_sub' in filename:
                    parts = filename.replace('cpv_fam', '').replace('.csv', '').split('_sub')
                    family_id = parts[0]
                    subfamily_id = parts[1]
                elif 'clust' in filename:
                    # Alternative naming: cpv_fam0clust1.csv
                    parts = filename.replace('cpv_fam', '').replace('.csv', '').split('clust')
                    family_id = parts[0]
                    subfamily_id = parts[1]
                else:
                    continue
                
                key = f"{family_id}_{subfamily_id}"
                self.cpv_subfamilies[key] = pd.read_csv(file)
                self.cpv_subfamilies[key]['family_id'] = family_id
                self.cpv_subfamilies[key]['subfamily_id'] = subfamily_id
                
                print(f"✓ Loaded CPV Family {family_id}, Subfamily {subfamily_id}: {len(self.cpv_subfamilies[key])} events")
                
            except Exception as e:
                print(f"✗ Error parsing {file}: {e}")
        
        # Prepare data for analysis
        self.prepare_family_data()
        
        # Summary
        print(f"\n📊 Data Summary:")
        print(f"   Families loaded: {len(self.cpv_families)}")
        print(f"   Subfamilies loaded: {len(self.cpv_subfamilies)}")
        
        if not self.cpv_families:
            print("⚠️  No family data loaded! Please check your paths.")
            return False
        
        return True
    
    def prepare_family_data(self):
        """Prepare data for analysis"""
        print("\nPreparing data for analysis...")
        
        # Prepare family data
        for family_id, data in self.cpv_families.items():
            try:
                # Convert time columns if they exist
                if 'time_amin' in data.columns:
                    data['time_amin'] = pd.to_datetime(data['time_amin'])
                    data['time_amax'] = pd.to_datetime(data['time_amax'])
                    data['start_doy'] = data['time_amin'].dt.dayofyear
                    data['end_doy'] = data['time_amax'].dt.dayofyear
                    data['start_month'] = data['time_amin'].dt.month
                    data['year'] = data['time_amin'].dt.year
                
                # Add family identifier
                data['family_id'] = family_id
                
                # Calculate duration if not present
                if 'duration' not in data.columns:
                    if 'timespan' in data.columns:
                        data['duration'] = data['timespan']
                    elif 'time_amin' in data.columns and 'time_amax' in data.columns:
                        data['duration'] = (data['time_amax'] - data['time_amin']).dt.days + 1
                
                print(f"✓ Prepared Family {family_id} data")
                
            except Exception as e:
                print(f"✗ Error preparing Family {family_id}: {e}")
        
        # Prepare subfamily data
        for key, data in self.cpv_subfamilies.items():
            try:
                # Convert time columns if they exist
                if 'time_amin' in data.columns:
                    data['time_amin'] = pd.to_datetime(data['time_amin'])
                    data['time_amax'] = pd.to_datetime(data['time_amax'])
                    data['start_doy'] = data['time_amin'].dt.dayofyear
                    data['end_doy'] = data['time_amax'].dt.dayofyear
                    data['start_month'] = data['time_amin'].dt.month
                    data['year'] = data['time_amin'].dt.year
                
                # Calculate duration if not present
                if 'duration' not in data.columns:
                    if 'timespan' in data.columns:
                        data['duration'] = data['timespan']
                    elif 'time_amin' in data.columns and 'time_amax' in data.columns:
                        data['duration'] = (data['time_amax'] - data['time_amin']).dt.days + 1
                
                print(f"✓ Prepared Subfamily {key} data")
                
            except Exception as e:
                print(f"✗ Error preparing Subfamily {key}: {e}")
    
    def plot_family_overview(self):
        """Plot overview of all families"""
        print("\n=== PLOTTING FAMILY OVERVIEW ===")
        
        if not self.cpv_families:
            print("No family data available for plotting!")
            return None
        
        # Combine all family data for overview
        all_families = []
        for family_id, data in self.cpv_families.items():
            family_data = data.copy()
            family_data['family'] = f"Family {family_id}"
            all_families.append(family_data)
        
        combined_data = pd.concat(all_families, ignore_index=True)
        
        # Create overview figure
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # Plot 1: Family sizes
        family_sizes = combined_data['family'].value_counts().sort_index()
        axes[0,0].bar(range(len(family_sizes)), family_sizes.values, alpha=0.7, color='skyblue')
        axes[0,0].set_xlabel('Family')
        axes[0,0].set_ylabel('Number of Events')
        axes[0,0].set_title('A) Events per Family')
        axes[0,0].set_xticks(range(len(family_sizes)))
        axes[0,0].set_xticklabels(family_sizes.index, rotation=45)
        axes[0,0].grid(True, alpha=0.3)
        
        # Plot 2: Duration distribution by family
        if 'duration' in combined_data.columns:
            families = sorted(combined_data['family'].unique())
            colors = plt.cm.Set1(np.linspace(0, 1, len(families)))
            
            for i, family in enumerate(families):
                family_data = combined_data[combined_data['family'] == family]
                axes[0,1].hist(family_data['duration'], alpha=0.6, 
                             label=family, bins=15, color=colors[i])
            axes[0,1].set_xlabel('Duration (days)')
            axes[0,1].set_ylabel('Frequency')
            axes[0,1].set_title('B) Duration Distribution by Family')
            axes[0,1].legend()
            axes[0,1].grid(True, alpha=0.3)
        
        # Plot 3: Magnitude distribution by family
        if 'HWMId_magnitude' in combined_data.columns:
            families = sorted(combined_data['family'].unique())
            colors = plt.cm.Set2(np.linspace(0, 1, len(families)))
            
            for i, family in enumerate(families):
                family_data = combined_data[combined_data['family'] == family]
                axes[0,2].hist(family_data['HWMId_magnitude'], alpha=0.6, 
                             label=family, bins=15, color=colors[i])
            axes[0,2].set_xlabel('Heat Magnitude Index')
            axes[0,2].set_ylabel('Frequency')
            axes[0,2].set_title('C) Magnitude Distribution by Family')
            axes[0,2].legend()
            axes[0,2].grid(True, alpha=0.3)
        
        # Plot 4: Start day distribution
        if 'start_doy' in combined_data.columns:
            axes[1,0].hist(combined_data['start_doy'], bins=36, alpha=0.7, 
                         color='lightcoral', edgecolor='black')
            axes[1,0].set_xlabel('Start Day of Year')
            axes[1,0].set_ylabel('Frequency')
            axes[1,0].set_title('D) Start Day Distribution (All Families)')
            axes[1,0].grid(True, alpha=0.3)
        
        # Plot 5: Family characteristics boxplot
        if len(families) > 1 and 'HWMId_magnitude' in combined_data.columns:
            sns.boxplot(data=combined_data, x='family', y='HWMId_magnitude', ax=axes[1,1])
            axes[1,1].set_xlabel('Family')
            axes[1,1].set_ylabel('Heat Magnitude Index')
            axes[1,1].set_title('E) Magnitude Distribution by Family')
            axes[1,1].tick_params(axis='x', rotation=45)
            axes[1,1].grid(True, alpha=0.3)
        
        # Plot 6: Spatial extent by family
        if 'n_unique_g_ids' in combined_data.columns:
            sns.boxplot(data=combined_data, x='family', y='n_unique_g_ids', ax=axes[1,2])
            axes[1,2].set_xlabel('Family')
            axes[1,2].set_ylabel('Spatial Extent (grid cells)')
            axes[1,2].set_title('F) Spatial Extent by Family')
            axes[1,2].tick_params(axis='x', rotation=45)
            axes[1,2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save to results directory
        output_file = os.path.join(self.output_dir, 'family_overview_analysis.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")
        plt.show()
        
        return combined_data
    
    def plot_individual_family_analysis(self, family_id):
        """Plot detailed analysis for a specific family"""
        if family_id not in self.cpv_families:
            print(f"Family {family_id} not found!")
            return
        
        print(f"\n=== PLOTTING FAMILY {family_id} DETAILED ANALYSIS ===")
        
        data = self.cpv_families[family_id]
        
        # Check for subfamilies
        family_subfamilies = {k: v for k, v in self.cpv_subfamilies.items() 
                            if v['family_id'].iloc[0] == family_id}
        
        has_subfamilies = len(family_subfamilies) > 0
        
        if has_subfamilies:
            print(f"Family {family_id} has {len(family_subfamilies)} subfamilies")
        
        # Create detailed family analysis
        fig, axes = plt.subplots(3, 3, figsize=(20, 15))
        fig.suptitle(f'Family {family_id} Detailed Analysis', fontsize=16, fontweight='bold')
        
        # Plot 1: Duration histogram
        if 'duration' in data.columns:
            axes[0,0].hist(data['duration'], bins=15, alpha=0.7, color='skyblue', edgecolor='black')
            axes[0,0].set_xlabel('Duration (days)')
            axes[0,0].set_ylabel('Frequency')
            axes[0,0].set_title(f'A) Duration Distribution - Family {family_id}')
            axes[0,0].grid(True, alpha=0.3)
        
        # Plot 2: Magnitude histogram
        if 'HWMId_magnitude' in data.columns:
            axes[0,1].hist(data['HWMId_magnitude'], bins=15, alpha=0.7, color='lightcoral', edgecolor='black')
            axes[0,1].set_xlabel('Heat Magnitude Index')
            axes[0,1].set_ylabel('Frequency')
            axes[0,1].set_title(f'B) Magnitude Distribution - Family {family_id}')
            axes[0,1].grid(True, alpha=0.3)
        
        # Plot 3: Start day distribution
        if 'start_doy' in data.columns:
            axes[0,2].hist(data['start_doy'], bins=36, alpha=0.7, color='lightgreen', edgecolor='black')
            axes[0,2].set_xlabel('Start Day of Year')
            axes[0,2].set_ylabel('Frequency')
            axes[0,2].set_title(f'C) Start Day Distribution - Family {family_id}')
            axes[0,2].grid(True, alpha=0.3)
        
        # Plot 4: End day distribution
        if 'end_doy' in data.columns:
            axes[1,0].hist(data['end_doy'], bins=36, alpha=0.7, color='gold', edgecolor='black')
            axes[1,0].set_xlabel('End Day of Year')
            axes[1,0].set_ylabel('Frequency')
            axes[1,0].set_title(f'D) End Day Distribution - Family {family_id}')
            axes[1,0].grid(True, alpha=0.3)
        
        # Plot 5: Spatial extent distribution
        if 'n_unique_g_ids' in data.columns:
            axes[1,1].hist(data['n_unique_g_ids'], bins=20, alpha=0.7, color='mediumpurple', edgecolor='black')
            axes[1,1].set_xlabel('Spatial Extent (grid cells)')
            axes[1,1].set_ylabel('Frequency')
            axes[1,1].set_title(f'E) Spatial Extent Distribution - Family {family_id}')
            axes[1,1].grid(True, alpha=0.3)
        
        # Plot 6: Duration vs Magnitude scatter
        if 'duration' in data.columns and 'HWMId_magnitude' in data.columns:
            scatter = axes[1,2].scatter(data['duration'], data['HWMId_magnitude'], 
                                      alpha=0.7, s=50, c='orange')
            axes[1,2].set_xlabel('Duration (days)')
            axes[1,2].set_ylabel('Heat Magnitude Index')
            axes[1,2].set_title(f'F) Duration vs Magnitude - Family {family_id}')
            axes[1,2].grid(True, alpha=0.3)
        
        # Plot 7: Year distribution
        if 'year' in data.columns:
            axes[2,0].hist(data['year'], bins=20, alpha=0.7, color='cyan', edgecolor='black')
            axes[2,0].set_xlabel('Year')
            axes[2,0].set_ylabel('Frequency')
            axes[2,0].set_title(f'G) Temporal Distribution - Family {family_id}')
            axes[2,0].grid(True, alpha=0.3)
        
        # Plot 8: Monthly distribution
        if 'start_month' in data.columns:
            month_counts = data['start_month'].value_counts().sort_index()
            axes[2,1].bar(month_counts.index, month_counts.values, alpha=0.7, color='pink')
            axes[2,1].set_xlabel('Start Month')
            axes[2,1].set_ylabel('Number of Events')
            axes[2,1].set_title(f'H) Monthly Distribution - Family {family_id}')
            axes[2,1].set_xticks(range(1, 13))
            axes[2,1].set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rotation=45)
            axes[2,1].grid(True, alpha=0.3)
        
        # Plot 9: Subfamily overview (if available)
        if has_subfamilies:
            subfamily_sizes = []
            subfamily_labels = []
            
            for key, subfamily_data in family_subfamilies.items():
                subfamily_id = subfamily_data['subfamily_id'].iloc[0]
                subfamily_sizes.append(len(subfamily_data))
                subfamily_labels.append(f"Sub {subfamily_id}")
            
            axes[2,2].pie(subfamily_sizes, labels=subfamily_labels, autopct='%1.1f%%', startangle=90)
            axes[2,2].set_title(f'I) Subfamily Distribution - Family {family_id}')
        else:
            # Summary statistics
            if 'duration' in data.columns and 'HWMId_magnitude' in data.columns:
                stats_data = {
                    'Duration': [data['duration'].mean(), data['duration'].std()],
                    'Magnitude': [data['HWMId_magnitude'].mean(), data['HWMId_magnitude'].std()],
                    'Spatial Extent': [data['n_unique_g_ids'].mean(), data['n_unique_g_ids'].std()]
                }
                
                metrics = list(stats_data.keys())
                means = [stats_data[m][0] for m in metrics]
                stds = [stats_data[m][1] for m in metrics]
                
                x_pos = np.arange(len(metrics))
                axes[2,2].bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7, color='lightblue')
                axes[2,2].set_xlabel('Metric')
                axes[2,2].set_ylabel('Mean ± Std')
                axes[2,2].set_title(f'I) Summary Statistics - Family {family_id}')
                axes[2,2].set_xticks(x_pos)
                axes[2,2].set_xticklabels(metrics, rotation=45)
                axes[2,2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save to results directory
        output_file = os.path.join(self.output_dir, f'family_{family_id}_detailed_analysis.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")
        plt.show()
    
    def plot_subfamily_analysis(self, family_id):
        """Plot analysis of subfamilies within a family"""
        print(f"\n=== PLOTTING SUBFAMILY ANALYSIS - FAMILY {family_id} ===")
        
        # Get subfamilies for this family
        family_subfamilies = {k: v for k, v in self.cpv_subfamilies.items() 
                            if v['family_id'].iloc[0] == family_id}
        
        if not family_subfamilies:
            print(f"No subfamilies found for Family {family_id}")
            return
        
        n_subfamilies = len(family_subfamilies)
        print(f"Found {n_subfamilies} subfamilies for Family {family_id}")
        
        # Create subplot comparison
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Subfamily Analysis - Family {family_id}', fontsize=16, fontweight='bold')
        
        # Prepare colors
        colors = plt.cm.Set1(np.linspace(0, 1, n_subfamilies))
        
        # Plot 1: Duration comparison
        for i, (key, subfamily_data) in enumerate(family_subfamilies.items()):
            subfamily_id = subfamily_data['subfamily_id'].iloc[0]
            if 'duration' in subfamily_data.columns:
                axes[0,0].hist(subfamily_data['duration'], alpha=0.6, 
                             label=f'Subfamily {subfamily_id}', bins=10, color=colors[i])
        
        axes[0,0].set_xlabel('Duration (days)')
        axes[0,0].set_ylabel('Frequency')
        axes[0,0].set_title(f'A) Duration Distribution - Family {family_id}')
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
        
        # Plot 2: Magnitude comparison
        for i, (key, subfamily_data) in enumerate(family_subfamilies.items()):
            subfamily_id = subfamily_data['subfamily_id'].iloc[0]
            if 'HWMId_magnitude' in subfamily_data.columns:
                axes[0,1].hist(subfamily_data['HWMId_magnitude'], alpha=0.6, 
                             label=f'Subfamily {subfamily_id}', bins=10, color=colors[i])
        
        axes[0,1].set_xlabel('Heat Magnitude Index')
        axes[0,1].set_ylabel('Frequency')
        axes[0,1].set_title(f'B) Magnitude Distribution - Family {family_id}')
        axes[0,1].legend()
        axes[0,1].grid(True, alpha=0.3)
        
        # Plot 3: Start day comparison
        for i, (key, subfamily_data) in enumerate(family_subfamilies.items()):
            subfamily_id = subfamily_data['subfamily_id'].iloc[0]
            if 'start_doy' in subfamily_data.columns:
                axes[1,0].hist(subfamily_data['start_doy'], alpha=0.6, 
                             label=f'Subfamily {subfamily_id}', bins=15, color=colors[i])
        
        axes[1,0].set_xlabel('Start Day of Year')
        axes[1,0].set_ylabel('Frequency')
        axes[1,0].set_title(f'C) Start Day Distribution - Family {family_id}')
        axes[1,0].legend()
        axes[1,0].grid(True, alpha=0.3)
        
        # Plot 4: Duration vs Magnitude scatter by subfamily
        for i, (key, subfamily_data) in enumerate(family_subfamilies.items()):
            subfamily_id = subfamily_data['subfamily_id'].iloc[0]
            if 'duration' in subfamily_data.columns and 'HWMId_magnitude' in subfamily_data.columns:
                axes[1,1].scatter(subfamily_data['duration'], subfamily_data['HWMId_magnitude'], 
                                alpha=0.7, label=f'Subfamily {subfamily_id}', s=50, c=[colors[i]])
        
        axes[1,1].set_xlabel('Duration (days)')
        axes[1,1].set_ylabel('Heat Magnitude Index')
        axes[1,1].set_title(f'D) Duration vs Magnitude - Family {family_id}')
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save to results directory
        output_file = os.path.join(self.output_dir, f'subfamily_analysis_family_{family_id}.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")
        plt.show()
        
        # Print subfamily statistics
        print(f"\nSubfamily Statistics for Family {family_id}:")
        for key, subfamily_data in family_subfamilies.items():
            subfamily_id = subfamily_data['subfamily_id'].iloc[0]
            stats = {
                'Count': len(subfamily_data),
                'Mean Duration': subfamily_data['duration'].mean() if 'duration' in subfamily_data.columns else 'N/A',
                'Mean Magnitude': subfamily_data['HWMId_magnitude'].mean() if 'HWMId_magnitude' in subfamily_data.columns else 'N/A',
                'Mean Spatial Extent': subfamily_data['n_unique_g_ids'].mean() if 'n_unique_g_ids' in subfamily_data.columns else 'N/A'
            }
            print(f"  Subfamily {subfamily_id}: {stats}")

def main():
    """Main plotting function"""
    # Initialize plotter (will ask for paths if needed)
    plotter = FamilySubfamilyPlotter()
    
    # Check if data was loaded successfully
    if not plotter.cpv_families:
        print("❌ No data loaded. Please check your directory paths.")
        return
    
    print("\n" + "="*60)
    print("GENERATING PLOTS...")
    print("="*60)
    
    # Plot overview of all families
    combined_data = plotter.plot_family_overview()
    
    # Plot detailed analysis for each family
    for family_id in plotter.cpv_families.keys():
        plotter.plot_individual_family_analysis(family_id)
        plotter.plot_subfamily_analysis(family_id)
    
    print("\n" + "="*60)
    print("PLOTTING COMPLETE!")
    print("="*60)
    print(f"All plots saved to: {plotter.output_dir}")
    print("\nGenerated files:")
    print("- family_overview_analysis.png")
    for family_id in plotter.cpv_families.keys():
        print(f"- family_{family_id}_detailed_analysis.png")
        print(f"- subfamily_analysis_family_{family_id}.png")

if __name__ == "__main__":
    main()