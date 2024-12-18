import pandas as pd
import glob
import os
import geopandas as gpd

from torch_points3d.datasets.instance import las_dataset as ls

# Test Las class

# Get a list of all .laz files
pt_files_paths = glob.glob("/home/nibio/DPCR-AGB/torch-points3d/data/biomass/raw/2014/region1/*.laz")
pt_files_list = [{"pt_file": path} for path in pt_files_paths]
print(pt_files_list[1:5])

labels_df = gpd.read_file('/home/nibio/DPCR-AGB/torch-points3d/data/biomass/raw/nfi.gpkg')
print(labels_df["las_file"].iloc[0])
labels_df['pt_file'] = labels_df['las_file']

pd.set_option('display.max_columns', None)
print(labels_df)

areas_dict = {
  "NFI": {
    "type": "object",
    "pt_files": "2014/*/*.laz",
    "label_files": "nfi.gpkg",
    "check_pt_crs": False,
    "pt_identifier": "las_file",
    "labels": labels_df,
    "split_col": "split",
    "delimiter": ","
  }
}

targets = {
  "VOLMB": {"task": "regression", "weight": 0.5},
}

las = ls.Las(root="/home/nibio/DPCR-AGB/apply_forNorway/", areas=areas_dict, split="train", stats=None, targets=targets)
#las = ls.Las(root="/home/nibio/DPCR-AGB/debug_forNorway/", areas=areas_dict, split="test", stats=None, targets=targets)
#las = ls.Las(root="/home/nibio/DPCR-AGB/debug_forNorway/", areas=areas_dict, split="val", stats=None, targets=targets)