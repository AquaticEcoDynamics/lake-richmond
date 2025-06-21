"""
Script: lakelevel_import_pipeline.py

Description:
    This script orchestrates the execution of all individual data import scripts that contribute
    to the creation or update of the consolidated lakelevel.parquet file used in analysis and plotting.

Key Features:
    - Archives existing lakelevel.parquet file with timestamp before rebuilding
    - Executes a series of import scripts in sequence
    - Allows easy extensibility by modifying the `pipeline_scripts` list
    - Provides logging of success or failure per script

Output:
    Updated lakelevel.parquet file in Data/data-warehouse/parquet/level/
    Backup of previous file stored with timestamp in the same directory

Requirements:
    - Python 3.7+
    - All required libraries for each script must be satisfied within the active environment

Author: Brendan Busch
"""

import subprocess
import os
from datetime import datetime
import shutil

# Archive existing lakelevel.parquet file
parquet_path = "Data/data-warehouse/parquet/level/lakelevel.parquet"
if os.path.exists(parquet_path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = f"{parquet_path}.{timestamp}.bak"
    shutil.move(parquet_path, archive_path)
    print(f"Archived existing parquet file to {archive_path}")

# Define relative paths to your pipeline scripts
pipeline_scripts = [
    "import_dwer_lakelevel.py",
    "load_mwh.py",
    "import_hge.py",
]

def run_pipeline():
    print("Running Lake Level Data Pipeline...\n")
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