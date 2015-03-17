import py2d,py2d.Math
import random
import geovis
import geovis.shapefile_fork as pyshp

shape = pyshp.Reader("D:/Test Data/cshapes/cshapes.shp").shape(1)
p = py2d.Math.Polygon.from_pointlist(py2d.Math.Polygon.simplify_sequence(py2d.Math.Polygon.from_tuples(shape.points)))
p_buf = p.offset(p, -0.15) #before mod, works up until 0.3 but going further gives empty result

##coords = list(reversed([(10,10),(90,10),(80,90),(50,60),(20,77)]))
##p = py2d.Math.Polygon.from_tuples(coords)
##p_buf = py2d.Math.Polygon.offset(p, 15.12) #before mod, works up until 0.3 but going further gives empty result

###
import pydraw
crs = pydraw.CoordinateSystem(shape.bbox)#[0,100,100,0])
img = pydraw.Image(500,500,crs=crs)
for eachbuf in p_buf:
    img.drawpolygon(eachbuf.as_tuple_list(), fillcolor=(222,0,0),outlinecolor=(0,0,0))
img.drawpolygon(p.as_tuple_list(), fillcolor=None, outlinecolor=(0,222,0))
img.view()#save("C:/Users/BIGKIMO/Desktop/buftest.png")
