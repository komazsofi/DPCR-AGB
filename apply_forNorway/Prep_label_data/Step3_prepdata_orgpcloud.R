# Load required libraries
library(fs)

# Function to search and extract .laz files
extract_laz_files <- function(search_directory, output_directory) {
  # Ensure output directory exists
  if (!dir_exists(output_directory)) {
    dir_create(output_directory)
  }
  
  # Search for .laz files recursively
  laz_files <- dir_ls(search_directory, recurse = TRUE, glob = "*.laz")
  
  # Copy each .laz file to the output directory
  for (file in laz_files) {
    file_name <- path_file(file)
    file_copy(file, path(output_directory, file_name), overwrite = TRUE)
  }
  
  # Provide feedback
  if (length(laz_files) > 0) {
    message(paste(length(laz_files), ".laz files have been extracted to", output_directory))
  } else {
    message("No .laz files were found in the specified directory.")
  }
}

################## MAIN SCRIPT

# Example usage
search_directory <- "/disks/normal/laserdata2/SR16_DL/test_prep_dec2024/clip_plots_forDL_test/"  # Replace with the directory to search
output_directory <- "/disks/normal/laserdata2/SR16_DL/test_prep_dec2024/clip_plots_forDL_test_forDL/"  # Replace with the output directory

# Call the function
extract_laz_files(search_directory, output_directory)