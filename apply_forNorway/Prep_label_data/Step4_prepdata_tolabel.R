# Load required libraries
library(dplyr)
library(sf)

source("/home/zsko/.creditals.R")

# Define directories
laz_directory <- "/disks/normal/laserdata2/SR16_DL/test_prep_dec2024/clip_plots_forDL_test2_dummy/"        # Replace with the directory containing .laz files
output_directory <- "/disks/normal/laserdata2/SR16_DL/test_prep_dec2024/" # Updated to separate metadata output directory
server_dir <- "/home/nibio/DPCR-AGB/torch-points3d/data/biomass/raw/2014/region1"

# Load masterfile
masterfile <- read.csv("/disks/normal/laserdata2/SR16_DL/test_prep_dec2024/SR16_ref_2024_forDLtrain_test.csv")
pts <- nfi_coords(all_theoretical = FALSE, crs=25833,uid=.ORACLE_UID_full,pwd=.ORACLE_PW_full)

masterfile <- pts %>%
  right_join(masterfile, by = "FLATEID")

# List all .laz files in the directory
laz_files <- list.files(laz_directory, pattern = "\\.laz$", full.names = TRUE)

# Extract basename without extension
laz_data <- data.frame(
  original_name = basename(laz_files),
  stringsAsFactors = FALSE
) %>% 
  mutate(
    FLATEID = sub("_.*", "", original_name),
    project = as.numeric(sub(".*_(.*)\\.laz$", "\\1", original_name))
  )

# Join with masterfile based on FLATEID and project
laz_data <- laz_data %>% 
  left_join(masterfile, by = c("FLATEID", "project"))

# Identify rows where joined attributes from masterfile are NA
na_rows <- apply(laz_data, 1, function(row) any(is.na(row[-c(1:2)])))  # Exclude FLATEID and project columns

# Delete corresponding .laz files and remove rows with NA attributes
if (any(na_rows)) {
  files_to_delete <- laz_files[na_rows]
  file.remove(files_to_delete)
  laz_data <- laz_data[!na_rows, ]
}

# Update laz_files to match filtered laz_data
laz_files <- laz_files[!na_rows]

# Generate new labels and columns
laz_data <- laz_data %>% 
  mutate(
    label = paste0("label_", row_number()),
    pt_file = paste0(label, ".laz"),
    las_file = file.path(server_dir, paste0(label, ".laz"))
  )

# Rename the laz files in the original directory
for (i in seq_along(laz_files)) {
  new_name <- file.path(laz_directory, paste0(laz_data$label[i], ".laz"))
  if (file.exists(laz_files[i])) {
    file.rename(laz_files[i], new_name)
  } else {
    warning(paste("File does not exist:", laz_files[i]))
  }
}

# Add split and split_col attributes
set.seed(123)  # For reproducibility
n <- nrow(laz_data)
splits <- sample(c("train", "val", "test"), size = n, replace = TRUE, prob = c(0.7, 0.1, 0.2))
laz_data <- laz_data %>% 
  mutate(
    split = splits,
    split_col = splits
  )

# Select desired attributes and convert to sf object
laz_sf <- laz_data %>%
  dplyr::select(FLATEID, VOLMB, las_file, split, split_col, geometry) %>%
  st_as_sf()

# Remove the first row from the sf object
laz_sf <- laz_sf[-1, ]

# Export as GeoPackage
gpkg_path <- file.path(output_directory, "laz_data_test2_dummy.gpkg")
st_write(laz_sf, gpkg_path, delete_dsn = TRUE)
