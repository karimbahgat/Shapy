
#Testing
import geometry
from geometry import *

def typetesting(VIEWGEOMS=False):
    #-------------------
    #   TYPE TESTING
    #-------------------
    print("#-------------------")
    print("#   TYPE TESTING")
    print("#-------------------")
    
    #point
    point = Point(5, 5)
    print("Point %s"%point.coords)
    print("    area %s"%point.area)
    print("    length %s"%point.length)
    print("    bounds %s"%point.bounds)
    print("")
    if VIEWGEOMS:
        point.view()

    #multipoint
    multipoint = MultiPoint([(3,3),(5,5),(7,7),(3,7),(7,3)])
    print("MultiPoint %s"%multipoint.geoms)
    print("    area %s"%multipoint.area)
    print("    length %s"%multipoint.length)
    print("    bounds %s"%multipoint.bounds)
    print("")
    if VIEWGEOMS:
        multipoint.view()

    #linestring
    linestring = LineString([(1.0,1.0),(15.0,15.0),(10.0,30.0),(55.0,45.0)])
    print("LineString %s"%linestring.coords)
    print("    area %s"%linestring.area)
    print("    length %s"%linestring.length)
    print("    bounds %s"%linestring.bounds)
    print("")
    if VIEWGEOMS:
        linestring.view()

    #multilinestring
    multilinestring = MultiLineString([[(1.0,1.0),(15.0,15.0),(10.0,30.0),(55.0,45.0)], [(1.0,33.0),(15.0,5.0),(10.0,1.0)] ])
    print("MultiLineString %s"%multilinestring.geoms)
    print("    area %s"%multilinestring.area)
    print("    length %s"%multilinestring.length)
    print("    bounds %s"%multilinestring.bounds)
    print("")
    if VIEWGEOMS:
        multilinestring.view()

    #single ring
    ring = LinearRing([(1,1),(1,10),(10,10),(10,1),(1,1)])
    print("LinearRing %s"%ring.coords)
    print("    area %s"%ring.area)
    print("    length %s"%ring.length)
    print("    bounds %s"%ring.bounds)
    if VIEWGEOMS:
        print("rings have no view method")
    print("")

    #polygon with holes
    polygon = Polygon(exterior=[(1,1),(1,10),(10,10),(10,1),(1,1)], interiors=[[(4,4),(4,9),(9,9),(9,4),(4,4)], [(1.2,1.2),(1.2,3.9),(3.9,3.9),(3.9,1.2),(1.2,1.2)]])
    print("Polygon %s"%polygon.exterior.coords)
    print("    area %s"%polygon.area)
    print("    length %s"%polygon.length)
    print("    bounds %s"%polygon.bounds)
    print("")
    if VIEWGEOMS:
        polygon.view()

    #multipolygon with holes
    polygonslist = [( [(1,1),(1,10),(10,10),(10,1),(1,1)], [[(4,4),(4,9),(9,9),(9,4),(4,4)], [(1.2,1.2),(1.2,3.9),(3.9,3.9),(3.9,1.2),(1.2,1.2)]] ),
                    ( [(21,21),(21,30),(30,30),(30,21),(21,21)], [[(24,24),(24,29),(29,29),(29,24),(24,24)], [(21.2,21.2),(21.2,23.9),(23.9,23.9),(23.9,21.2),(21.2,21.2)]] ) ]
    multipolygon = MultiPolygon(polygonslist)
    print("Multipolygon %s"%multipolygon.geoms)
    print("    area %s"%multipolygon.area)
    print("    length %s"%multipolygon.length)
    print("    bounds %s"%multipolygon.bounds)
    print("")
    if VIEWGEOMS:
        multipolygon.view()
    print("")

def distancetesting(VIEWGEOMS=False):
    #-------------------
    #   DISTANCE TESTING
    #-------------------
    print("#-------------------")
    print("#   DISTANCE TESTING")
    print("#-------------------")

    #basic point to point distance test        
    p1 = Point(0,0)
    p2 = Point(100,100)
    dist = p1.distance(p2)
    print("p1 %s -> p2 %s = %s"%(p1.coords[0],p2.coords[0],dist))
    
    #point to multipoint distance test        
    point = Point(0,0)
    multipoint = MultiPoint([(100,100),(70,70),(10,10)])
    dist = point.distance(multipoint, getclosestpoints=True)
    print("p1 %s -> multipoint %s = %s"%(point.coords[0],[each.coords[0] for each in multipoint.geoms],dist))

    #point to line distance test
    point = Point(0.0,0.0)
    line = LineString([(32.0,23.0),(25.0,15.0),(10.0,30.0),(55.0,45.0)])
    result = point.distance(line, getclosestpoints=True)
    print("p1 %s -> line %s = %s"%(point.coords[0],line.coords,result))
    if VIEWGEOMS:
        #WARNING, THE RESULTS SETUP WILL CHANGE SO THIS CODE WILL FAIL
        import pydraw
        css = pydraw.CoordinateSystem([0,0,60,60])
        img = pydraw.Image(400,400,css=css)
        #closestpoint = result["closestpoint_line"]
        img.drawcircle(*point.coords[0], fillsize=15, fillcolor=(222,0,0))
        img.drawgeojson(line)
        #img.drawcircle(*closestpoint.coords[0], fillsize=3, fillcolor=(0,222,0))
        img.view()

    #point to polygon distance test
    point = Point(0.0,0.0)
    polygon = Polygon([(52.0,23.0),(25.0,15.0),(10.0,30.0),(55.0,45.0)])
    result = point.distance(polygon, getclosestpoints=True)
    print("p1 %s -> polygon %s = %s"%(point.coords[0],polygon.exterior.coords,result))

    #point in polygon hole distance test
    point = Point(5,5)
    polygon = Polygon(exterior=[(1,1),(1,10),(10,10),(10,1),(1,1)], interiors=[[(4,4),(4,9),(9,9),(9,4),(4,4)], [(1.2,1.2),(1.2,3.9),(3.9,3.9),(3.9,1.2),(1.2,1.2)]])
    result = point.distance(polygon, getclosestpoints=True)
    print("p1 %s -> inner polygon %s = %s"%(point.coords[0],polygon.exterior.coords,result))
    if VIEWGEOMS:
        #WARNING, THE RESULTS SETUP WILL CHANGE SO THIS CODE WILL FAIL
        import pydraw
        css = pydraw.CoordinateSystem([0,0,11,11])
        img = pydraw.Image(400,400,css=css)
        #closestpoint = result["closestpoint_line"]
        img.drawcircle(*point.coords[0], fillsize=15, fillcolor=(222,0,0))
        img.drawgeojson(polygon)
        #img.drawcircle(*closestpoint.coords[0], fillsize=3, fillcolor=(0,222,0))
        img.view()

    print("")

def buffertesting(VIEWGEOMS=False):
    #-------------------
    #   BUFFER TESTING
    #-------------------
    print("#-------------------")
    print("#   BUFFER TESTING")
    print("#-------------------")

    #single polygon buffer test
    polygon = Polygon(exterior=[(10,10),(100,10),(100,100),(10,100)], interiors=[[(20,20),(20,90),(90,90),(90,20)]])
    print("pre-buffer %s"%polygon)
    if VIEWGEOMS:
        polygon.view()
    #
    polygon_buffer = polygon.buffer(buffersize=9)
    print("buffer %s"%polygon_buffer)
    if VIEWGEOMS:
        polygon_buffer.view()

    #multipolygon buffer test
    polygonslist = [( [(30.0,30.0),(50.0,30.0),(50.0,50.0),(30.0,50.0)], [] ),
                    ( [(60.0,60.0),(80.0,60.0),(80.0,80.0),(60.0,80.0)], [] )]
    multipolygon = MultiPolygon(polygonslist)
    print("pre-buffer %s"%multipolygon)
    if VIEWGEOMS:
        multipolygon.view()
    #
    multipolygon_buffer = multipolygon.buffer(buffersize=9)
    print("multibuffer %s"%multipolygon_buffer)
    if VIEWGEOMS:
        multipolygon_buffer.view()
    print("")

def uniontesting(VIEWGEOMS=False):
    #-------------------
    #   UNION TESTING
    #-------------------
    print("#-------------------")
    print("#   UNION TESTING")
    print("#-------------------")
    
    #simple union test
    u1 = Polygon(exterior=[(10,10),(100,10),(100,100),(10,100)], interiors=[[(20,20),(20,90),(90,90),(90,20)]])
    polygonslist = [( [(30.0,30.0),(50.0,30.0),(50.0,50.0),(30.0,50.0)], [] ),
                    ( [(60,60),(80,60),(80,80),(60,80)], [] )]
    u2 = MultiPolygon(polygonslist)
    result = u1.union(u2)
    print("union %s"%result)
    if VIEWGEOMS:
        result.view()

    #test multiple cumulative union on entire shapefile
    print("")
    print("cumulative union:")
    # setup image drawer
    import pydraw
    css = pydraw.CoordinateSystem([-180,90,180,-90])
    img = pydraw.Image(1000,500, background=(0,0,111), css=css)
    # load and loop shapefile
    import geovis.shapefile_fork as pyshp
    cshapesfile = "D:/Test Data/cshapes/cshapes.shp"
    natearthfile = "D:/Test Data/necountries/necountries.shp"
    linesfile = "D:/Test Data/lines/ne_50m_rivers_lake_centerlines.shp"
    pointfile = "D:/Test Data/gtd_georef/gtd_georef.shp"
    reader = pyshp.Reader(cshapesfile)
    oldshape = False
    stopindex = 9
    for index,shape in enumerate(reader.iterShapes()):
        geotype = shape.__geo_interface__["type"]
        geom = geoj2geom(shape)
        #add to cumulative union
        if oldshape:
            union = oldshape.union(geom)
            print("    %s"%union)
            try:
                img.drawgeojson(union) #img.drawgeojson(geom)
                oldshape = union
            except:
                #img2 = pydraw.Image(1000,500, background=(0,0,111), css=css)
                #img2.drawgeojson(oldshape, fillcolor=(0,222,0))
                #img2.drawgeojson(geom, fillcolor=(222,0,0))
                #img2.view()
                pass
        else:
            oldshape = geom
        if index == stopindex:
            if VIEWGEOMS:
                img.drawgeojson(union)
                img.view()
                union.view(css=css)
            break
    img.view()

def RunTestSuite(VIEWGEOMS=True):

    ##################################################
    #BEGIN TESTING
    typetesting(VIEWGEOMS=VIEWGEOMS)
    distancetesting(VIEWGEOMS=VIEWGEOMS)
    buffertesting(VIEWGEOMS=VIEWGEOMS)
    uniontesting(VIEWGEOMS=VIEWGEOMS)
    print("----------------------------")
    print("TESTS SUCCESSFULLY COMPLETED")
    ###################################################

if __name__ == "__main__":
    
    #distancetesting(True)
    #uniontesting(False)
    RunTestSuite(VIEWGEOMS=False)



