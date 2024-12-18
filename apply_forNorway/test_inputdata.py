import geopandas as gpd
import os
import laspy

# Load your GeoPackage
nfi = gpd.read_file("/home/nibio/DPCR-AGB/torch-points3d/data/biomass/raw/nfi.gpkg")

# Check the splits
test_data = nfi[nfi['split'] == 'test']
train_data = nfi[nfi['split'] == 'train']

# Check the number of rows in the test split
print(f"Number of test samples: {len(test_data)}")
print(f"Number of test samples: {len(train_data)}")

# Verify that all LAS files referenced in the GeoPackage exist
missing_files = []
for file in nfi['las_file']:
    if not os.path.exists(file):
        missing_files.append(file)

if missing_files:
    print(f"Missing LAS files: {missing_files}")
else:
    print("All LAS files are present.")

# Define the directory containing LAS files
las_dir = "/home/nibio/DPCR-AGB/torch-points3d/data/biomass/raw/2014/region1/"

# Iterate through all files in the directory
for las_file in os.listdir(las_dir):
    if las_file.endswith(".laz"):  # Check if the file is a LAS file
        las_path = os.path.join(las_dir, las_file)  # Full path to the LAS file
        try:
            with laspy.open(las_path) as las:
                print(f"LAS file read successfully: {las_path}")
        except UnicodeDecodeError as e:
            print(f"Encoding issue with file: {las_path} - {e}")
        except Exception as e:  # Catch any other exceptions
            print(f"Error with file {las_path}: {e}")

las_file_path = "/home/nibio/DPCR-AGB/torch-points3d/data/biomass/raw/2014/region1/label_2.laz"

try:
    with laspy.open(las_file_path) as las:
        # Check header details
        header = las.header
        print("Header Information:")
        print(f"Version: {header.version}")
        print(f"Point Count: {header.point_count}")
        print(f"System Identifier: {header.system_identifier}")
        print(f"Generating Software: {header.generating_software}")

        # Check VLRs
        vlrs = header.vlrs
        print("\nVariable Length Records (VLRs):")
        for vlr in vlrs:
            print(f"Description: {vlr.description}")
            print(f"Record ID: {vlr.record_id}")
            print(f"Data: {vlr.data}")
except Exception as e:
    print(f"Error while reading LAS file: {e}")

