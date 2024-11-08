import pandas as pd
import glob
import geopandas as gpd

from torch_points3d.datasets.instance import las_dataset as ls

# Test read_pt

pt_file = '/home/nibio/SR16_DL/torch-points3d/data/biomass/als_plots/gen_rand_plot_1.laz'  # replace with your file path
#feature_cols = ['intensity']  # replace with the features you're interested in

# Call the function
pos, features, crs = ls.read_pt(pt_file,feature_cols=[],delimiter=",")

# Print the results
print("Positions:", pos)
print("Features:", features)
print("CRS:", crs)

# Test Las class

# Get a list of all .laz files
pt_files_paths = glob.glob("/home/nibio/SR16_DL/torch-points3d/data/biomass/als_plots/*.laz")
pt_files_list = [{"pt_file": path} for path in pt_files_paths]
#print(pt_files_list)

#labels_df = pd.read_csv('/home/nibio/DPCR-AGB/torch-points3d/data/biomass/rand_gen_points_split_mod.csv')
labels_df=gpd.read_file('/home/nibio/SR16_DL/torch-points3d/data/biomass/rand_gen_points_clean_mod.gpkg')
#print(labels_df)

areas_dict = {
  "NFI": {
    "type": "object",
    "pt_files": "/biomass/als_plots/*.laz",
    "label_files": "/biomass/rand_gen_points_clean.gpkg",
    "check_pt_crs": False,
    "pt_identifier": "pt_file",
    "labels": labels_df,
    "split_col": "split_col",
    "delimiter": ","
  }
}

targets = {
  "SRRVOLMB_1": {"task": "regression", "weight": 0.5},
}

las = ls.Las(root="/home/nibio/SR16_DL/torch-points3d/data/", areas=areas_dict, split="train", stats=None, targets=targets)
las = ls.Las(root="/home/nibio/SR16_DL/torch-points3d/data/", areas=areas_dict, split="test", stats=None, targets=targets)
las = ls.Las(root="/home/nibio/SR16_DL/torch-points3d/data/", areas=areas_dict, split="val", stats=None, targets=targets)