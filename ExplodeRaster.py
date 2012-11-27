##Author: Jesse Langdon
##Title: Explode Raster
##Contact: jesselangdon@gmail.com
##Description: Takes an raster with integer values (representing classes, themes, etc.)
##             and outputs an separate raster dataset for each value.

# Load Python libraries          
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

# set the environment, raster dataset and output folder based on user input
inRaster = arcpy.GetParameterAsText(1)
outLocation = arcpy.GetParameterAsText(2)
arcpy.env.mask = arcpy.GetParameterAsText(3)
extractVal = arcpy.GetParameterAsText(4)
nodataVal = arcpy.GetParameterAsText(5)
extractIntVal = int(extractVal)
nodataIntVal = int(nodataVal)
env.workspace = arcpy.GetParameterAsText(2)

# open a search cursor to collect all the raster values in the input raster dataset.
rows = arcpy.SearchCursor(inRaster, "", "", "VALUE", "")

# iterate through rows in the cursor, extract each raster value to a new raster dataset.
for row in rows:
    rowString = str(row.VALUE)
    SQLclause = "VALUE =" + rowString
    rasExtract = ExtractByAttributes(inRaster, SQLclause)
    remap = arcpy.sa.RemapValue([[row.VALUE, extractIntVal], ["NoData", nodataIntVal]])
    reclass = Reclassify(rasExtract, "VALUE", remap, "Data")
    reclass.save(outLocation + "/" + rowString + "extract.tif")

elapsed = (time.clock() - start)
timestring = str(elapsed/60)
print "Total processing time was " + timestring + " minutes."