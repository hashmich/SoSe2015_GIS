#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Stefan, Hendrik, Sven'

import arcpy

# define function that is used later to check, if polygon reaches extent of tile
def touchesClassBoundary(feature, classExtent):
    result = False
    featureExtent = feature.extent
    if(   featureExtent.XMin <= classExtent.XMin
       or featureExtent.XMax >= classExtent.XMax
       or featureExtent.YMin <= classExtent.YMin
       or featureExtent.YMax >= classExtent.YMax):
        result = True
    return result


# set input and output
fc_in1 = arcpy.GetParameterAsText(0)
fc_out  = arcpy.GetParameterAsText(1)
fc_out_csv_name = arcpy.GetParameterAsText(2)


### 1) preparing input data for statistic calculation ###

# define temporary file used for merging
tmp_fc_name = 'in_memory/tmp7'
tmp_fc_name2 = 'in_memory/tmp6'

# merge polygons
try:
    if len(fc_in1) > 1:
        arcpy.Merge_management(fc_in1, tmp_fc_name)
        fc_in = arcpy.Dissolve_management(tmp_fc_name,tmp_fc_name2,"FACC_Code", "","SINGLE_PART")
    else:
        arcpy.CopyFeatures_management(fc_in1, tmp_fc_name)
        fc_in = tmp_fc_name
except:
    arcpy.Delete_management("in_memory")
# check if input featureclass has any spatial reference system set. Assume WGS 84 otherwise
sr = arcpy.Describe(fc_in).spatialReference
if(sr.type == 'Unknown'):
    sr = arcpy.SpatialReference("WGS 1984")
    arcpy.DefineProjection_management(fc_in, sr)

# if spatial reference type is 'Geographic', perform transformation. Otherwise sr would be 'Projected',
# which is a requirement to correctly calculate GEODESIC polygon areas & lengths
sr = arcpy.Describe(fc_in).spatialReference
if(sr.type == 'Geographic'):
    # perform reprojection into a projected CRS
    sr = arcpy.SpatialReference("Azimuthal Equidistant (world)")
    arcpy.Project_management(fc_in, fc_out, sr)

arcpy.Delete_management("in_memory")

# retieving the featureClass' extent
dsc = arcpy.Describe(fc_out)
fc_extent = dsc.extent

# add columns in which calculated statistics will be stored
# alternative: Polygon(arcpy).getArea('GEODESIC', 'SQUAREKILOMETERS ') - just returns the value (use cursor)
arcpy.AddField_management(fc_out, "water_expa", "DOUBLE")       # area takes into account inner polygon-rings (islands are substracted from the overall area)
arcpy.AddField_management(fc_out, "total_area", "DOUBLE")       # total water body area
arcpy.AddField_management(fc_out, "Perimeter", "DOUBLE")        # outer perimeter
arcpy.AddField_management(fc_out, "coast_line", "DOUBLE")       # coast length including all inner polygon rings
arcpy.AddField_management(fc_out, 'Incomplete', 'SHORT', 1)     # if the shape touches the featureclass' outer boundary and might be incomplete


### 2) calculation of water body statistics ###

# CalculateField_management stores value on the just created fields
# a loop is not needed here, the CalculateField_management() method iterates over all features on it's own
arcpy.CalculateField_management(fc_out, "water_expa", "!shape.geodesicArea@SQUAREKILOMETERS!", "PYTHON_9.3", "#")
arcpy.CalculateField_management(fc_out, "coast_line", "!shape.geodesicLength@KILOMETERS!", "PYTHON_9.3", "#")


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
            row.total_area = poly.getArea('Geodesic') / 1000000
        del outerRing_array
        break   # there should be no other parts

    # check if feature reaches featureclass extent - mark as (possibly) incomplete if it does
    row.Incomplete = 1 if(touchesClassBoundary(row.SHAPE, fc_extent)) else 0
    rows.updateRow(row)     # save perimeter & completeness

# tidy locks & memory
del row
del rows


### 3) create output ###

# create dictionary to assign FACC codes with water body type
FACC_C = {"BA040" : "sea", "BH080" : "lake", "BH140" : "river"}

# if input name for table output isn't empty, open file to store statistics as table
if fc_out_csv_name != '':
    fc_out_csv = open(fc_out_csv_name, 'w')
    fc_out_csv.write("Water Body_ID;water_expanse[km^2];total_area[km^2];coast_line[km];Perimeter[km];Type;Incompletness\n")
# store statistics in table file
search  = arcpy.SearchCursor(fc_out)
for row in search:
    if fc_out_csv_name != '':
        fc_out_csv.write("%s;%s;%s;%s;%s;%s;%s\n" % (row.FID,
                                            round(row.water_expa,3),
                                            round(row.total_area,3),
                                            round(row.coast_line,3),
                                            round(row.Perimeter,3),
                                            FACC_C[row.FACC_CODE],
                                            row.Incomplete)
                     )

# close table file
if fc_out_csv_name != '':
    fc_out_csv.close()
