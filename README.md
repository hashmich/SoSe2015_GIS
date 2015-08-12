# SoSe2015_GIS
Transfer exercise in ArgGIS-Python programming:
## Waterbody Statistics
### (Polygon Statistics)

### Presentation on Prezi.com
http://prezi.com/cto12a3w6tro/?utm_campaign=share&utm_medium=copy

#### Operating Instructions
1. Download the sourcecode.
2. Fire up ArcGIS and point your homefolder to the root of the downloaded source.
3. Despite having some default input and output parameters set, the tool requires absolute pathes!
So please browse to the test data & output folders and select the according files / type in the output filenames (those must not be preexisting!) as the default settings indicate. 
4. Add the folder "Results" to the source root if required. 

#### Input
The script currently is designed to take input featureclasses (tiles) as provided here:

http://dds.cr.usgs.gov/srtm/version2_1/SWBD/

The tool accepts multi-values for the input featureclass. So you may enter several tiles, which will be merged and dissolved by their FACC code into a single featureclass. This functionality is of interest, if watershed features you're describing are depicted across several tiles. 
The merging condition field is currently hardcoded, but can be passed as an input parameter to make the tool more generic.

Select an absolute path and filename for the output featureclass and CSV output. 
THE DEFAULT VALUES REFUSE TO WORK and are just an indication of what you are supposed to enter. (Funny though, that you'll get the right folder opened when browsing, if you got your homefolder settings right.)
The output files/filenames must not exist before the script is running. 

#### Feature-Tile Coverage & Tile Merging
As you might be interested, if a particular polygon is fully covered by the tile in effect, the tool introduces a field named 'incomplete' in the output featureclass as well as in the CSV. The value of this field will be [INT 1] if the polygon touches the extent of the tile, [INT 0] if not.
So if you find the polygon you're interested in is indicated as incomplete, you might consider looking at the neighbouring tile as well. So just add it's filename to the input, the tool will merge everything into a single tile. 

#### Accepted Coordinate Reference Systems
The Tool accepts featureclasses of any CRS. 
If the CRS is unknown, WGS84 will be assumed.
For proper calculation of geodesic areas, the input file has to be in a *projected* CRS. The tool takes care of the reprojection if it is not. 

#### Output
Rather self-explanatory. 
Have a look at the Field "Incomplete" in the output featureclass):
This one tells, if the polygon touches the tile's extent rectangle - and *possibly* is only part of a larger waterbody. You will have to examine the neighbouring tiles to check, whether the waterbody is extending into them and merge/dissolve them into a larger featureclass. This can be done by the tool itself, just select multiple input featureclasses. 
