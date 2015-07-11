#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Stefan, Hendrik, Sven'


import arcpy
from arcpy import env
import os
env.workspace = os.getcwd()
env.overwriteOutput = True


#Input festlegen
fc_in = arcpy.GetParameterAsText(0)
##fc_in   = "Data/e000n05f.shp"      #muss in fc_in umbenannt werden, falls Umprojektion von WGS84 in anderes Koordinatensystem erfolgt
##fc_out   = "Results/fc_out.shp"     #wird benötigt, falls Umprojektion von WGS84 in anderes Koordinatensystem erfolgt
fc_out  = arcpy.GetParameterAsText(1)
###fc_out_csv = open("E:/Studium neu/Studium/GIS-Programmierung/Projekt/Results/Gewaesser.csv", "w+")
fc_out_csv_name = arcpy.GetParameterAsText(2)

tmp_fc_name = os.path.join(env.workspace, 'Results/fc_in_wgs84.shp')


# check if input featureclass has any spatial reference system set. Assume WGS 84 otherwise
sr = arcpy.Describe(fc_in).spatialReference
if(sr.type == 'Unknown'):
    arcpy.CopyFeatures_management(fc_in, tmp_fc_name)
    fc_in = tmp_fc_name
    sr = arcpy.SpatialReference("WGS 1984")
    arcpy.DefineProjection_management(fc_in, sr)

# if spatial reference type is 'Geographic', perform transformation. Otherwise sr would be 'Projected',
# which is a requirement to correctly calculate the polygon areas
sr = arcpy.Describe(fc_in).spatialReference
if(sr.type == 'Geographic'):
    # perform reprojection into a projected CRS
    sr_transform = arcpy.SpatialReference("Azimuthal Equidistant (world)")
    #arcpy.Project_management(fc_in, fc_out, sr_transform)


#Datei in gewünschten Ordner kopieren
#arcpy.CopyFeatures_management(fc_in, os.path.join(env.workspace, fc_out))

#Felder hinzufügen, in denen Statistiken gespeichert werden sollen
#(NUR NÖTIG, WENN FELD BERECHNEN ALS METHODE VERWENDET WIRD)
# alternative: Polygon(arcpy).getArea('GEODESIC', 'SQUAREKILOMETERS ') - just returns the value (use cursor)
arcpy.AddField_management(fc_out, "Area", "DOUBLE")         #Fläche
arcpy.AddField_management(fc_out, "Perimeter", "DOUBLE")    #Umfang
arcpy.AddField_management(fc_out, 'Incomplete', 'SHORT', 1)    # if the shape touches the featureclass' outer boundary and might be incomplete
#Statistiken berechnen
#Mit "Feld berechnen". Stores value on the just created fields.
rows = arcpy.da.UpdateCursor(fc_out, ["Area", "Perimeter", 'Incomplete'])
for row in rows:
    arcpy.CalculateField_management(fc_out, "Area", "!shape.geodesicArea@SQUAREKILOMETERS!", "PYTHON_9.3", "#")
    arcpy.CalculateField_management(fc_out, "Perimeter", "!shape.geodesicLength@KILOMETERS!", "PYTHON_9.3", "#")
# tidy locks & memory
del row
del rows


#Statistiken ausgeben
search  = arcpy.da.SearchCursor(fc_out, ["FID", "Area", "Perimeter", "FACC_CODE"])
FACC_C = {"BA040" : "Meer", "BH080" : "See", "BH140" : "Fluss"}

fc_out_csv = open(fc_out_csv_name, 'w')
fc_out_csv.write("Gewässer_ID;Fläche[km^2];Umfang[km];Gewässertyp\n")
for row in search:
    print "Die Fläche von Gewässer", row[0], "beträgt", round(row[1],3), "Quadratkilometer und der Umfang", round(row[2],3), "Kilometer. Es handelt sich hierbei um ein(en)", FACC_C[row[3]]+"."
    fc_out_csv.write("%s;%s;%s;%s\n" % (row[0], round(row[1],3), round(row[2],3), FACC_C[row[3]]))
fc_out_csv.close()
