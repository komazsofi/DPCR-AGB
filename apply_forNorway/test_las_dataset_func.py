import pandas as pd
import glob
import os
import geopandas as gpd

from torch_points3d.datasets.instance import las_dataset as ls

# Test Las class

# Get a list of all .laz files
pt_files_paths = glob.glob("/home/nibio/DPCR-AGB/debug_forNorway/clip_plots_forDL_test_reorg/*.laz")
pt_files_list = [{"pt_file": path} for path in pt_files_paths]
print(pt_files_list)

labels_df = gpd.read_file('/home/nibio/DPCR-AGB/debug_forNorway/final_labels_sorted.gpkg')
print(labels_df["las_file"].iloc[0])

#base_dir = "/home/nibio/DPCR-AGB/debug_forNorway/test/als_plots/"
#labels_df['pt_file'] = labels_df['las_file'].apply(lambda x: os.path.join(base_dir, os.path.basename(x)))

# Define the path transformations
#old_base = "/home/nibio/DPCR-AGB/torch-points3d/data/biomass/raw/clip_plots_forDL_test/"
#new_base = "/home/nibio/DPCR-AGB/debug_forNorway/clip_plots_forDL_test/"

# Update the paths in the column
#labels_df["pt_file"] = labels_df["las_file"].str.replace(old_base, new_base, regex=False)
print(labels_df["pt_file"].iloc[0])

# Duplicate the first row
# first_row = labels_df.iloc[0]  # Get the first row
# duplicated_row = pd.DataFrame([first_row], columns=labels_df.columns)  # Convert it to a DataFrame

# Insert the duplicated row at the beginning
# labels_df = pd.concat([duplicated_row, labels_df], ignore_index=True)

# Remove first row
#labels_df = labels_df.iloc[1:].reset_index(drop=True)

pd.set_option('display.max_columns', None)
print(labels_df)

areas_dict = {
  "NFI": {
    "type": "object",
    "pt_files": "clip_plots_forDL_test/*/*.laz",
    "label_files": "SR16_training_forDL_test.gpkg",
    "check_pt_crs": False,
    "pt_identifier": "pt_file",
    "labels": labels_df,
    "split_col": "split",
    "delimiter": ","
  }
}

targets = {
  "VOLMB": {"task": "regression", "weight": 0.5},
}

las = ls.Las(root="/home/nibio/DPCR-AGB/debug_forNorway/", areas=areas_dict, split="train", stats=None, targets=targets)
#las = ls.Las(root="/home/nibio/DPCR-AGB/debug_forNorway/", areas=areas_dict, split="test", stats=None, targets=targets)
#las = ls.Las(root="/home/nibio/DPCR-AGB/debug_forNorway/", areas=areas_dict, split="val", stats=None, targets=targets)