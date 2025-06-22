"""
Script: run_wq_import_pipeline.py

Description:
    This script orchestrates the execution of all water quality (WQ) data import scripts,
    creating standardized parquet files for downstream use in plotting and analysis.

Key Features:
    - Deletes any existing WQ parquet output directory before rebuilding
    - Executes a sequence of WQ import scripts
    - Modular design makes adding new import scripts straightforward
    - Provides logging output for script status

Output:
    Updated parquet files saved to Data/data-warehouse/parquet/WQ/

Requirements:
    - Python 3.7+
    - All required libraries for each script must be satisfied within the active environment

Author: Brendan Busch
"""

import subprocess
import os
import shutil

# Remove existing WQ parquet output directory
wq_output_dir = "Data/data-warehouse/parquet/WQ"
if os.path.exists(wq_output_dir):
    shutil.rmtree(wq_output_dir)
    print(f"Removed existing WQ parquet output directory: {wq_output_dir}")

# Define the scripts to run
pipeline_scripts = [
    "import_360E_logger_data.py",
    "import_HGE_WQ_data.py",
    "import_HGE_MSc_Salinity.py"
]

def run_pipeline():
    print("Running Water Quality Import Pipeline...\n")
    for script in pipeline_scripts:
        script_path = os.path.join(os.path.dirname(__file__), script)
        print(f"▶ Running {script_path}...")
        try:
            subprocess.run(["python3", script_path], check=True)
            print(f"✓ Finished {script_path}\n")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error running {script_path}: {e}\n")

if __name__ == "__main__":
    run_pipeline()
