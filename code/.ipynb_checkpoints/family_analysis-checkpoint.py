"""
Plot Family Analysis - No Subfamilies Found
Focus on comprehensive family analysis and comparisons
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

class FamilyPlotter:
    def __init__(self):
        """Initialize with family data only"""
        # Use clustering_step1 for families (the original source)
        self.families_dir = "results/clustering_step1/"
        self.output_dir = "results/Advanced_Analysis/"
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.load_family_data()
    
    def load_family_data(self):
        """Load family data from clustering results"""
        print("=" * 60)
        print("HEATWAVE FAMILIES ANALYSIS (NO SUBFAMILIES)")
        print("=" * 60)
        print(f"\nLoading family data from: {self.families_dir}")
        
        # Load family CPV files
        cpv_family_pattern = os.path.join(self.families_dir, "cpv_fam*.csv")
        cpv_family_files = glob.glob(cpv_family_pattern)
        
        print(f"Found {len(cpv_family_files)} CPV family files")
        
        # Load family CPV data
        self.cpv_families = {}
        for file in cpv_family_files:
            filename = os.path.basename(file)
            family_id = filename.replace('cpv_fam', '').replace('.csv', '')
            
            try:
                self.cpv_families[family_id] = pd.read_csv(file)
                print(f"✓ Loaded CPV Family {family_id}: {len(self.cpv_families[family_id])} events")
            except Exception as e:
                print(f"✗ Error loading {file}: {e}")
        
        self.prepare_family_data()
        
        print(f"\n📊 Data Summary:")
        print(f"   Families loaded: {len(self.cpv_families)}")
        print(f"   Total events: {sum(len(data) for data in self.cpv_families.values())}")
        
        return True
    
    def prepare_family_data(self):
        """Prepare data for analysis"""
        print("\nPreparing data for analysis...")
        
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
    
    def plot_comprehensive_family_analysis(self):
        """Create comprehensive family analysis plots"""
        print("\n=== COMPREHENSIVE FAMILY ANALYSIS ===")
        
        if not self.cpv_families:
            print("No family data available!")
            return
        
        # Combine all family data
        all_families = []
        for family_id, data in self.cpv_families.items():
            family_data = data.copy()
            family_data['family'] = f"Family {family_id}"
            all_families.append(family_data)
        
        combined_data = pd.concat(all_families, ignore_index=True)
        
        # Create comprehensive analysis figure
        fig = plt.figure(figsize=(20, 16))
        
        # Create grid layout
        gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
        
        # Plot 1: Family sizes (top left)
        ax1 = fig.add_subplot(gs[0, 0])
        family_sizes = combined_data['family'].value_counts().sort_index()
        bars = ax1.bar(range(len(family_sizes)), family_sizes.values, alpha=0.8, color='steelblue')
        ax1.set_xlabel('Family')
        ax1.set_ylabel('Number of Events')
        ax1.set_title('A) Events per Family', fontweight='bold')
        ax1.set_xticks(range(len(family_sizes)))
        ax1.set_xticklabels([f"Fam {i}" for i in family_sizes.index])
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        # Plot 2: Duration histograms by family (top middle)
        ax2 = fig.add_subplot(gs[0, 1])
        families = sorted(combined_data['family'].unique())
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        for i, family in enumerate(families):
            family_data = combined_data[combined_data['family'] == family]
            if 'duration' in family_data.columns:
                ax2.hist(family_data['duration'], alpha=0.7, label=family, 
                        bins=20, color=colors[i % len(colors)])
        ax2.set_xlabel('Duration (days)')
        ax2.set_ylabel('Frequency')
        ax2.set_title('B) Duration Distributions', fontweight='bold')
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Magnitude histograms by family (top right)
        ax3 = fig.add_subplot(gs[0, 2])
        for i, family in enumerate(families):
            family_data = combined_data[combined_data['family'] == family]
            if 'HWMId_magnitude' in family_data.columns:
                ax3.hist(family_data['HWMId_magnitude'], alpha=0.7, label=family,
                        bins=20, color=colors[i % len(colors)])
        ax3.set_xlabel('Heat Magnitude Index')
        ax3.set_ylabel('Frequency')
        ax3.set_title('C) Magnitude Distributions', fontweight='bold')
        ax3.legend(fontsize=8)
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Spatial extent comparison (top far right)
        ax4 = fig.add_subplot(gs[0, 3])
        if 'n_unique_g_ids' in combined_data.columns:
            sns.boxplot(data=combined_data, x='family', y='n_unique_g_ids', ax=ax4)
            ax4.set_xlabel('Family')
            ax4.set_ylabel('Spatial Extent (grid cells)')
            ax4.set_title('D) Spatial Extent by Family', fontweight='bold')
            ax4.tick_params(axis='x', rotation=45)
            ax4.grid(True, alpha=0.3)
        
        # Plot 5: Seasonal patterns (second row, left)
        ax5 = fig.add_subplot(gs[1, :2])  # Span 2 columns
        if 'start_doy' in combined_data.columns:
            for i, family in enumerate(families):
                family_data = combined_data[combined_data['family'] == family]
                ax5.hist(family_data['start_doy'], alpha=0.7, label=family,
                        bins=36, color=colors[i % len(colors)])
            ax5.set_xlabel('Start Day of Year')
            ax5.set_ylabel('Frequency')
            ax5.set_title('E) Seasonal Distribution Patterns', fontweight='bold')
            ax5.legend()
            ax5.grid(True, alpha=0.3)
            
            # Add season markers
            season_markers = [1, 80, 172, 266, 356]  # Approximate season boundaries
            season_labels = ['Summer', 'Autumn', 'Winter', 'Spring', 'Summer']
            for i, marker in enumerate(season_markers[:-1]):
                ax5.axvline(marker, color='red', linestyle='--', alpha=0.5)
                if i < len(season_labels)-1:
                    ax5.text(marker + 40, ax5.get_ylim()[1] * 0.9, season_labels[i], 
                            rotation=90, alpha=0.7)
        
        # Plot 6: Duration vs Magnitude scatter (second row, right)
        ax6 = fig.add_subplot(gs[1, 2:])  # Span 2 columns
        if 'duration' in combined_data.columns and 'HWMId_magnitude' in combined_data.columns:
            for i, family in enumerate(families):
                family_data = combined_data[combined_data['family'] == family]
                ax6.scatter(family_data['duration'], family_data['HWMId_magnitude'],
                           alpha=0.6, label=family, s=50, color=colors[i % len(colors)])
            ax6.set_xlabel('Duration (days)')
            ax6.set_ylabel('Heat Magnitude Index')
            ax6.set_title('F) Duration vs Magnitude Relationships', fontweight='bold')
            ax6.legend()
            ax6.grid(True, alpha=0.3)
        
        # Plot 7: Monthly distribution (third row, left)
        ax7 = fig.add_subplot(gs[2, :2])
        if 'start_month' in combined_data.columns:
            monthly_by_family = pd.crosstab(combined_data['start_month'], combined_data['family'])
            monthly_by_family.plot(kind='bar', ax=ax7, color=colors[:len(families)])
            ax7.set_xlabel('Month')
            ax7.set_ylabel('Number of Events')
            ax7.set_title('G) Monthly Distribution by Family', fontweight='bold')
            ax7.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rotation=45)
            ax7.legend(title='Family')
            ax7.grid(True, alpha=0.3)
        
        # Plot 8: Temporal trends (third row, right)
        ax8 = fig.add_subplot(gs[2, 2:])
        if 'year' in combined_data.columns:
            for i, family in enumerate(families):
                family_data = combined_data[combined_data['family'] == family]
                yearly_counts = family_data.groupby('year').size()
                ax8.plot(yearly_counts.index, yearly_counts.values, 
                        marker='o', label=family, color=colors[i % len(colors)], linewidth=2)
            ax8.set_xlabel('Year')
            ax8.set_ylabel('Number of Events')
            ax8.set_title('H) Temporal Trends by Family', fontweight='bold')
            ax8.legend()
            ax8.grid(True, alpha=0.3)
        
        # Plot 9: Statistical summary (bottom row)
        ax9 = fig.add_subplot(gs[3, :])
        
        # Create summary statistics table
        summary_stats = []
        for family_id, data in self.cpv_families.items():
            stats = {
                'Family': f'Family {family_id}',
                'Count': len(data),
                'Mean Duration': data['duration'].mean() if 'duration' in data.columns else 'N/A',
                'Mean Magnitude': data['HWMId_magnitude'].mean() if 'HWMId_magnitude' in data.columns else 'N/A',
                'Mean Spatial Extent': data['n_unique_g_ids'].mean() if 'n_unique_g_ids' in data.columns else 'N/A',
                'Std Duration': data['duration'].std() if 'duration' in data.columns else 'N/A',
                'Std Magnitude': data['HWMId_magnitude'].std() if 'HWMId_magnitude' in data.columns else 'N/A'
            }
            summary_stats.append(stats)
        
        summary_df = pd.DataFrame(summary_stats)
        
        # Plot summary as grouped bar chart
        if len(summary_df) > 0:
            x = np.arange(len(summary_df))
            width = 0.2
            
            # Normalize for comparison
            if isinstance(summary_df['Mean Duration'].iloc[0], (int, float)):
                norm_duration = summary_df['Mean Duration'] / summary_df['Mean Duration'].max()
                norm_magnitude = summary_df['Mean Magnitude'] / summary_df['Mean Magnitude'].max()
                norm_spatial = summary_df['Mean Spatial Extent'] / summary_df['Mean Spatial Extent'].max()
                
                ax9.bar(x - width, norm_duration, width, label='Duration (norm)', alpha=0.8, color='skyblue')
                ax9.bar(x, norm_magnitude, width, label='Magnitude (norm)', alpha=0.8, color='lightcoral')
                ax9.bar(x + width, norm_spatial, width, label='Spatial Extent (norm)', alpha=0.8, color='lightgreen')
                
                ax9.set_xlabel('Family')
                ax9.set_ylabel('Normalized Values')
                ax9.set_title('I) Summary Statistics Comparison (Normalized)', fontweight='bold')
                ax9.set_xticks(x)
                ax9.set_xticklabels(summary_df['Family'])
                ax9.legend()
                ax9.grid(True, alpha=0.3)
        
        plt.suptitle('Comprehensive Heatwave Family Analysis', fontsize=20, fontweight='bold', y=0.98)
        
        # Save the comprehensive plot
        output_file = os.path.join(self.output_dir, 'comprehensive_family_analysis.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")
        plt.show()
        
        # Print summary statistics
        print("\n📊 Family Summary Statistics:")
        print("="*60)
        for family_id, data in self.cpv_families.items():
            print(f"\nFamily {family_id}:")
            print(f"  Events: {len(data)}")
            if 'duration' in data.columns:
                print(f"  Duration: {data['duration'].mean():.1f} ± {data['duration'].std():.1f} days")
            if 'HWMId_magnitude' in data.columns:
                print(f"  Magnitude: {data['HWMId_magnitude'].mean():.2f} ± {data['HWMId_magnitude'].std():.2f}")
            if 'n_unique_g_ids' in data.columns:
                print(f"  Spatial Extent: {data['n_unique_g_ids'].mean():.1f} ± {data['n_unique_g_ids'].std():.1f} grid cells")
            if 'year' in data.columns:
                print(f"  Time Range: {data['year'].min()}-{data['year'].max()}")
        
        return combined_data
    
    def create_individual_family_plots(self):
        """Create detailed plots for each individual family"""
        print("\n=== CREATING INDIVIDUAL FAMILY PLOTS ===")
        
        for family_id, data in self.cpv_families.items():
            print(f"Creating detailed plot for Family {family_id}...")
            
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            fig.suptitle(f'Family {family_id} Detailed Analysis', fontsize=16, fontweight='bold')
            
            # Duration histogram
            if 'duration' in data.columns:
                axes[0,0].hist(data['duration'], bins=20, alpha=0.7, color='steelblue', edgecolor='black')
                axes[0,0].set_xlabel('Duration (days)')
                axes[0,0].set_ylabel('Frequency')
                axes[0,0].set_title('A) Duration Distribution')
                axes[0,0].grid(True, alpha=0.3)
            
            # Magnitude histogram
            if 'HWMId_magnitude' in data.columns:
                axes[0,1].hist(data['HWMId_magnitude'], bins=20, alpha=0.7, color='coral', edgecolor='black')
                axes[0,1].set_xlabel('Heat Magnitude Index')
                axes[0,1].set_ylabel('Frequency')
                axes[0,1].set_title('B) Magnitude Distribution')
                axes[0,1].grid(True, alpha=0.3)
            
            # Start day distribution
            if 'start_doy' in data.columns:
                axes[0,2].hist(data['start_doy'], bins=36, alpha=0.7, color='lightgreen', edgecolor='black')
                axes[0,2].set_xlabel('Start Day of Year')
                axes[0,2].set_ylabel('Frequency')
                axes[0,2].set_title('C) Seasonal Distribution')
                axes[0,2].grid(True, alpha=0.3)
            
            # Spatial extent
            if 'n_unique_g_ids' in data.columns:
                axes[1,0].hist(data['n_unique_g_ids'], bins=20, alpha=0.7, color='gold', edgecolor='black')
                axes[1,0].set_xlabel('Spatial Extent (grid cells)')
                axes[1,0].set_ylabel('Frequency')
                axes[1,0].set_title('D) Spatial Extent Distribution')
                axes[1,0].grid(True, alpha=0.3)
            
            # Duration vs Magnitude
            if 'duration' in data.columns and 'HWMId_magnitude' in data.columns:
                scatter = axes[1,1].scatter(data['duration'], data['HWMId_magnitude'], 
                                          alpha=0.6, s=50, c='purple')
                axes[1,1].set_xlabel('Duration (days)')
                axes[1,1].set_ylabel('Heat Magnitude Index')
                axes[1,1].set_title('E) Duration vs Magnitude')
                axes[1,1].grid(True, alpha=0.3)
            
            # Temporal evolution
            if 'year' in data.columns:
                yearly_counts = data.groupby('year').size()
                axes[1,2].plot(yearly_counts.index, yearly_counts.values, 'o-', color='darkred', linewidth=2)
                axes[1,2].set_xlabel('Year')
                axes[1,2].set_ylabel('Number of Events')
                axes[1,2].set_title('F) Temporal Evolution')
                axes[1,2].grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save individual family plot
            output_file = os.path.join(self.output_dir, f'family_{family_id}_detailed.png')
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {output_file}")
            plt.show()

def main():
    """Main plotting function"""
    # Initialize plotter
    plotter = FamilyPlotter()
    
    if not plotter.cpv_families:
        print("❌ No family data loaded!")
        return
    
    print("\n" + "="*60)
    print("GENERATING COMPREHENSIVE FAMILY PLOTS...")
    print("="*60)
    
    # Create comprehensive analysis
    combined_data = plotter.plot_comprehensive_family_analysis()
    
    # Create individual family plots
    plotter.create_individual_family_plots()
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print("="*60)
    print(f"All plots saved to: {plotter.output_dir}")
    print("\nGenerated files:")
    print("- comprehensive_family_analysis.png")
    for family_id in plotter.cpv_families.keys():
        print(f"- family_{family_id}_detailed.png")
    
    print("\n💡 Note: No subfamilies were found.")
    print("   To generate subfamilies, run clustering_step2.py on each family:")
    for family_id in plotter.cpv_families.keys():
        print(f"   python clustering_step2.py -d results/clustering_step1/gv_fam{family_id}.csv -u 4 -i {family_id}")

if __name__ == "__main__":
    main()