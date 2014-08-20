import py2d,py2d.Math
import random
import geovis
import geovis.shapefile_fork as pyshp

shape = pyshp.Reader("D:/Test Data/cshapes/cshapes.shp").shape(1)

p = py2d.Math.Polygon.from_pointlist(py2d.Math.Polygon.simplify_sequence(py2d.Math.Polygon.from_tuples(shape.points)))
p_buf = p.offset(p, -0.08) #before mod, works up until 0.3 but going further gives empty result

###
import pydraw
crs = pydraw.CoordinateSystem(shape.bbox)
img = pydraw.Image(900,900,crs=crs)
img.drawpolygon(p.as_tuple_list(), fillcolor=(0,222,0))
for eachbuf in p_buf:
    img.drawpolygon(eachbuf.as_tuple_list(), fillcolor=(222,0,0))

img.save("C:/Users/BIGKIMO/Desktop/buftest.png")
