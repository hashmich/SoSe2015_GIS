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
fc   = "Data/e144s26a.shp"      #muss in fc_in umbenannt werden, falls Umprojektion von WGS84 in anderes Koordinatensystem erfolgt
#fc  = "Results/fc_out.shp"     #wird benötigt, falls Umprojektion von WGS84 in anderes Koordinatensystem erfolgt

#Koordinatensystem festlegen
prjfile = "Data/WGS 1984.prj"
arcpy.DefineProjection_management(fc, prjfile)
#Umprojektion in flächentreues Koordinatensystem
#arcpy.Project_management(fc_in, fc, "Data/AziEqui.prj")

#Felder hinzufügen, in denen Statistiken gespeichert werden sollen
#(NUR NÖTIG, WENN FELD BERECHNEN ALS METHODE VERWENDET WIRD)
arcpy.AddField_management(fc, "Area", "FLOAT")      #Fläche
arcpy.AddField_management(fc, "Perimeter", "FLOAT") #Umfang


#Statistiken berechnen

#Mit Calculate Areas Tool
#arcpy.CalculateAreas_stats(fc, "Results/test.shp")

#Mit "Feld berechnen". Fügt der bestehenden Datei in Tabellenfeld Werte hinzu
updateArea = arcpy.da.UpdateCursor(fc, ["Area"])
for row in updateArea:
    arcpy.CalculateField_management(fc, "Area", "!shape.geodesicArea@SQUAREMETERS!", "PYTHON_9.3", "#")

updatePerimeter = arcpy.da.UpdateCursor (fc, ["Perimeter"])
for row in updatePerimeter:
    arcpy.CalculateField_management(fc, "Perimeter", "!shape.geodesicLength@KILOMETERS!", "PYTHON_9.3", "#")



#Statistiken ausgeben
search  = arcpy.da.SearchCursor(fc, ["FID", "Area", "Perimeter"])
for row in search:
    print "Die Fläche von Gewässer", row[0], "beträgt", round(row[1],0), "Quadratmeter und der Umfang", round(row[2],3), "Kilometer."
