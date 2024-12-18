library(sr16)
library(lidR)
library(sf)
library(dplyr)
library(raster)

source("/home/zsko/.creditals.R")

clip_plots2 <- function(alsdir,outdir,pts=NA,dst=8.92,shape='circle',filter='-drop_class 7',suffix=NA,recursive=FALSE,laz=TRUE){
  
  library(lidR)
  library(sf)
  
  # LS-flater
  if (is.na(pts)[1]) pts <- nfi_coords(theoretical = FALSE,crs=25832)
  
  if (!dir.exists(outdir)) dir.create(outdir)
  
  
  # create LAScatalog with lidR
  cat('creating lascatalog with lidR...')
  
  if (recursive) alsdir <- list.files(alsdir,recursive=TRUE, full.names = TRUE, pattern='\\.laz$|\\.las$')
  
  ctg <- catalog(alsdir) 
  cat('done.\n')
  
  # points in same crs as alsdata
  pts <- st_transform(pts,crs = st_crs(ctg))
  pts <- st_set_crs(pts, st_crs(ctg)$epsg)
  #st_crs(pts) <- st_crs(ctg)$epsg 
  
  # bare flatesentere innenfor laserdata-omriss
  inside <- sapply( st_intersects(pts, st_as_sf(ctg) ) , function(x){length(x) != 0}) 
  pts <- pts[inside,]
  
  # hvis ingen flater innen prosjekt
  if (nrow(pts) < 1) {cat('No plots within bounding box.\n') ; return(invisible(1))}
  
  # buffer
  if (shape == 'square')   pts_buff <- st_buffer(pts,endCapStyle='SQUARE',nQuadSegs=4,dist=dst) 
  if (shape == 'circle')   pts_buff <- st_buffer(pts,nQuadSegs=100,dist=dst) 
  
  # legg til suffix 
  if(is.na(suffix)) { pts_buff$FLATEID_suffix <- pts_buff$FLATEID } else { pts_buff$FLATEID_suffix <- with(pts_buff, paste0(FLATEID,suffix)) }
  
  # navn på katalog for utdata
  opt_output_files(ctg) <- paste0(outdir,"{FLATEID_suffix}")
  opt_laz_compression(ctg) <- laz
  
  # hack pga feil i lidR
  pts_buff$geometry <- pts_buff$geom
  
  # klipp med lidR
  #lc <- try( lasclip(ctg,pts_buff,filter=filter) , silent=TRUE)
  lc <- try( clip_roi(ctg, pts_buff, filter=filter) , silent=TRUE)
  
  if (class(lc) == 'try-error') if(lc == "Error : written_path is not character it is a NULL\n") {
    
    warning('No points within AOI. Should be ok, but lidR::lasclip throws an error anyway (a bug?): ',lc)
    
    return (invisible(1))
    
  } else { stop('lidR::lasclip: ',lc) }
  
  return (invisible(0))
  
  
}

clipping_als_forNFI <- function(clipplot_dir, als_dir, als_projs, pts) {
  
  #TODO: write a log file which catches also errors printed out red
  
  # Delete empty folders
  for(f in list.files(clipplot_dir, full.names = TRUE)){
    n_f <- list.files(f)
    if(length(n_f) == 0){
      print(paste0('Deleting empty folder: ', f))
      unlink(f, recursive = TRUE)
    }
  }
  
  # Get the list of directories
  als_dir_list = list.dirs(als_dir, recursive = FALSE)
  
  # Loop over directories and clip plots
  for (i in 1:length(als_dir_list)){ 
    
    pid <- as.numeric(basename(als_dir_list[i]))
    sr16id <- als_projs$sr16_id[als_projs$pid == pid]
    projsnavn <- als_projs$prosjnavn[als_projs$pid == pid]
    
    cat(paste0('----\n', projsnavn,' - ',i,' sr16id:', sr16id, '\n----\n'))
    
    alsdir <- paste0(als_dir_list[i],'/data/')
    outdir <- paste0(clipplot_dir, sr16id, '/')
    
    if (dir.exists(outdir)) {
      cat('Clips already exists, skipping.\n')
      next 
    }
    try(clip_plots2(alsdir, outdir, pts = pts, suffix = paste0('_', sr16id)))
  }
  
}

################## MAIN SCRIPT

als_dir <- "~/network_fstab/databank/Kildedata/Punktskydata/fra_hoydedata_no/ALS/"
clipplot_dir="/disks/normal/laserdata2/SR16_DL/test_prep_dec2024/clip_plots_forDL_test/"
masterfile=read.csv("/disks/normal/laserdata2/SR16_DL/test_prep_dec2024/SR16_ref_2024_forDLtrain_test.csv")

## Import
pts <- nfi_coords(all_theoretical = FALSE, crs=25833,uid=.ORACLE_UID_full,pwd=.ORACLE_PW_full)

pts_filt <- pts[pts$FLATEID %in% masterfile$FLATEID, ]

# Get projects
als_projs <- get_vroom2('als_projects')
# This is needed because I accidentally generated two sr16id for two projects
als_projs <- als_projs[!duplicated(als_projs$pid),]

### Processing newly downloaded data and add to clip plots database ###

clipping_als_forNFI(clipplot_dir, als_dir, als_projs, pts_filt)