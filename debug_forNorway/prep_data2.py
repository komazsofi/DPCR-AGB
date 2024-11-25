import os
import geopandas as gpd
import shutil

# Paths
nfi_path = '/home/nibio/DPCR-AGB/torch-points3d/data/biomass/nfi.gpkg'
las_dir = '/home/nibio/DPCR-AGB/torch-points3d/data/biomass/raw/2014/region1'
output_gpkg_path = '/home/nibio/DPCR-AGB/torch-points3d/data/biomass/raw/nfi.gpkg'

# Read the GeoPackage
nfi = gpd.read_file(nfi_path)
for index, row in nfi.head().iterrows():
    print(f"Row {index}:")
    for col_name, value in row.items():
        print(f"  {col_name}: {value}")

# Function to rename LAS files in the directory
def rename_las_files(directory, nfi_df):
    # Collect all LAS files and sort by their number
    las_files = [
        file_name for file_name in os.listdir(directory)
        if file_name.startswith("file_") and file_name.endswith(".las")
    ]
    las_files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))

    # Rename files and update the GeoDataFrame
    for new_number, old_file_name in enumerate(las_files):
        # Create the new file name
        new_file_name = f"file_{new_number}.las"

        # Rename the LAS file
        old_path = os.path.join(directory, old_file_name)
        new_path = os.path.join(directory, new_file_name)
        shutil.move(old_path, new_path)

        # Update the GeoPackage `las_file` column
        old_relative_path = f"raw/2014/region1/{old_file_name}"
        new_relative_path = f"raw/2014/region1/{new_file_name}"
        nfi_df['las_file'] = nfi_df['las_file'].replace(old_relative_path, new_relative_path)

    print("Renaming complete and GeoDataFrame updated.")

# Update `BMag_ha` attribute in the GeoPackage
nfi['BMag_ha'] = nfi['V_ha']

# Rename LAS files and update GeoPackage paths
rename_las_files(las_dir, nfi)

def update_las_file_path(las_file_path):
    if 'raw/' in las_file_path:
        # Keep only the part of the path after 'raw/'
        return las_file_path.split('raw/', 1)[-1]
    return las_file_path

nfi['las_file'] = nfi['las_file'].apply(update_las_file_path)
nfi['las_file'] = nfi['las_file'].apply(lambda path: os.path.basename(path))
nfi['las_file'] = nfi['las_file'].apply(lambda x: f"raw/2014/region1/{x.split('/')[-1]}")
nfi['split_col'] = nfi['split']

nfi['split'] = nfi['split_col'].str.strip().str.lower()

# Save the modified GeoPackage
nfi.to_file(output_gpkg_path, driver="GPKG", delimiter=",")
nfi.to_file("/home/nibio/DPCR-AGB/torch-points3d/data/biomass/nfi.gpkg", driver="GPKG", delimiter=",")

print(f"Updated GeoPackage saved to: {output_gpkg_path}")

for index, row in nfi.head().iterrows():
    print(f"Row {index}:")
    for col_name, value in row.items():
        print(f"  {col_name}: {value}")

las_files = sorted([f for f in os.listdir("/home/nibio/DPCR-AGB/torch-points3d/data/biomass/raw/2014/region1/") if f.endswith(".las")])
print(las_files)