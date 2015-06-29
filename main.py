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
fc  = "Data/e000n05f.shp"

#Koordinatensystem festlegen
prjfile = "Data/WGS 1984.prj"
arcpy.DefineProjection_management(fc, prjfile)

#Felder hinzufuegen, in denen Statistiken gespeichert werden sollen
#(NUR NoeTIG, WENN FELD BERECHNEN ALS METHODE VERWENDET WIRD)
arcpy.AddField_management(fc, "Area", "LONG")      #Fläche
arcpy.AddField_management(fc, "Perimeter", "LONG") #Umfang


#Statistiken berechnen

#Mit Calculate Areas Tool
#arcpy.CalculateAreas_stats(fc, "Results/test.shp")

#Mit Feld berechnen. Fügt der bestehenden Datei in Tabellenfeld Werte hinzu
update = arcpy.da.UpdateCursor(fc, ["Area"])
for row in update:
    arcpy.CalculateField_management(fc, "Area", "!shape.area@SQUAREMETERS!")
