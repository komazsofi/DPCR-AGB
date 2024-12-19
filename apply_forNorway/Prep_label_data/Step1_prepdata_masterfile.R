library(sr16)
source("/home/zsko/.creditals.R")

# Import

inputdir="/disks/normal/laserdata2/SR16_Update2024/Update_processing/Data_preparation/"
refdate="2024-09-01"

mdat <- readRDS(paste0(inputdir, "SR16_Modelldata_ref_", refdate, "_final.rds"))

# Filter attributes

mdat_sel_fortrain=mdat[, c(1:32, 47, 51, 141 ,150:154, 164, 165, 178)]
#mdat_sel_fortrain_sel=mdat_sel_fortrain[mdat_sel_fortrain$Region_id==2,]

# Export

write.csv(mdat_sel_fortrain,"/disks/normal/laserdata2/SR16_DL/SR16_ref_2024_forDLtrain_all.csv")