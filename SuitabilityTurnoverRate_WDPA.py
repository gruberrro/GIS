##Author: Jesse Langdon
##Title: Calculate Suitability Turnover Rate with Biomes
##Contact: jesselangdon@gmail.com
##Description: Calculate the habitat turnover rate by protected area polygon.

# Load Python libraries          
import pyodbc
import time
from time import clock
import arcpy
from arcpy import env
from arcpy.sa import *
import os

# start timing the process
start = time.clock()

# checkout Spatial Analyst extension
arcpy.CheckOutExtension("Spatial")

# enable overwriting
arcpy.env.overwriteOutput = True

# Set ArcPy workspace environment
env.workspace = "C:/JL/Data/SppTurnover/WDPA_WithBiomes.gdb"

# connect to SQL Server Express database
cnxn = pyodbc.connect('DRIVER={SQL Server Native Client 10.0};SERVER=DESKTOP\SQLEXPRESS;DATABASE=Species;UID=sa;PWD=SimfdS#1')
cursor = cnxn.cursor()
rows = cursor.execute("select ID from dbo.View_AllSpp_ForTurnover")

# Set variables
modelList = [ row.ID for row in rows ] 
gcmList = (["a2_CGCM31", "a2_HADCM3"])
inputPath = ("C:/JL/Data/BiomeSuitability/FinalOutput/")
outputPath = ("C:/JL/Data/SppTurnover/WDPA_WithBiomes.gdb/")

# main processing loop
for model in modelList:
    for gcm in gcmList:
        # first calculate zonal stats for current distribution
        outMax_cru = ZonalStatisticsAsTable("WDPA_" + gcm, "WDPAID2", inputPath + model + "_cru_suit.tif",
                        model + "_cru_suit_zoneMax", "DATA", "MAXIMUM")
        arcpy.JoinField_management("WDPA_" + gcm, "WDPAID2", model + "_cru_suit_zoneMax", "WDPAID2", "MAX")
        arcpy.CalculateField_management("WDPA_" + gcm, "suit_sum","[MAX]","VB", "#")
        arcpy.DeleteField_management("WDPA_" + gcm, "MAX")

        # then add the zonal stats from the future distribution
        outMax_gcm = ZonalStatisticsAsTable("WDPA_" + gcm, "WDPAID2", inputPath + model + "_" + gcm + "_suit.tif", 
                        model + "_" + gcm + "_suit_zoneMax", "DATA", "MAXIMUM")
        arcpy.JoinField_management("WDPA_" + gcm, "WDPAID2", model + "_" + gcm + "_suit_zoneMax", "WDPAID2", "MAX")
        arcpy.CalculateField_management("WDPA_" + gcm, "suit_sum","[suit_sum] + [MAX]","VB","#")
        arcpy.DeleteField_management("WDPA_" + gcm, "MAX")

        # tally number of expansions, contractions, and stable distributions per protected area based on values in suit_sum field
        inRaster = ("WDPA_" + gcm)
        rasterDataset = "WDPA_gcm"
        arcpy.MakeRasterLayer_management(inRaster, rasterDataset)
        arcpy.SelectLayerByAttribute_management(rasterDataset, "NEW_SELECTION", '"suit_sum" = 11')
        arcpy.CalculateField_management(rasterDataset, "suit_exp", "!suit_exp! + 1", "PYTHON")
        arcpy.SelectLayerByAttribute_management(rasterDataset, "NEW_SELECTION", '"suit_sum" = 20')
        arcpy.CalculateField_management(rasterDataset, "suit_con", "!suit_con! + 1", "PYTHON")
        arcpy.SelectLayerByAttribute_management(rasterDataset, "NEW_SELECTION", '"suit_sum" = 21')
        arcpy.CalculateField_management(rasterDataset, "suit_stb", "!suit_stb! + 1", "PYTHON")

    # print message for each species model iteration
    print "Model " + model + " is complete."

elapsed = (time.clock() - start)
timestring = str(elapsed/60)
print "Total processing time was " + timestring + " minutes."