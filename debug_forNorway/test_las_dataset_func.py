import pandas as pd
import glob
import os
import geopandas as gpd

from torch_points3d.datasets.instance import las_dataset as ls

# Test read_pt

pt_file = '/home/nibio/DPCR-AGB/debug_forNorway/test/als_plots/gen_rand_plot_1.laz'  # replace with your file path
#feature_cols = ['intensity']  # replace with the features you're interested in

# Call the function
pos, features, crs = ls.read_pt(pt_file,feature_cols=[],delimiter=",")

# Print the results
print("Positions:", pos)
print("Features:", features)
print("CRS:", crs)

# Test Las class

# Get a list of all .laz files
pt_files_paths = glob.glob("/home/nibio/DPCR-AGB/debug_forNorway/test/als_plots/*.laz")
pt_files_list = [{"pt_file": path} for path in pt_files_paths]
print(pt_files_list)

labels_df = gpd.read_file('/home/nibio/DPCR-AGB/debug_forNorway/test/rand_gen_points_clean_mod.gpkg')

base_dir = "/home/nibio/DPCR-AGB/debug_forNorway/test/als_plots/"
labels_df['pt_file'] = labels_df['las_file'].apply(lambda x: os.path.join(base_dir, os.path.basename(x)))

pd.set_option('display.max_columns', None)
print(labels_df)
print(labels_df['pt_file'].iloc[0])

areas_dict = {
  "NFI": {
    "type": "object",
    "pt_files": "test/als_plots/*.laz",
    "label_files": "test/rand_gen_points_clean_mod.gpkg",
    "check_pt_crs": False,
    "pt_identifier": "pt_file",
    "labels": labels_df,
    "split_col": "split_col",
    "delimiter": ","
  }
}

targets = {
  "V_ha": {"task": "regression", "weight": 0.5},
}

las = ls.Las(root="/home/nibio/DPCR-AGB/debug_forNorway/", areas=areas_dict, split="train", stats=None, targets=targets)
las = ls.Las(root="/home/nibio/DPCR-AGB/debug_forNorway/", areas=areas_dict, split="test", stats=None, targets=targets)
las = ls.Las(root="/home/nibio/DPCR-AGB/debug_forNorway/", areas=areas_dict, split="val", stats=None, targets=targets)