import os

import pandas as pd
import geopandas as gpd
import numpy as np

# csv file
#data=pd.read_csv('/home/nibio/SR16_DL/torch-points3d/data/biomass/rand_gen_points_split.csv')

#new_path = "/home/nibio/SR16_DL/torch-points3d/data/biomass/als_plots/"
#data['pt_file'] = data['pt_file'].apply(lambda row: new_path + row)

#print(data['pt_file'].iloc[0])

#data.to_csv('/home/nibio/SR16_DL/torch-points3d/data/biomass/rand_gen_points_split_mod.csv', index=False)

# working with geopackage file
gdf = gpd.read_file('/home/nibio/SR16_DL/torch-points3d/data/biomass/rand_gen_points_clean.gpkg')
#gdf = gdf.rename(columns={'las_file': 'pt_file'})

new_path = "/home/nibio/SR16_DL/torch-points3d/data/biomass/als_plots/"
gdf['pt_file'] = gdf['las_file'].apply(lambda row: new_path + row)

# Add a new column 'split_col' with desired proportions of 'train', 'val', 'test'
choices = ['train', 'val', 'test']
probs = [0.7, 0.1, 0.2]  # probabilities for 'train', 'val', 'test' respectively

gdf['split_col'] = np.random.choice(choices, size=len(gdf), p=probs)
print(gdf)
print(gdf['pt_file'].iloc[0])
print(gdf['las_file'].iloc[0])

# Check whether all laz files exists

# List of all .laz files in the directory
laz_files = [os.path.join(new_path, f) for f in os.listdir(new_path) if f.endswith('.laz')]
#print(laz_files)

# Filter rows in GeoDataFrame based on existence of .laz files in the directory
gdf = gdf[gdf['pt_file'].isin(laz_files)]
gdf['ID'] = range(len(gdf))

print(gdf)

# Export
gdf.to_file('/home/nibio/SR16_DL/torch-points3d/data/biomass/rand_gen_points_clean_mod.gpkg', driver='GPKG')

# Filter rows where 'split_col' is 'train', 'test', or 'val'
train_df = gdf[gdf['split_col'] == 'train']
print(train_df.shape)
test_df = gdf[gdf['split_col'] == 'test']
val_df = gdf[gdf['split_col'] == 'val']

# Select desired columns
columns = ['ID', 'SRRVOLMB_1']
print(train_df[columns].shape)

train_df['ID'] = range(len(train_df))
test_df['ID'] = range(len(test_df))
val_df['ID'] = range(len(val_df))

# Save to CSV files
train_df[columns].to_csv('/home/nibio/SR16_DL/nfi-data/train_split.csv', index=False)
test_df[columns].to_csv('/home/nibio/SR16_DL/nfi-data/test_split.csv', index=False)
val_df[columns].to_csv('/home/nibio/SR16_DL/nfi-data/val_split.csv', index=False)