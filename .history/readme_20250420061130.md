# Final Report: Heatwave Analysis and Clustering

This repository contains scripts and tools for analyzing heatwave data, clustering heatwave events, and visualizing the results. The project leverages Python libraries such as `deepgraph`, `matplotlib`, and `pandas` to process and analyze large datasets.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Environment Setup](#environment-setup)
3. [Repository Structure](#repository-structure)
4. [How to Run the Scripts](#how-to-run-the-scripts)
5. [Input Data Requirements](#input-data-requirements)
6. [Output Files](#output-files)
7. [Dependencies](#dependencies)
8. [Troubleshooting](#troubleshooting)

---

## Project Overview

This project analyzes heatwave data to:
- Detect extreme heatwave events.
- Cluster heatwaves based on spatio-temporal characteristics.
- Visualize heatwave clusters and their distributions.

The scripts in this repository are designed to process large datasets, perform clustering using algorithms like K-Means and UPGMA, and generate insightful visualizations.

---

## Environment Setup

To ensure reproducibility, the project uses a `conda` environment. Follow these steps to set up the environment:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/final-report.git
   cd final-report

Here’s a detailed `README.md` file for your project:

```markdown
# Final Report: Heatwave Analysis and Clustering

This repository contains scripts and tools for analyzing heatwave data, clustering heatwave events, and visualizing the results. The project leverages Python libraries such as `deepgraph`, `matplotlib`, and `pandas` to process and analyze large datasets.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Environment Setup](#environment-setup)
3. [Repository Structure](#repository-structure)
4. [How to Run the Scripts](#how-to-run-the-scripts)
5. [Input Data Requirements](#input-data-requirements)
6. [Output Files](#output-files)
7. [Dependencies](#dependencies)
8. [Troubleshooting](#troubleshooting)

---

## Project Overview

This project analyzes heatwave data to:
- Detect extreme heatwave events.
- Cluster heatwaves based on spatio-temporal characteristics.
- Visualize heatwave clusters and their distributions.

The scripts in this repository are designed to process large datasets, perform clustering using algorithms like K-Means and UPGMA, and generate insightful visualizations.

---

## Environment Setup

To ensure reproducibility, the project uses a `conda` environment. Follow these steps to set up the environment:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/final-report.git
   cd final-report
   ```

2. **Create the Conda Environment**:
   Use the provided `environment.yml` file to create the environment:
   ```bash
   conda env create -f environment.yml
   ```

3. **Activate the Environment**:
   ```bash
   conda activate fr
   ```

4. **Verify the Installation**:
   Ensure all dependencies are installed:
   ```bash
   conda list
   ```

---

## Repository Structure

```
Final_Report/
├── code/
│   ├── clustering_step1.py       # Script for K-Means clustering
│   ├── clustering_step2.py       # Script for UPGMA clustering
│   ├── cluster_analysis.py       # Script for analyzing clusters
│   ├── plotting_results.py       # Script for visualizing results
│   ├── heatwaves_detection.py    # Script for detecting heatwaves
│   ├── con_sep.py                # Connectors and selectors for DeepGraph
│   ├── cppv.py                   # Create CPV datasets
│   ├── extr.py                   # Utility functions for temperature and percentiles
│   ├── plotting.py               # Plotting utilities
├── data/                         # Input datasets (not included in the repo)
├── results/                      # Output results and visualizations
├── environment.yml               # Conda environment file
└── README.md                     # Project documentation
```

---

## How to Run the Scripts

### 1. **Detect Heatwaves**
   Use the `heatwaves_detection.py` script to detect extreme heatwave events:
   ```bash
   python code/heatwaves_detection.py
   ```
   - **Input**: NetCDF dataset of temperature data.
   - **Output**: CSV files containing detected heatwave events.

### 2. **K-Means Clustering**
   Use the `clustering_step1.py` script to perform K-Means clustering:
   ```bash
   python code/clustering_step1.py -d data/heatwave_nodes.csv -k 4
   ```
   - **Arguments**:
     - `-d`: Path to the dataset.
     - `-k`: Number of clusters.
   - **Output**: Clustered data and visualizations.

### 3. **UPGMA Clustering**
   Use the `clustering_step2.py` script to perform UPGMA clustering:
   ```bash
   python code/clustering_step2.py -d data/heatwave_nodes.csv -u 5 -i 1
   ```
   - **Arguments**:
     - `-d`: Path to the dataset.
     - `-u`: Number of UPGMA clusters.
     - `-i`: Family number.
   - **Output**: Clustered data and visualizations.

### 4. **Cluster Analysis**
   Use the `cluster_analysis.py` script to analyze clusters:
   ```bash
   python code/cluster_analysis.py -d data/heatwave_nodes.csv -k 4
   ```
   - **Arguments**:
     - `-d`: Path to the dataset.
     - `-k`: Number of clusters.
   - **Output**: Cluster analysis results and visualizations.

### 5. **Plot Results**
   Use the `plotting_results.py` script to visualize heatwave data:
   ```bash
   python code/plotting_results.py -d data/heatwave_nodes.csv -cpv data/supernodes.csv -n 5 -b magnitude
   ```
   - **Arguments**:
     - `-d`: Path to the nodes dataset.
     - `-cpv`: Path to the supernodes table.
     - `-n`: Number of heatwaves to plot.
     - `-b`: Column to sort heatwaves by (e.g., `magnitude`).

---

## Input Data Requirements

- **Heatwave Nodes Dataset**:
  - CSV file containing heatwave node data.
  - Required columns: `cp`, `time`, `latitude`, `longitude`, `magnitude`, etc.

- **Supernodes Table**:
  - CSV file containing supernode data.
  - Required columns: `cp`, `time_amin`, `time_amax`, `HWMId_magnitude`, etc.

---

## Output Files

- **Heatwave Detection**:
  - CSV files containing detected heatwave events.

- **Clustering Results**:
  - CSV files with cluster labels.
  - Visualizations of clusters in circular space and day-of-year distributions.

- **Plots**:
  - PNG files of heatwave visualizations (e.g., `HWMID_global_1.png`).

---

## Dependencies

The project dependencies are listed in the environment.yml file. Key dependencies include:
- `deepgraph==0.2.4`
- `matplotlib==3.5.3`
- `numpy==1.22.0`
- `pandas==1.3.5`
- `basemap==1.3.2`
- `scikit-learn==1.0.2`

To recreate the environment:
```bash
conda env create -f environment.yml
```

---

## Troubleshooting

1. **Missing Dependencies**:
   If you encounter missing dependencies, ensure the environment is activated:
   ```bash
   conda activate fr
   ```

2. **Basemap Issues**:
   If `Basemap` fails to install, try:
   ```bash
   conda install -c conda-forge basemap
   ```

3. **File Not Found**:
   Ensure the input files are placed in the `data/` directory and paths are correctly specified.

4. **Visualization Errors**:
   If plots are not generated, check if the output directory exists:
   ```bash
   mkdir -p /path/to/output/directory
   ```

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contact

For questions or issues, please contact:
- **Name**: Ayush
- **Email**: ayush@example.com
```

### Key Features of the README:
1. **Comprehensive Instructions**: Detailed steps for running each script.
2. **Environment Setup**: Clear instructions for setting up the conda environment.
3. **Input and Output Details**: Explanation of required input files and expected outputs.
4. **Troubleshooting Section**: Common issues and their solutions.
5. **Repository Structure**: Overview of the project files and directories.

Let me know if you need further refinements!### Key Features of the README:
1. **Comprehensive Instructions**: Detailed steps for running each script.
2. **Environment Setup**: Clear instructions for setting up the conda environment.
3. **Input and Output Details**: Explanation of required input files and expected outputs.
4. **Troubleshooting Section**: Common issues and their solutions.
5. **Repository Structure**: Overview of the project files and directories.

Let me know if you need further refinements!