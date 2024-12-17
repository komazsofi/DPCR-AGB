import os
import glob

import pandas as pd
import geopandas as gpd
import numpy as np

from shapely.geometry import Point

# Import
path_field_data="/home/nibio/DPCR-AGB/debug_forNorway/SR16_Modelldata_ref_2024_forDLtrain.csv"

# Read in and convert into geopandas based on approx coords
df_field = pd.read_csv(path_field_data)
print(df_field.head)
print(df_field.info())

geometry = [Point(xy) for xy in zip(df_field['longitude'], df_field['latitude'])]
gdf_field = gpd.GeoDataFrame(df_field, geometry=geometry)
gdf_field .set_crs(epsg=4326, inplace=True)
print(gdf_field.head)
print(gdf_field.info())

# Give an attribute with the laz names created based on FLATEID and project (sr16id)
base_path = '/home/nibio/DPCR-AGB/debug_forNorway/clip_plots_forDL_test'
gdf_field ['las_file'] = (
    base_path + '/' + gdf_field['project'].astype(str) + '/' + gdf_field ['FLATEID'] + '_' + gdf_field['project'].astype(str) + '.laz'
)
print(gdf_field[['las_file']].head)

# Check whether files exists
gdf_field['file_exists'] = gdf_field['las_file'].apply(os.path.exists)
file_exists_stats = gdf_field['file_exists'].value_counts()
print(file_exists_stats)

# Create dataframe which is in the right order and populate information from other dataframe
pattern = '/home/nibio/DPCR-AGB/debug_forNorway/clip_plots_forDL_test/*/*.laz'
file_list = glob.glob(pattern)
#print(file_list)

file_df = pd.DataFrame(file_list, columns=['las_file'])
df_train = file_df.merge(gdf_field, on='las_file', how='left')
gdf_train = gpd.GeoDataFrame(df_train, geometry=df_train['geometry'], crs=gdf_field.crs)
print(gdf_train.head)
print(gdf_train.info())

# Clean data table and remove files that are not exists/outlier
gdf_train_filt = gdf_train[
    (gdf_train['file_exists'] == True) &
    (gdf_train['Region_id'] == 2) &
    (gdf_train['out_vol'] != True) &
    (gdf_train['out_mhoyde'] != True)]
print(gdf_train_filt.head)

valid_las_files = set(gdf_train_filt['las_file'])

for root, _, files in os.walk(base_path):
    for file in files:
        if file.endswith('.laz'):
            full_path = os.path.join(root, file)

            # Step 3: Check if the file exists in the GeoDataFrame
            if full_path not in valid_las_files:
                # If not in the GeoDataFrame, remove the file
                print(f"Removing: {full_path}")
                os.remove(full_path)

# Assign train, val, test
choices = ['train', 'val', 'test']
probs = [0.7, 0.1, 0.2]  # probabilities for 'train', 'val', 'test' respectively

gdf_train_filt['split'] = np.random.choice(choices, size=len(gdf_train_filt), p=probs)

# Select coloumns which is needed, correct path and export
columns_to_select = ['FLATEID', 'VOLMB', 'las_file', 'split', 'geometry']
gdf_selected = gdf_train_filt[columns_to_select]

old_base_path = "/home/nibio/DPCR-AGB/debug_forNorway/"
new_base_path = "/home/nibio/DPCR-AGB/torch-points3d/data/biomass/raw/"

gdf_selected['las_file'] = gdf_selected['las_file'].str.replace(old_base_path, new_base_path, regex=False)
gdf_selected.to_file("/home/nibio/DPCR-AGB/debug_forNorway/SR16_training_forDL_test.gpkg", driver="GPKG")