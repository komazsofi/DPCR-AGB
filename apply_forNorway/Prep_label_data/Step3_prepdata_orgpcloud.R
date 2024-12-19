# Load required libraries
library(fs)
library(lidR)
library(sf)

# Function to search, extract, and convert .laz files
extract_and_convert_laz_files <- function(search_directory, output_directory, target_crs = 25833) {
  # Ensure output directory exists
  if (!dir_exists(output_directory)) {
    dir_create(output_directory)
  }
  
  # Search for .laz files recursively
  laz_files <- dir_ls(search_directory, recurse = TRUE, glob = "*.laz")
  
  # Process each .laz file
  for (file in laz_files) {
    # Read the .laz file
    las <- readLAS(file)
    
    # Check if the file was read successfully
    if (is.null(las)) {
      message(paste("Failed to read", file))
      next
    }
    
    # Transform CRS
    las_transformed <- st_transform(las, crs = target_crs)
    
    # Generate the output file name
    file_name <- path_file(file)
    output_file <- path(output_directory, file_name)
    
    # Write the transformed .laz file
    writeLAS(las_transformed, output_file)
  }
  
  # Provide feedback
  if (length(laz_files) > 0) {
    message(paste(length(laz_files), ".laz files have been processed and exported to", output_directory))
  } else {
    message("No .laz files were found in the specified directory.")
  }
}

################## MAIN SCRIPT

# Example usage
search_directory <- "/disks/normal/laserdata2/SR16_DL/clip_plots_forDL/"  # Replace with the directory to search
output_directory <- "/disks/normal/laserdata2/SR16_DL/prep_allnfi_dec2024/"  # Replace with the output directory

# Call the function
extract_and_convert_laz_files(search_directory, output_directory)