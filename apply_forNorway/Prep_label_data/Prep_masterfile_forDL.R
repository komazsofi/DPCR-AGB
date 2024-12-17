source("~/sr-16-update-workflow/configuration_file.R")

mdat <- readRDS(paste0(outdir_data_prep, "SR16_Modelldata_ref_", refdate, "_outliers.rds"))

mdat_sel_fortrain=mdat[, c(1:32, 47, 51, 141 ,150:157, 164, 165, 178:180)]

write.csv(mdat_sel_fortrain,"/disks/normal/laserdata2/SR16_DL/SR16_Modelldata_ref_2024_forDLtrain.csv")