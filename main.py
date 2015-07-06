#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Stefan, Hendrik, Sven'


import arcpy
from arcpy import env

#Workpace Uni oder daheim.
import config
env.workspace = config.workspace
env.overwriteOutput = True


#Input festlegen
fc_in = arcpy.GetParameterAsText(0)
##fc_in   = "Data/e000n05f.shp"      #muss in fc_in umbenannt werden, falls Umprojektion von WGS84 in anderes Koordinatensystem erfolgt
##fc_out   = "Results/fc_out.shp"     #wird benötigt, falls Umprojektion von WGS84 in anderes Koordinatensystem erfolgt
fc_out  = arcpy.GetParameterAsText(1)
###fc_out_csv = open("E:/Studium neu/Studium/GIS-Programmierung/Projekt/Results/Gewaesser.csv", "w+")
fc_out_csv = arcpy.GetParameterAsText(2)

#Koordinatensystem festlegen
sr = arcpy.SpatialReference("WGS 1984")
sr_transform = arcpy.SpatialReference("Azimuthal Equidistant (world)")
#prjfile = "Data/WGS 1984.prj"
arcpy.DefineProjection_management(fc_in, sr)
#Umprojektion in flächentreues Koordinatensystem
arcpy.Project_management(fc_in, fc_out, sr_transform)

#Datei in gewünschten Ordner kopieren
#fc      = arcpy.CopyFeatures_management(fc_in, fc_out)

#Felder hinzufügen, in denen Statistiken gespeichert werden sollen
#(NUR NÖTIG, WENN FELD BERECHNEN ALS METHODE VERWENDET WIRD)
arcpy.AddField_management(fc_out, "Area", "SHORT")      #Fläche
arcpy.AddField_management(fc_out, "Perimeter", "FLOAT") #Umfang


#Statistiken berechnen
#Mit Calculate Areas Tool
#arcpy.CalculateAreas_stats(fc, "Results/test.shp")

#Mit "Feld berechnen". Fügt der bestehenden Datei in Tabellenfeld Werte hinzu
updateArea = arcpy.da.UpdateCursor(fc_out, ["Area"])
for row in updateArea:
    arcpy.CalculateField_management(fc_out, "Area", "!shape.geodesicArea@SQUAREMETERS!", "PYTHON_9.3", "#")

updatePerimeter = arcpy.da.UpdateCursor (fc_out, ["Perimeter"])
for row in updatePerimeter:
    arcpy.CalculateField_management(fc_out, "Perimeter", "!shape.geodesicLength@KILOMETERS!", "PYTHON_9.3", "#")



#Statistiken ausgeben
search  = arcpy.da.SearchCursor(fc_out, ["FID", "Area", "Perimeter", "FACC_CODE"])
FACC_C = {"BA040" : "Meer", "BH080" : "See", "BH140" : "Fluss"}

fc_out_csv.write("Gewässer_ID;Fläche [m^2];Umfang[km];Gewässertyp\n")
for row in search:
    print "Die Fläche von Gewässer", row[0], "beträgt", int(round(row[1],0)), "Quadratmeter und der Umfang", round(row[2],3), "Kilometer. Es handelt sich hierbei um ein(en)", FACC_C[row[3]]+"."
    fc_out_csv.write("%s;%s;%s;%s\n" % (row[0], int(round(row[1],0)), round(row[2],3), FACC_C[row[3]]))

fc_out_csv.close()
