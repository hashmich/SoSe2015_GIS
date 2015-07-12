#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Stefan, Hendrik, Sven'


import arcpy
from arcpy import env
import os
env.workspace = os.path.dirname(os.path.realpath(__file__))   # os.getCwd() returns the wrong path when ran under ArcGIS
env.scratchWorkspace = env.workspace
env.overwriteOutput = True


def touchesClassBoundary(feature, classExtent):
    featureExtent = feature.extent
    if(   featureExtent.XMin <= classExtent.XMin
       or featureExtent.XMax >= classExtent.XMax
       or featureExtent.YMin <= classExtent.YMin
       or featureExtent.YMax >= classExtent.YMax):
        return True
    return False


#Input und Output festlegen
fc_in = arcpy.GetParameterAsText(0)
fc_out  = arcpy.GetParameterAsText(1)
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
# which is a requirement to correctly calculate GEODESIC polygon areas & lengths
sr = arcpy.Describe(fc_in).spatialReference
if(sr.type == 'Geographic'):
    # perform reprojection into a projected CRS
    sr = arcpy.SpatialReference("Azimuthal Equidistant (world)")
    arcpy.Project_management(fc_in, fc_out, sr)

# retieving the featureClass' extent
dsc = arcpy.Describe(fc_out)
fc_extent = dsc.extent

#Felder hinzufügen, in denen Statistiken gespeichert werden sollen
# alternative: Polygon(arcpy).getArea('GEODESIC', 'SQUAREKILOMETERS ') - just returns the value (use cursor)
arcpy.AddField_management(fc_out, "Area", "DOUBLE")         # area takes into account inner polygon-rings (islands are substracted from the overall area)
arcpy.AddField_management(fc_out, "Perimeter", "DOUBLE")    # outer perimeter
arcpy.AddField_management(fc_out, "Length", "DOUBLE")    # coast length including all inner polygon rings
arcpy.AddField_management(fc_out, 'Incomplete', 'SHORT', 1)    # if the shape touches the featureclass' outer boundary and might be incomplete
#Statistiken berechnen
# CalculateField_management stores value on the just created fields
# a loop is not needed here, the CalculateField_management() method iterates over all features on it's own
arcpy.CalculateField_management(fc_out, "Area", "!shape.geodesicArea@SQUAREKILOMETERS!", "PYTHON_9.3", "#")
arcpy.CalculateField_management(fc_out, "Length", "!shape.geodesicLength@KILOMETERS!", "PYTHON_9.3", "#")


# difference between arcpy.Cursor & arcpy.da.Cursor:
# arcpy.Cursor allows to resolve row fields like this: row.Perimeter - arcpy.da.Cursor uses numerical indices instead
rows = arcpy.UpdateCursor(fc_out)
for row in rows:
    # calculating the perimeter - this takes into account only the outer ring(s)
    # SHAPE is not a fieldname, but references the field containing the shape object
    for part in row.SHAPE:
        poly = arcpy.Polygon(part)  # <--Create polygon object from part
        outerRing_array = arcpy.Array()
        for pnt in part:
            if pnt is None: # starting an interior ring
                break
            else:
                outerRing_array.add(pnt)
        if(len(outerRing_array) > 0):
            # create the outer polygon with the CRS used before
            poly = arcpy.Polygon(outerRing_array, sr)
            row.Perimeter = poly.getLength('GEODESIC') / 1000  # get length converted to kilometers

        del outerRing_array
        break   # there should be no other parts

    # check if feature reaches featureclass extent - mark as (possibly) incomplete if it does
    row.Incomplete = 1 if(touchesClassBoundary(row.SHAPE, fc_extent)) else 0
    rows.updateRow(row)     # save perimeter & completeness

# tidy locks & memory
del row
del rows


#Statistiken ausgeben
search  = arcpy.SearchCursor(fc_out)
FACC_C = {"BA040" : "Meer", "BH080" : "See", "BH140" : "Fluss"}

fc_out_csv = open(fc_out_csv_name, 'w')
fc_out_csv.write("Gewässer_ID;Fläche[km^2];Umfang[km];Uferlänge[km];Gewässertyp;Randlage\n")
for row in search:
    fc_out_csv.write("%s;%s;%s;%s;%s;%s\n" % (row.FID,
                                        round(row.Area,3),
                                        round(row.Perimeter,3),
                                        round(row.Length,3),
                                        FACC_C[row.FACC_CODE],
                                        row.Incomplete)
                     )
    print "Waterbody "+str(row.FID)+\
          ", Area "+str(round(row.Area,3))+\
          "km^2, CoastLength "+str(round(row.Length,3))+\
          "km, Perimeter "+str(round(row.Perimeter,3))+\
          ", Type "+FACC_C[row.FACC_CODE]+\
          ", incomplete "+str(row.Incomplete)+"."
fc_out_csv.close()



