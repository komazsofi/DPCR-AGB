import os
import geopandas as gpd

# Define the directory containing the LAS files
las_directory = "/home/nibio/DPCR-AGB/torch-points3d/data/biomass/raw/2014/region1/"

# Get the list of files in the directory
file_list = {os.path.basename(f): os.path.join(las_directory, f) for f in os.listdir(las_directory) if f.endswith('.laz')}

# Load the GPKG file
gpkg_file_path = "/home/nibio/DPCR-AGB/debug_forNorway/test/rand_gen_points_clean_mod.gpkg"
gdf = gpd.read_file(gpkg_file_path)

#gdf['las_file'] = gdf['las_file'].str.replace('.las', '.laz', regex=False)

gdf['file_name'] = gdf['las_file'].apply(
    lambda x: file_list.get(os.path.basename(x), None)  # Match the base name of `las_file` with `file_list`
)

gdf.rename(columns={'las_file': 'las_file1'}, inplace=True)
gdf.rename(columns={'file_name': 'las_file'}, inplace=True)

gdf['las_file3'] = gdf['las_file'].apply(os.path.basename)

gdf = gdf.drop(columns=['ID'])
gdf = gdf.iloc[1:].reset_index(drop=True)

for index, row in gdf.head().iterrows():
    print(f"Row {index}:")
    for col_name, value in row.items():
        print(f"  {col_name}: {value}")

# Save the updated GPKG file
output_gpkg_path = "/home/nibio/DPCR-AGB/debug_forNorway/nfi.gpkg"
gdf.to_file(output_gpkg_path, driver="GPKG", delimiter=",")
