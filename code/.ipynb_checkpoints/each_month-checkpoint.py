import argparse
import numpy as np
import pandas as pd
import deepgraph as dg
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from scipy.interpolate import griddata
import matplotlib.cm as cm

def make_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Path to the nodes dataset to be worked on.", type=str)
    parser.add_argument("-cpv", "--cpv", help="Path to the supernodes table.", type=str)
    parser.add_argument("-b", "--by", help="Column name by which the heatwaves should be sorted.", type=str)
    return parser

def plot_combined_heatwaves_for_each_month(cpv, gv, by, output_dir):
    """
    Plots combined heatwaves for each month (January to December) across 40 years.
    """
    # Ensure time_amin is in datetime format and extract the month
    cpv['time_amin'] = pd.to_datetime(cpv['time_amin'])
    cpv['month'] = cpv['time_amin'].dt.month  # Extract month from time_amin

    # Iterate over each month (1 to 12)
    for month in range(1, 13):
        print(f"\nProcessing combined heatwaves for month: {month} (across 40 years)")
        monthly_cpv = cpv[cpv['month'] == month]  # Filter heatwaves for the current month

        if monthly_cpv.empty:
            print(f"No heatwaves found for month {month}. Skipping...")
            continue

        try:
            # Combine all heatwaves for the current month
            combined_gv = gv[gv.cp.isin(monthly_cpv.cp)]

            # Create a DeepGraph object for the combined data
            ggg = dg.DeepGraph(combined_gv)

            # Feature functions
            def n_cp_nodes(cp):
                return len(cp.unique())

            feature_funcs = {'magnitude': [np.sum],
                             'latitude': np.min,
                             'longitude': np.min,
                             'cp': n_cp_nodes}

            # Create family-g_id intersection graph
            fgv = ggg.partition_nodes(['g_id'], feature_funcs=feature_funcs)

            # Ensure proper renaming of columns
            fgv.rename(columns={'cp_n_cp_nodes': 'n_cp_nodes',
                                'longitude_amin': 'longitude',  # Fix column name
                                'latitude_amin': 'latitude'}, inplace=True)

            # Debugging: Check columns in fgv
            print(f"Columns in fgv for month {month}: {fgv.columns}")

            # Prepare data for pcolormesh
            lon = fgv['longitude'].values
            lat = fgv['latitude'].values
            data = fgv['magnitude_sum'].values  # Replace with the appropriate data column

            # Aggregate data to ensure grid consistency
            grid_data = pd.DataFrame({'latitude': lat, 'longitude': lon, 'data': data})
            aggregated_data = grid_data.groupby(['latitude', 'longitude']).mean().reset_index()

            # Extract the aggregated values
            lat = aggregated_data['latitude'].values
            lon = aggregated_data['longitude'].values
            data = aggregated_data['data'].values

            # Create the grid
            lon_grid, lat_grid = np.meshgrid(np.unique(lon), np.unique(lat))

            # Interpolate missing values in the data grid
            points = np.array([aggregated_data['latitude'], aggregated_data['longitude']]).T
            values = aggregated_data['data']
            data_grid = griddata(points, values, (lat_grid, lon_grid), method='linear')

            # Replace any remaining NaN values with 0 (optional)
            data_grid = np.nan_to_num(data_grid, nan=0.0)

            # Set a colormap that handles NaN values
            cmap = cm.get_cmap('viridis_r')  # Compatible with older Matplotlib versions
            cmap.set_bad(color='gray')

            # Configure map projection
            fig, ax = plt.subplots(figsize=(12, 8))
            m = Basemap(projection='cyl',
                        llcrnrlon=gv.longitude.min() - 1, urcrnrlon=gv.longitude.max() + 1,
                        llcrnrlat=gv.latitude.min() - 1, urcrnrlat=gv.latitude.max() + 1,
                        resolution='l', ax=ax)
            m.drawcoastlines(linewidth=.8, zorder=10)
            m.drawparallels(range(-50, 50, 20), linewidth=.2)
            m.drawmeridians(range(0, 360, 20), linewidth=.2)

            # Plot the data using pcolormesh
            pcm = m.pcolormesh(lon_grid, lat_grid, data_grid, cmap=cmap, shading='auto')

            # Add colorbar
            cbar = m.colorbar(pcm, location='right', pad=0.05)
            cbar.set_label('Number of Heat Wave Days', fontsize=15)

            # Add title
            ax.set_title(f'Combined Heatwaves in Month {month} (Across 40 Years)', fontsize=16)

            # Save the plot to the updated directory
            output_path = f"{output_dir}/combined_heatwaves_month_{month}.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved for month {month}: {output_path}")
            plt.close(fig)

        except Exception as e:
            print(f"Error processing combined heatwaves for month {month}: {e}")

# Main script
if __name__ == "__main__":
    parser = make_argparser()
    args = parser.parse_args()
    cpv = pd.read_csv(args.cpv)
    gv = pd.read_csv(args.data)
    by = args.by
    output_dir = "results/Monthly_Heatwaves"

    # Call the function to plot combined heatwaves for each month
    plot_combined_heatwaves_for_each_month(cpv, gv, by, output_dir)
