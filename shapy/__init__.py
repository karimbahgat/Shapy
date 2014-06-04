"""
# Shapy

v0.1

Author: Karim Bahgat

Year: 2014


## Description:

A lightweight and portable pure-Python version of Shapely for geometry processing.


## Introduction:

As the name suggests, Shapy is a pure-Python version of Shapely. 

Based on and modelled precisely after Shapely, so should be easy to use 
by those familiar with Shapely...

Also some functionality that's not available in Shapely.


## Dependencies:

Absolutely no dependencies, though it probably won't work on Python3 yet. 


## Usage:

The package is not yet complete. Currently the supported features are:

- All shapely geometries can be created (Point,MultiPoint,LineString,MultiLineString,Polygon,MultiPolygon)
- All geometries have the basic shapely attributes with correct values:
  - .geom_type, .bounds, .area, .length
  - all geometries also have the .__geo_interface__ geojson attribute
- Easily visualize all geometries with the .view() method. Note: The coordinate converter has some quirks so might not show the shape correctly or at all. 
- Easily make geometries from real shapefiles by passing any object that has the __geo_interface__ to the `geoj2geom(object)` function.
- Point geometries can use the .distance() method to any other geometry.
- The intersect(), union(), difference(), symmetric_difference() methods can be used by Polygon and MultiPolygon geometries, but currently only with other Polygon or MultiPolygon geometries.
- The buffer() method can be used by Polygons and MultiPolygons. 

Docs are not yet completed, but just follow the shapely usage and names and
you should be alright. 

There's still a few things left to add, so it would be great if others could contribute some of the remaining functionality. 

"""

from geometry import *
from tester import *

