#The geometry instances for clippy

#import stuff
import itertools, math
import clipper

#global settings
PRECISION = 1000000000

#helper functions
def _flatten(coords):
    """
    Flattens the coordinate pairs from Pyshp so they can be used by clipper
    """
    return list(itertools.chain.from_iterable(coords))
def _Floats2Ints(coords):
    precision = PRECISION
    return map(int,[xory*precision for xory in coords])
def _Ints2Floats(coords):
    #returns as pairs
    precision = PRECISION
    return [(point.x/float(precision),point.y/float(precision)) for point in coords]
def _PrepCoords(coords, convertfloats=True):
    if convertfloats:
        return clipper.IntsToPoints(_Floats2Ints(_flatten(coords)))
    else:
        return clipper.IntsToPoints(_flatten(coords))
def _ResultTree2Geom(resulttree):
    def node2geom(node):
        childcount = node.ChildCount
        if childcount > 0:
            resultlist = []
            #collect results as a list of exterior-interiors tuples
            for nodechild in node.Childs:
                exterior = _Ints2Floats(nodechild.Contour)
                nodeholes = nodechild.Childs
                interiors = []
                for hole in nodeholes:
                    interiors.append( _Ints2Floats(hole.Contour) )
                    #check if any subpolygons inside the hole and add to results
                    subpolys = node2geom(hole)
                    if subpolys:
                        resultlist.extend( subpolys )
                resultlist.append( (exterior, interiors) )
            return resultlist
    resultlist = node2geom(resulttree)
    if resultlist:
        if len(resultlist) == 1:
            exterior,interiors = resultlist[0]
            geom = Polygon(exterior, interiors)
        elif len(resultlist) > 1:
            geom = MultiPolygon(resultlist)
        return geom
def _Clip(subjectgeom, clipgeom, cliptype,
         txt2cliptype=dict([
            ("intersect",0),
            ("union",1),
            ("difference",2),
            ("exclusive_or",3)
            ])):
    """
    Note: this clip function now requires coordinate pairs ala Pyshp
    
    - subjectpolys is the main shape to be compared with another one
    - clippolys is the shape to be compared with
    - cliptype can be "intersect","union","difference", or "exclusive_or"
    """
    cliptype = txt2cliptype[cliptype]
    # prepare clipper and add geoms
    main = clipper.Clipper()
    subjectgeom._addtoclipper(main, clipper.PolyType.Subject)
    clipgeom._addtoclipper(main, clipper.PolyType.Clip)
    # run clip operation
    resulttree = clipper.PolyTree()
    main.Execute2(cliptype, resulttree, clipper.PolyFillType.Positive, clipper.PolyFillType.Positive) #main._ClipType
    # make geom from resulttree
    topnode = resulttree
    geom = _ResultTree2Geom(topnode)
    return geom


#user functions
def geoj2geom(geojson):
    geotype = geojson["type"]
    coords = geojson["coordinates"]
    if geotype == "Polygon":
        exterior = coords[0]
        interiors = []
        if len(coords) > 1:
            interiors.extend(coords[1:])
        geom = Polygon(exterior, interiors)
    elif geotype == "MultiPolygon":
        multipolylist = []
        for eachmulti in coords:
            exterior = eachmulti[0]
            interiors = []
            if len(eachmulti) > 1:
                interiors.extend(eachmulti[1:])
            polylist = (exterior, interiors)
            multipolylist.append(polylist)
        geom = MultiPolygon(multipolylist)
    return geom

#define geometry classes
class Point:
    #NOT FINISHED
    def __init__(self, x, y):
        self.geom_type = "Point"
        #prep coords for clip analysis
        coords = [x,y]
        preppedcoords = _PrepCoords([coords])
        #then set properties
        self.coords = coords
        self._coords = preppedcoords
        self.area = 0.0
        self.length = 0.0
        self.bounds = [x,y,x,y]
        self.x = x
        self.y = y
    def buffer(self, buffersize, jointype="miter"):
        jointypes = dict([("bevel",clipper.JoinType.Square),
                          ("round",clipper.JoinType.Round),
                          ("miter",clipper.JoinType.Miter)])
        jointype = jointypes[jointype]
        #prep coords
        preppedpoint = _PrepCoords([self.coords], convertfloats=False)
        #execute buffer
        resulttree = clipper.OffsetPoint(preppedpoint, buffersize, jointype=jointype)
        #finally create and return geom
        geom = _ResultTree2Geom(resulttree)
        #   for lines use .OffsetPolyLines
        #   for points use the _DoRound(pt, limit) function from inside _OffsetInternal
        return geom

class MultiPoint:
    #NOT FINISHED
    def __init__(self, points):
        pass
        
class LineString:
    #NOT FINISHED
    def __init__(self, coordinates):
        self.geom_type = "LineString"
        #prep coords for clip analysis
        preppedcoords = _PrepCoords(coordinates)
        floatcoords = _PrepCoords(coordinates, convertfloats=False)
        #get bounds
        rectobj = clipper._GetBounds([floatcoords]) #must wrap in list bc _GetBounds takes a list of polygons
        _bounds = (rectobj.left, rectobj.top, rectobj.right, rectobj.bottom)
        #then set properties
        self.coords = coordinates
        self._coords = preppedcoords
        self.area = 0.0
        self.bounds = _bounds
    @property
    def __geo_interface__(self):
        geojson = dict()
        coords = self.coords
        #set dict items
        geojson["type"] = self.geom_type
        geojson["coordinates"] = coords
        return geojson
    @property
    def length(self):
        hypot = math.hypot
        length = 0
        for index in xrange(len(self.coords)-1):
            x1,y1 = self.coords[index]
            x2,y2 = self.coords[index+1]
            xdiff = x2-x1
            ydiff = y2-y1
            #dotprod = x1*y2 + x2*y1
            #_linelength = dotprod
            _linelength = hypot(xdiff,ydiff)
            length += _linelength
        return length
    def buffer(self, buffersize, jointype="miter", endtype="project"):
        jointypes = dict([("bevel",clipper.JoinType.Square),
                          ("round",clipper.JoinType.Round),
                          ("miter",clipper.JoinType.Miter)])
        jointype = jointypes[jointype]
        endtypes = dict([("butt",clipper.EndType.Butt),
                         ("project",clipper.EndType.Square),
                         ("round",clipper.EndType.Round),
                         ("closed",clipper.EndType.Closed)])
        endtype = endtypes[endtype]
        #prep coords
        alllines = [_PrepCoords(self.coords, convertfloats=False)]
        #execute buffer
        resulttree = clipper.OffsetPolyLines(alllines, buffersize, jointype=jointype, endtype=endtype)
        #finally create and return geom
        geom = _ResultTree2Geom(resulttree)
        #   for lines use .OffsetPolyLines
        #   for points use the _DoRound(pt, limit) function from inside _OffsetInternal
        return geom

class MultiLineString:
    #NOT FINISHED
    def __init__(self, linestrings):
        pass
        
class LinearRing:
    def __init__(self, coordinates, counterclockwise=False):
        """
        By default coords are forced to go in a clockwise direction
        If counterclockwise is set to True, then it will be forced counterclockwise, which is used for holes, ie interior rings
        """
        self.geom_type = "LinearRing"
        #check that ring is closed
        if coordinates[0] != coordinates[-1]:
            coordinates.append(coordinates[0])
        #prep coords for clip analysis
        preppedcoords = _PrepCoords(coordinates)
        #get area bc needed to get direction/orientation anyway
        floatcoords = _PrepCoords(coordinates, convertfloats=False)
        _area = clipper.Area(floatcoords)
        is_clockwise = _area > 0.0
        #get bounds
        rectobj = clipper._GetBounds([floatcoords]) #must wrap in list bc _GetBounds takes a list of polygons
        _bounds = (rectobj.left, rectobj.top, rectobj.right, rectobj.bottom)
        #then test correct orientation for exterior/interior
        if counterclockwise:
            if is_clockwise:
                coordinates = list(reversed(coordinates))
                preppedcoords = list(reversed(preppedcoords))
                _area *= -1
        else:
            if not is_clockwise:
                coordinates = list(reversed(coordinates))
                preppedcoords = list(reversed(preppedcoords))
                _area *= -1
        #then set properties
        self.coords = coordinates
        self._coords = preppedcoords
        self.area = _area
        self.bounds = _bounds
    @property
    def length(self):
        hypot = math.hypot
        length = 0
        for index in xrange(len(self.coords)-1):
            x1,y1 = self.coords[index]
            x2,y2 = self.coords[index+1]
            xdiff = x2-x1
            ydiff = y2-y1
            #dotprod = x1*y2 + x2*y1
            #_linelength = dotprod
            _linelength = hypot(xdiff,ydiff)
            length += _linelength
        return length

class Polygon:
    def __init__(self, exterior, interiors=[]):
        """
        - exterior is a single list of the polygon's outer coordinates
        - interiors is a list of several coordinate lists (one for each hole)
        """
        self.geom_type = "Polygon"
        self.exterior = LinearRing(exterior)
        self.interiors = [LinearRing(hole, counterclockwise=True) for hole in interiors]
    ### Properties
    @property
    def __geo_interface__(self):
        geojson = dict()
        coords = [self.exterior.coords]
        _holes = [hole.coords for hole in self.interiors]
        if _holes:
            coords.extend(_holes)
        #set dict items
        geojson["type"] = self.geom_type
        geojson["coordinates"] = coords
        return geojson
    @property
    def area(self):
        sumarea = self.exterior.area
        for hole in self.interiors:
            sumarea += hole.area #hole areas are negative so will decrease the total area
        return sumarea
    @property
    def length(self):
        length = self.exterior.length
        for hole in self.interiors:
            length += hole.length #hole areas give more edges to the polygon so should increase the total length
        return length
    @property
    def bounds(self):
        return self.exterior.bounds
    ### Comparison methods
    def distance(self, other):
        if other.geom_type in ("Point","MultiPoint"):
            #...
            pass
        else:
            #clipper._ClosestPointOnLine(pt, linePt1, linePt2)
            pass
    def contains(self, other):
        #clipper._Poly2ContainsPoly1(outPt1, outPt2)
        pass
    def within(self, other):
        #same as contains, but reverse the two polygons
        pass
    ### Constructive methods
    def buffer(self, buffersize, jointype="miter"):
        jointypes = dict([("bevel",clipper.JoinType.Square),
                          ("round",clipper.JoinType.Round),
                          ("miter",clipper.JoinType.Miter)])
        jointype = jointypes[jointype]
        #prep coords
        allpolys = [_PrepCoords(self.exterior.coords, convertfloats=False)]
        _holes = [_PrepCoords(hole.coords, convertfloats=False) for hole in self.interiors]
        if _holes:
            allpolys.extend(_holes)
        #execute buffer
        resulttree = clipper.OffsetPolygons(allpolys, buffersize, jointype=jointype)
        #finally create and return geom
        geom = _ResultTree2Geom(resulttree)
        #   for lines use .OffsetPolyLines
        #   for points use the _DoRound(pt, limit) function from inside _OffsetInternal
        return geom
    def clean(self):
        pass
    def simplify(self):
        pass
    ### Set theory methods
    def intersect(self, other):
        subjpolys = self
        clippolys = other
        result = _Clip(subjpolys, clippolys, "intersect")
        return result
    def union(self, other):
        subjpolys = self
        clippolys = other
        result = _Clip(subjpolys, clippolys, "union")
        return result
    def difference(self, other):
        subjpolys = self
        clippolys = other
        result = _Clip(subjpolys, clippolys, "difference")
        return result
    def symmetric_difference(self, other):
        subjpolys = self
        clippolys = other
        result = _Clip(subjpolys, clippolys, "exclusive_or")
        return result
    ### Internal use only
    def _addtoclipper(self, clipperobj, addtype):
        preppedcoords = [self.exterior._coords]
        preppedcoords.extend([hole._coords for hole in self.interiors])
        for outer_or_hole in preppedcoords:
            clipperobj.AddPolygon(outer_or_hole, addtype)

class MultiPolygon:
    def __init__(self, polygons):
        """
        - polygons is a sequence of polygon type lists, each with one exterior list followed by a list of hole-lists
          example: MultiPolygon([ (exterior1, [hole1_1,hole1_2]), (exterior2, [hole2_1,hole2_2]) ])
        """
        self.geom_type = "MultiPolygon"
        geoms = []
        for polygon in polygons:
            exterior, holes = polygon
            geoms.append( Polygon(exterior, holes) )
        self.geoms = geoms
    ### Properties
    @property
    def __geo_interface__(self):
        geojson = dict()
        coords = []
        for geom in self.geoms:
            eachmulticoords = [geom.exterior.coords]
            _holes = [hole.coords for hole in geom.interiors]
            if _holes:
                eachmulticoords.extend(_holes)
            coords.append(eachmulticoords)
        #set dict items
        geojson["type"] = self.geom_type
        geojson["coordinates"] = coords
        return geojson
    @property
    def area(self):
        sumarea = 0
        for geom in self.geoms:
            sumarea += geom.area
        return sumarea
    @property
    def length(self):
        length = 0
        for geom in self.geoms:
            length += geom.length
        return length
    @property
    def bounds(self):
        xmin,ymin,xmax,ymax = self.geoms[0].exterior.bounds
        for geom in self.geoms:
            _xmin,_ymin,_xmax,_ymax = geom.exterior.bounds
            if _xmin < xmin: xmin = _xmin
            if _ymin < ymin: ymin = _ymin
            if _xmax > xmax: xmax = _xmax
            if _ymax > ymax: ymax = _ymax
        return (xmin,ymin,xmax,ymax)
    ### Constructive methods
    def buffer(self, buffersize, jointype="miter"):
        jointypes = dict([("bevel",clipper.JoinType.Square),
                          ("round",clipper.JoinType.Round),
                          ("miter",clipper.JoinType.Miter)])
        jointype = jointypes[jointype]
        #Note: buffer on multipolygon automatically dissolves if it ends up intersecting itself
        allpolys = []
        for geom in self.geoms:
            #prep coords
            temppolys = [_PrepCoords(geom.exterior.coords, convertfloats=False)]
            _holes = [_PrepCoords(hole.coords, convertfloats=False) for hole in geom.interiors]
            if _holes:
                temppolys.extend(_holes)
            allpolys.extend(temppolys)
        #execute buffer
        resulttree = clipper.OffsetPolygons(allpolys, buffersize, jointype=jointype)
        #finally create and return geom
        geom = _ResultTree2Geom(resulttree)
        #   for lines use .OffsetPolyLines
        #   for points use the _DoRound(pt, limit) function from inside _OffsetInternal
        return geom
    ### Set theory methods
    def intersect(self, other):
        subjpolys = self
        clippolys = other
        result = _Clip(subjpolys, clippolys, "intersect")
        return result
    def union(self, other):
        subjpolys = self
        clippolys = other
        result = _Clip(subjpolys, clippolys, "union")
        return result
    def difference(self, other):
        subjpolys = self
        clippolys = other
        result = _Clip(subjpolys, clippolys, "difference")
        return result
    def symmetric_difference(self, other):
        subjpolys = self
        clippolys = other
        result = _Clip(subjpolys, clippolys, "exclusive_or")
        return result
    ### Internal use only
    def _addtoclipper(self, clipperobj, addtype):
        for eachmulti in self.geoms:
            eachmulti._addtoclipper(clipperobj, addtype)


if __name__ == "__main__":

    #point
    point = Point(5, 5)
    print point.area
    print point.length
    print point.bounds

    #multipoint

    #linestring
    linestring = LineString([(1.0,1.0),(15.0,15.0),(10.0,30.0)])
    print linestring.area
    print linestring.length
    print linestring.bounds

    #multilinestring

    #single ring
    ring = LinearRing([(1,1),(1,10),(10,10),(10,1),(1,1)])
    print ring.area
    print ring.length
    print ring.bounds

    #polygon with holes
    polygon = Polygon(exterior=[(1,1),(1,10),(10,10),(10,1),(1,1)], interiors=[[(4,4),(4,9),(9,9),(9,4),(4,4)], [(1.2,1.2),(1.2,3.9),(3.9,3.9),(3.9,1.2),(1.2,1.2)]])
    print polygon.area
    print polygon.length
    print polygon.bounds
    print polygon.__geo_interface__

    #multipolygon with holes
    polygonslist = [( [(1,1),(1,10),(10,10),(10,1),(1,1)], [[(4,4),(4,9),(9,9),(9,4),(4,4)], [(1.2,1.2),(1.2,3.9),(3.9,3.9),(3.9,1.2),(1.2,1.2)]] ),
                    ( [(1,1),(1,10),(10,10),(10,1),(1,1)], [[(4,4),(4,9),(9,9),(9,4),(4,4)], [(1.2,1.2),(1.2,3.9),(3.9,3.9),(3.9,1.2),(1.2,1.2)]] ) ]
    multipolygon = MultiPolygon(polygonslist)
    print multipolygon.area
    print multipolygon.length
    print multipolygon.bounds
    print multipolygon.__geo_interface__

    #buffer test
    polygon = Polygon(exterior=[(10,10),(100,10),(100,100),(10,100)], interiors=[[(20,20),(20,90),(90,90),(90,20)]])
    print "buffer",polygon.buffer(buffersize=2).exterior.coords
    polygonslist = [( [(30.0,30.0),(50.0,30.0),(50.0,50.0),(30.0,50.0)], [] ),
                    ( [(60.0,60.0),(80.0,60.0),(80.0,80.0),(60.0,80.0)], [] )]
    multipolygon = MultiPolygon(polygonslist)
    print "multibuffer",multipolygon.buffer(buffersize=2)

    #union test
    u1 = Polygon(exterior=[(10,10),(100,10),(100,100),(10,100)], interiors=[[(20,20),(20,90),(90,90),(90,20)]])
    polygonslist = [( [(30.0,30.0),(50.0,30.0),(50.0,50.0),(30.0,50.0)], [] ),
                    ( [(60,60),(80,60),(80,80),(60,80)], [] )]
    u2 = MultiPolygon(polygonslist)
    result = u1.union(u2)
    "below printing assumes the result is a multipolygon"
    print "obj",result
    for geom in result.geoms:
        print "ext",geom.exterior.coords
        print "holes",[hole.coords for hole in geom.interiors]

    #use geojson to make geometries from a shapefile
##    import geovis.shapefile_fork as pyshp
##    reader = pyshp.Reader("D:/Test Data/cshapes/cshapes.shp")
##    oldshape = False
##    for shape in reader.iterShapes():
##        geoj = shape.__geo_interface__
##        geotype = geoj["type"]
##        print geotype
##        #
##        geom = geoj2geom(geoj)
##        #
##        if geotype == "Polygon":
##            holenr = len(geom.interiors)
##            if holenr > 0:
##                print holenr
##        elif geotype == "MultiPolygon":
##            for eachmulti in geom.geoms:
##                holenr = len(eachmulti.interiors)
##                if holenr > 0:
##                    print holenr
##        #add to cumulative union
##        if oldshape:
##            union = oldshape.union(geom)
##            print union
##            oldshape = union
##        else:
##            oldshape = geom

    #test visualizing via geojson
    import geovis
    geovis.SetRenderingOptions(renderer="PIL")
    geovis.SetMapDimensions(width=800, height=400)
    newmap = geovis.NewMap()
    newmap.AddShape(multipolygon.buffer(10, jointype="round"))
    poly1 = Polygon(exterior=[(30.0,30.0),(50.0,30.0),(50.0,50.0),(30.0,50.0)]).buffer(10, jointype="round")
    poly2 = Polygon(exterior=[(60.0,60.0),(80.0,60.0),(80.0,80.0),(60.0,80.0)]).buffer(10, jointype="round")
    newmap.AddShape(poly1.intersect(poly2), fillcolor=geovis.Color("purple"))
    newmap.AddShape(linestring.buffer(5, jointype="round", endtype="project"))
    #newmap.SaveMap("C:/Users/BIGKIMO/Desktop/clippyviz.png")
    newmap.ViewMap()
    
