# SoSe2015_GIS
Transfer exercise in ArgGIS-Python programming:
## Waterbody Statistics
### (Polygon Statistics)

#### Operating Instructions
1. Download the sourcecode.
2. Fire up ArcGIS and point your homefolder to the root of the downloaded source.
3. Despite having some default input and output parameters set, the tool requires absolute pathes!
So please browse to the test data & output folders and select the according files / type in the output filenames (those must not be preexisting!) as the default settings indicate. 

#### Input
The script currently is designed to take input featureclasses as provided here:

http://dds.cr.usgs.gov/srtm/version2_1/SWBD/

#### Accepted Coordinate Reference Systems
The Tool accepts featureclasses of any CRS. 
If the CRS is unknown, WGS84 will be assumed.
For proper calculation of geodesic areas, the input file has to be in a *projected* CRS. The tool takes care of the reprojection if it is not. 

#### Output
Rather self-explanatory. 
Have a look at the Field "Incomplete" (output featureclass) or "Randlage" (out.csv):
This one tells, if the polygon touches the tile's extent rectangle - and *possibly* is only part of a larger waterbody. You will have to examine the neighbouring tiles to check, whether the waterbody is extending into them and merge/dissolve them into a larger featureclass. 
