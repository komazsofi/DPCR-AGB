library(sf)
library(sr16)
library(stringr)
library(dplyr)
library(readr)
library(lidR)

source("/home/zsko/.creditals.R")

# Import
als_dir="~/network_fstab/databank/Kildedata/Punktskydata/fra_hoydedata_no/ALS/"
als_info=st_read("/disks/normal/laserdata2/SR16_Update2024/Update_processing/Data_preparation/proj_utm33_main_als.shp")
als_info=st_transform(als_info,crs=25833)

clipplot_dir="/disks/normal/laserdata2/SR16_DL/test_prep_dec2024/clip_plots_forDL_test2/"

masterfile=read.csv("/disks/normal/laserdata2/SR16_DL/test_prep_dec2024/SR16_ref_2024_forDLtrain_test.csv")

## Import coords and make selection
pts <- nfi_coords(all_theoretical = FALSE, crs=25833,uid=.ORACLE_UID_full,pwd=.ORACLE_PW_full)
pts_filt <- pts[pts$FLATEID %in% masterfile$FLATEID, ]

# Get ALS project information
als_info <- st_make_valid(als_info)

als_aoi=st_intersection(pts_filt,als_info)
print(unique(als_aoi$PROSJNAVN))

als_aoi_c=als_aoi[,c("PROSJNAVN","RAPPORT","SISTFLYDAT","FLATEID")]

# Extract project number and the year of measurements
projnumb <- str_match(als_aoi_c$RAPPORT, "\\\\(\\d+)\\\\")
als_aoi_c$ProjectID=as.numeric(projnumb[,2])

als_projs <- get_vroom2('als_projects')
als_projs <- als_projs[!duplicated(als_projs$pid),]

als_aoi_c2 <- als_aoi_c %>%
  left_join(als_projs %>% dplyr::select(pid, sr16_id, ), by = c("ProjectID" = "pid"))

# Extract circular plots around random points

for (i in 1:length(als_aoi_c2$ProjectID)) {
  
  print(i)
  
  tileshp=list.files(path=paste0(als_dir,als_aoi_c2$ProjectID[i],"/metadata/"),pattern="Tileinndeling.shp",full.names = TRUE)
  tileshp_v=st_read(tileshp)
  
  tileshp_v <-  sf::st_transform(tileshp_v, sf::st_crs(25833))
  tile_aoi=st_intersection(als_aoi_c2[i,],tileshp_v)
  
  if (any("kartid" %in% names(tile_aoi))) {
    tile_aoi <- rename(tile_aoi, KARTID = kartid)
  }
  
  lasfile=paste0(als_dir,tile_aoi$ProjectID,"/data/",tile_aoi$KARTID,".laz")
  las=readLAS(lasfile)
  
  las_pr <-  sf::st_transform(las, sf::st_crs(25833))
  las_sub=clip_roi(las_pr,st_buffer(tile_aoi,dist=9))
  
  writeLAS(las_sub,paste0(clipplot_dir,als_aoi_c2$FLATEID[i],"_",als_aoi_c2$sr16_id[i],".laz"))
  
}