#The geometry instances for shapy

#import stuff
import itertools, math
import clipper,measure

#global settings
PRECISION = 1000000000

#helper functions
def _pairwise(iterable):
    a,b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a,b)
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
    """
    This function prepares a shape for advanced processing.
    It takes a single list of coordinate tuples and returns the
    same list with each coordinate being a namedtuple with x,y properties.
    Unless "convertfloats" is set to False, then floats will be inflated and
    converted to integers which is required for any _Clip() operations.
    The only time converfloats should be False is when the coordinates will be
    sent directly to the clipper.py modules' _Bounds, _Area, or _Offset methods.
    """
    if convertfloats:
        return clipper.IntsToPoints(_Floats2Ints(_flatten(coords)))
    else:
        return clipper.IntsToPoints(_flatten(coords))
def _ResultTree2Geom(resulttree):
    """
    This function takes a resulttree as returned by the _Clip function
    and converts it to a ready-to-use geometry instance. If the resulttree
    is empty then the None value will be returned, meaning there were no
    results. Resulttrees are only used when the result is from clipping
    polygons with polygons. 
    """
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
def _TypeCombi(geom1, geom2):
    """
    Returns a string of the unique type combination of two geometries.
    Except for multipolygons, only takes single geometries, no multis.
    Returns either "pointline","linepoly",or "polypoint",
    or "pointpoint","lineline","polypoly"
    """
    bothtypes = (geom1.geom_type,geom2.geom_type)
    if "Point" in bothtypes:
        if "LineString" in bothtypes:
            typecombi = "pointline"
        elif "Polygon" in bothtypes:
            typecombi = "polypoint"
        else:
            typecombi = "pointpoint"
    elif "LineString" in bothtypes:
        if "Polygon" in bothtypes:
            typecombi = "linepoly"
        else:
            typecombi = "lineline"
    #polygons can be multis bc the clipper can handle them
    elif "Polygon" in bothtypes[0]:
        if "Polygon" in bothtypes[1]:
            typecombi = "polypoly"
    return typecombi
            
def _Clip(subjectgeom, clipgeom, cliptype,
         txt2cliptype=dict([
            ("intersect",0),
            ("union",1),
            ("difference",2),
            ("exclusive_or",3)
            ])):
    """
    Note: each input shape (subj and clip) is a geom object. They must be
    single geoms, except for MultiPolygons which is allowed. 
    
    - subjectpolys is the main geom to be compared with another one
    - clippolys is the geom to be compared with
    - cliptype can be "intersect","union","difference", or "exclusive_or"
    """
    cliptype = txt2cliptype[cliptype]
    typecombi = _TypeCombi(subjectgeom, clipgeom)
    if typecombi == "pointline":
        #intersection returns point if on line
        pass
    elif typecombi == "linepoly":
        #intersection returns part of line inside poly
        pass
    elif typecombi == "polypoint":
        #intersection returns point if inside
        pass
    #or same types
    elif typecombi == "pointpoint":
        #intersection tests if same
        pass
    elif typecombi == "lineline":
        #intersection returns intsec point
        pass
    elif typecombi == "polypoly":
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
def _Dist(geom1, geom2, getclosestpoints=False, relativedist=False):
    """
    Used for measuring distances between geoms. 
    Only singlegeoms are allowed, not multis. 
    Actual distances are calculated in measure.py module.
    Returns a dictionary with result entries. "mindist" is the
    distance, the closest point on a polygon is given as
    "closestpoint_poly", while for a linestring it is 
    "closestpoint_line". Points don't generate any closestpoint
    values. However, this is a bit iffy and not yet implemented
    and will change. 
    """
    typecombi = _TypeCombi(geom1, geom2)
    #then measure distance bw different shapetypes
    if typecombi == "pointline":
        if geom1.geom_type == "LineString": geom1,geom2 = geom2,geom1
        results = measure.dist_point2lines(geom1.coords[0], geom2.coords, getclosestpoint=getclosestpoints, relativedist=relativedist)
    elif typecombi == "linepoly":
        if geom1.geom_type == "Polygon": geom1,geom2 = geom2,geom1
        polyandholes = geom2.exterior.coords
        if geom2.interiors: polyandholes.extend(geom2.interiors)
        results = measure.dist_lines2poly(geom1.coords, polyandholes, getclosestpoints=getclosestpoints, relativedist=relativedist)
    elif typecombi == "polypoint":
        if geom1.geom_type == "Point": geom1,geom2 = geom2,geom1
        polyandholes = [ geom1.exterior.coords ]
        if geom1.interiors: polyandholes.extend([hole.coords for hole in geom1.interiors])
        results = measure.dist_poly2point(polyandholes, geom2.coords[0], getclosestpoint=getclosestpoints, relativedist=relativedist)
    #or same types
    elif typecombi == "pointpoint":
        mindist = measure.dist_point2point(geom1.coords[0], geom2.coords[0], relativedist=relativedist)
        results = {"mindist":mindist}
    elif typecombi == "lineline":
        results = measure.dist_lines2lines(geom1.coords, geom2.coords, getclosestpoints=getclosestpoints, relativedist=relativedist)
    elif typecombi == "polypoly":
        polyandholes1 = [ geom1.exterior.coords ]
        if geom1.interiors: polyandholes.extend(geom1.interiors)
        polyandholes2 = geom2.exterior.coords
        if geom2.interiors: polyandholes.extend([hole.coords for hole in geom2.interiors])
        results = measure.dist_poly2poly(polyandholes1, polyandholes2, getclosestpoints=getclosestpoints, relativedist=relativedist)
    #finally create geoms out of closest geoms and points, and
    #   add to result dict if desired.
    #...
    return results

##def _Compare(geom1, geom2, comparetype):
##    """
##    Used for contains and within...
##    """
##    typecombi = _TypeCombi(subjectgeom, clipgeom)
##    if typecombi == "pointline":
##        pass
##    elif typecombi == "linepoly":
##        pass
##    elif typecombi == "polypoint":
##        #use clipper._PointInPolygon(pt, outPt)
##        pass
##    #or same types
##    elif typecombi == "pointpoint":
##        pass
##    elif typecombi == "lineline":
##        pass
##    elif typecombi == "polypoly":
##        #use clipper._Poly2ContainsPoly1(outPt1, outPt2)
##        pass


#user functions
def geoj2geom(shapeobj):
    """
    Takes any object that has the __geo_interface__ attribute
    and creates and returns a ready-to-use geometry instance. 
    """
    geojson = shapeobj.__geo_interface__
    geotype = geojson["type"]
    coords = geojson["coordinates"]
    if geotype == "Point":
        x,y = coords
        geom = Point(x,y)
    elif geotype == "MultiPoint":
        multipoints = coords
        geom = MultiPoint(multipoints)
    elif geotype == "LineString":
        linelist = coords
        geom = LineString(linelist)
    elif geotype == "MultiLineString":
        multilinelist = coords
        geom = MultiLineString(multilinelist)
    elif geotype == "Polygon":
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
    #NOT FINISHED, LACKING SET THEORY METHODS
    def __init__(self, x, y):
        #NOTE: coords is an xy-tuple nested inside a list
        self.geom_type = "Point"
        #prep coords for clip analysis
        coords = [(x,y)]
        preppedcoords = _PrepCoords(coords)
        #then set properties
        self.coords = coords
        self._coords = preppedcoords
        self.area = 0.0
        self.length = 0.0
        self.bounds = [x,y,x,y]
        self.x = x
        self.y = y
    ### Properties
    @property
    def __geo_interface__(self):
        geojson = dict()
        coords = self.coords
        #set dict items
        geojson["type"] = self.geom_type
        geojson["coordinates"] = coords[0]
        return geojson
    ### Constructive methods
    def buffer(self, buffersize, jointype="miter"):
        # for points use the _DoRound(pt, limit) function from inside _OffsetInternal
        pass
    ### Comparison methods
    def distance(self, other, getclosestpoints=False):
        #MAYBE ADD getgeoms OPTION
        othertype = other.geom_type
        #begin measuring
        if othertype == "Point":
            minresult = _Dist(self, other, getclosestpoints=getclosestpoints)
        elif othertype == "MultiPoint":
            _firstresult = _Dist(self, other.geoms[0], getclosestpoints=getclosestpoints, relativedist=True)
            mindist = _firstresult["mindist"]
            minresult = _firstresult
            for geom in other.geoms:
                _result = _Dist(self, geom, getclosestpoints=getclosestpoints, relativedist=True)
                _dist = _result["mindist"]
                if _dist < mindist: mindist = _dist
            mindist = math.sqrt(mindist)
            minresult["mindist"] = mindist
        elif othertype == "LineString":
            minresult = _Dist(self, other, getclosestpoints=getclosestpoints)
        #elif othertype == "MultiLineString":
        #    pass
        elif othertype == "Polygon":
            minresult = _Dist(self, other, getclosestpoints=getclosestpoints)
        #elif othertype == "MultiPolygon":
        #    pass
        return minresult
    ### Other
    def view(self, imagesize=None, crs=None, fillcolor=(111,111,111), outlinecolor=(0,0,0)):
        """
        Draws and pops up a window with the shape.

        - imagesize is an optional two-tuple of the pixel size of the viewimage in the form of (pixelwidth,pixelheight). Default is 400 by 400.
        """
        import pydraw
        if not crs:
            x1,y1,x2,y2 = self.bounds
            xoffset = 5
            yoffset = 5
            crs_bounds = [x1-xoffset, y1-yoffset, x2+xoffset, y2+yoffset]
            crs = pydraw.CoordinateSystem(crs_bounds)
        if not imagesize: imagesize = (400,400)
        img = pydraw.Image(*imagesize, background=(250,250,250), crs=crs)
        img.drawgeojson(self, fillcolor=fillcolor, outlinecolor=outlinecolor)
        img.view()

class MultiPoint:
    #NOT FINISHED
    def __init__(self, points):
        self.geom_type = "MultiPoint"
        #prep coords for clip analysis
        self.geoms = [Point(*point) for point in points]
        self.area = 0.0
        self.length = 0.0
    ### Properties
    @property
    def __geo_interface__(self):
        geojson = dict()
        coords = [geom.coords[0] for geom in self.geoms]
        #set dict items
        geojson["type"] = self.geom_type
        geojson["coordinates"] = coords
        return geojson
    @property
    def bounds(self):
        _x,_y = self.geoms[0].coords[0]
        xmin,ymin,xmax,ymax = _x,_y,_x,_y
        for geom in self.geoms:
            _x,_y = geom.coords[0]
            if _x < xmin: xmin = _x
            if _y < ymin: ymin = _y
            if _x > xmax: xmax = _x
            if _y > ymax: ymax = _y
        return [xmin,ymin,xmax,ymax]
    ### Constructive methods
    def buffer(self, buffersize, jointype="miter"):
        # for points use the _DoRound(pt, limit) function from inside _OffsetInternal
        pass
    ### Other
    def view(self, imagesize=None, crs=None, fillcolor=(111,111,111), outlinecolor=(0,0,0)):
        """
        Draws and pops up a window with the shape.

        - imagesize is an optional two-tuple of the pixel size of the viewimage in the form of (pixelwidth,pixelheight). Default is 400 by 400.
        """
        import pydraw
        if not crs:
            x1,y1,x2,y2 = self.bounds
            xwidth = x2-x1
            yheight = y2-y1
            xoffset = xwidth*0.1
            yoffset = yheight*0.1
            crs_bounds = [x1-xoffset, y1-yoffset, x2+xoffset, y2+yoffset]
            crs = pydraw.CoordinateSystem(crs_bounds)
        if not imagesize: imagesize = (400,400)
        img = pydraw.Image(*imagesize, background=(250,250,250), crs=crs)
        img.drawgeojson(self, fillcolor=fillcolor, outlinecolor=outlinecolor)
        img.view()
        
class LineString:
    #NOT FINISHED, LACKING SET THEORY METHODS
    def __init__(self, coordinates):
        self.geom_type = "LineString"
        #prep coords for clip analysis
        preppedcoords = _PrepCoords(coordinates)
        floatcoords = _PrepCoords(coordinates, convertfloats=False)
        #get bounds
        rectobj = clipper._GetBounds([floatcoords]) #must wrap in list bc _GetBounds takes a list of polygons
        _bounds = [rectobj.left, rectobj.top, rectobj.right, rectobj.bottom]
        #then set properties
        self.coords = coordinates
        self._coords = preppedcoords
        self.area = 0.0
        self.bounds = _bounds
    ### Properties
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
    ### Constructive methods
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
        return geom
    ### Other
    def view(self, imagesize=None, crs=None, fillcolor=(111,111,111), outlinecolor=(0,0,0)):
        """
        Draws and pops up a window with the shape.

        - imagesize is an optional two-tuple of the pixel size of the viewimage in the form of (pixelwidth,pixelheight). Default is 400 by 400.
        """
        import pydraw
        if not crs:
            x1,y1,x2,y2 = self.bounds
            xwidth = x2-x1
            yheight = y2-y1
            xoffset = xwidth*0.1
            yoffset = yheight*0.1
            crs_bounds = [x1-xoffset, y1-yoffset, x2+xoffset, y2+yoffset]
            crs = pydraw.CoordinateSystem(crs_bounds)
        if not imagesize: imagesize = (400,400)
        img = pydraw.Image(*imagesize, background=(250,250,250), crs=crs)
        img.drawgeojson(self, fillcolor=fillcolor, outlinecolor=outlinecolor)
        img.view()

class MultiLineString:
    #NOT FINISHED, LACKING SET THEORY METHODS
    def __init__(self, lines):
        self.geom_type = "MultiLineString"
        geoms = []
        for line in lines:
            geoms.append( LineString(line) )
        self.geoms = geoms
    ### Properties
    @property
    def __geo_interface__(self):
        geojson = dict()
        coords = []
        for geom in self.geoms:
            eachmulticoords = geom.coords
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
        xmin,ymin,xmax,ymax = self.geoms[0].bounds
        for geom in self.geoms:
            _xmin,_ymin,_xmax,_ymax = geom.bounds
            if _xmin < xmin: xmin = _xmin
            if _ymin < ymin: ymin = _ymin
            if _xmax > xmax: xmax = _xmax
            if _ymax > ymax: ymax = _ymax
        return [xmin,ymin,xmax,ymax]
    ### Constructive methods
    def buffer(self, buffersize, jointype="miter", endtype="project"):
        "NOTE: Fails for multilines!"
        jointypes = dict([("bevel",clipper.JoinType.Square),
                          ("round",clipper.JoinType.Round),
                          ("miter",clipper.JoinType.Miter)])
        #Note: buffer on multipolygon automatically dissolves if it ends up intersecting itself
        alllines = []
        for geom in self.geoms:
            #buffer each
            templine = geom.buffer(buffersize, jointype=jointype, endtype=endtype)
            alllines.append(templine)
        #union all buffers
        subjpolys = alllines[0]
        clippolys = alllines[1:]
        result = _Clip(subjpolys, clippolys, "union")
        return result
        #resulttree = clipper.OffsetPolyLines(alllines, buffersize, jointype=jointype, endtype=endtype)
        #finally create and return geom
        #geom = _ResultTree2Geom(resulttree)
        #return geom
    ### Other
    def view(self, imagesize=None, crs=None, fillcolor=(111,111,111), outlinecolor=(0,0,0)):
        """
        Draws and pops up a window with the shape.

        - imagesize is an optional two-tuple of the pixel size of the viewimage in the form of (pixelwidth,pixelheight). Default is 400 by 400.
        """
        import pydraw
        if not crs:
            x1,y1,x2,y2 = self.bounds
            xwidth = x2-x1
            yheight = y2-y1
            xoffset = xwidth*0.1
            yoffset = yheight*0.1
            crs_bounds = [x1-xoffset, y1-yoffset, x2+xoffset, y2+yoffset]
            crs = pydraw.CoordinateSystem(crs_bounds)
        if not imagesize: imagesize = (400,400)
        img = pydraw.Image(*imagesize, background=(250,250,250), crs=crs)
        img.drawgeojson(self, fillcolor=fillcolor, outlinecolor=outlinecolor)
        img.view()
        
class LinearRing:
    def __init__(self, coordinates, counterclockwise=False):
        """
        Not really of interest, mostly just a helper for polygons.
        Therefore does not have all methods, only the basic properties. 
        
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
        _bounds = [rectobj.left, rectobj.top, rectobj.right, rectobj.bottom]
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
    ### Other
    def view(self, imagesize=None, crs=None, fillcolor=(111,111,111), outlinecolor=(0,0,0)):
        """
        Draws and pops up a window with the shape.

        - imagesize is an optional two-tuple of the pixel size of the viewimage in the form of (pixelwidth,pixelheight). Default is 400 by 400.
        """
        import pydraw
        if not crs:
            x1,y1,x2,y2 = self.bounds
            xwidth = x2-x1
            yheight = y2-y1
            xoffset = xwidth*0.1
            yoffset = yheight*0.1
            crs_bounds = [x1-xoffset, y1-yoffset, x2+xoffset, y2+yoffset]
            crs = pydraw.CoordinateSystem(crs_bounds)
        if not imagesize: imagesize = (400,400)
        img = pydraw.Image(*imagesize, background=(250,250,250), crs=crs)
        img.drawgeojson(self, fillcolor=fillcolor, outlinecolor=outlinecolor)
        img.view()
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
        return [xmin,ymin,xmax,ymax]
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
    ### Other
    def view(self, imagesize=None, crs=None, fillcolor=(111,111,111), outlinecolor=(0,0,0)):
        """
        Draws and pops up a window with the shape.

        - imagesize is an optional two-tuple of the pixel size of the viewimage in the form of (pixelwidth,pixelheight). Default is 400 by 400.
        """
        import pydraw
        if not crs:
            x1,y1,x2,y2 = self.bounds
            xwidth = x2-x1
            yheight = y2-y1
            xoffset = xwidth*0.1
            yoffset = yheight*0.1
            crs_bounds = [x1-xoffset, y1-yoffset, x2+xoffset, y2+yoffset]
            crs = pydraw.CoordinateSystem(crs_bounds)
        if not imagesize: imagesize = (400,400)
        img = pydraw.Image(*imagesize, background=(250,250,250), crs=crs)
        img.drawgeojson(self, fillcolor=fillcolor, outlinecolor=outlinecolor)
        img.view()
    ### Internal use only
    def _addtoclipper(self, clipperobj, addtype):
        for eachmulti in self.geoms:
            eachmulti._addtoclipper(clipperobj, addtype)



    
