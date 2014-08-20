"""
A pure-Python implementation of the Greiner-Hollman clipping algorithm

CURRENTLY ONLY WORKS IF ONE INTERSECTION PER EDGE, BC INSERTALGO IS WRONG AND NEED TO SORT ALPHAS
    status: ___
ALSO DOES NOT HANDLE VERTEXES ON EDGES (DEGENERATES)
    status: ___

Based on:
http://davis.wpi.edu/~matt/courses/clipping/
http://what-when-how.com/computer-graphics-and-geometric-modeling/clipping-basic-computer-graphics-part-6/

Karim Bahgat, 2014
"""

import math,itertools

#HELPER FUNCTIONS
def _pairwise(iterable):
    a,b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a,b)

#CLASSES
class _Line:
    def __init__(self, linestart, linestop):
        (x1,y1),(x2,y2) = (linestart.x,linestart.y),(linestop.x,linestop.y)
        self.x1,self.y1,self.x2,self.y2 = x1,y1,x2,y2
        self.xdiff = x2-x1
        self.ydiff = y2-y1
        try:
            self.slope = self.ydiff/float(self.xdiff)
            self.zero_y = self.slope*(0-x1)+y1
        except ZeroDivisionError:
            self.slope = None
            self.zero_y = None
    def __str__(self):
        return str(self.tolist())
    def relativelength(self):
        return self.xdiff**2 + self.ydiff**2
    def walkdistance(self, distance):
        angl_rad = math.radians(self.getangle())
        xbuff = distance * math.cos(angl_rad)
        ybuff = distance * math.sin(angl_rad)
        newx = self.x2-xbuff
        newy = self.y2+ybuff
        return (newx,newy)
    def tolist(self):
        return (_Node(self.x1,self.y1),_Node(self.x2,self.y2))
    def intersect(self, otherline, infinite=False):
        """
        Input must be another line instance
        Finds real intersect point between line segments
        Based on http://stackoverflow.com/questions/18234049/determine-if-two-lines-intersect
        """
        # MANUAL APPROACH
        # http://stackoverflow.com/questions/18234049/determine-if-two-lines-intersect
        if self.slope == None:
            if otherline.slope == None:
                return False
            ix = self.x1
            iy = ix*otherline.slope+otherline.zero_y
        elif otherline.slope == None:
            ix = otherline.x1
            iy = ix*self.slope+self.zero_y
        else:
            try:
                ix = (otherline.zero_y-self.zero_y) / (self.slope-otherline.slope)
            except ZeroDivisionError:
                #slopes are exactly the same so never intersect
                return False
            iy = ix*self.slope+self.zero_y
        #check that intsec happens within bbox of both lines
        if ix >= min(self.x1,self.x2) and ix >= min(otherline.x1,otherline.x2)\
        and ix <= max(self.x1,self.x2) and ix <= max(otherline.x1,otherline.x2)\
        and iy >= min(self.y1,self.y2) and iy >= min(otherline.y1,otherline.y2)\
        and iy <= max(self.y1,self.y2) and iy <= max(otherline.y1,otherline.y2):
            return _Node(ix,iy)
        else:
            return False    

class _Node:
    def __init__(self, x, y, isintersection=False, alpha=None, prev=None, next=None):
        self.x = x
        self.y = y
        self.prev = prev
        self.next = next
        self.isintersection = isintersection
        self.visited = False
        self.entry = None
        self.alpha = None
        self.nextPoly = "not yet used"
        self.neighbour = None
    def __str__(self):
        return "Node("+str(self.x)+", "+str(self.y)+")"

##class _NewPolygon:
##    def __init__(self, xypoints=None):
##        """
##        Creates a new polygon consisting of nodes.
##        Automatically converts a normal xy list if xypoints is given
##        """
##        self.nodes = []
##        if xypoints:
##            for xy in xypoints:
##                self.AddVertext(xy)
##    def AddVertex(self, xy):
##        node = _Node(*xy)
##        self.InsertNode(node)
##    def InsertNode(self, node):
##        if selfnodes:
##            pass

##class _Clipper:
##    def __init__(self):
##        """
##        Subj and clip polys are each a single polygonlist of xy tuples.
##        Later extend to take multiple polygons, and with holes. 
##        """
##        self.subjectpoly = []
##        self.clippoly= []
##        pass
##    def addpolygon(self, polygon, polytype):
##        if polytype == "subject":
##            self.subjectpoly = polygon
##        elif polytype == "clip":
##            self.clippoly = polygon
##    def execute(self):
##        self._phase1()
##        self._phase2()
##        self._phase3()
##    def _phase1(self):
##        """
##        Loop all polygonlists, convert xys to nodes, and find and insert
##        intersection points.
##        If no intersections, test if polygon inside (return inside-poly if intsectmode or outside-poly if union)
##        or outside the other polygon (return None if intsect mode or both if union).
##        """
##        self.subjnodes = []
##        self.clipnodes = []
##        for subjxy in self.subjpoly:
##            node = _Node(*subjxy)
##            self.subjnodes.append(node)
##            for clipxy in self.clippoly:
##                self.clipnodes.append(node)
##        pass
##    def _phase2(self):
##        """
##        Start by determining if first node is inside or outside, and set
##        entry/exit flag accordingly. 
##        Loop through nodeslists and set and switch entryflag everytime
##        encounter intersect node.
##        """
##        pass
##    def _phase3(self):
##        """
##        Traverse nodeslists and collect resultspolygons forward for every entry
##        node and backward for every exitpoint.
##        """
##        pass

# SOME FUNCTIONS
def _pointinring(point, ring): 
    # By: Karim Bahgat
    inside = False
    lastpolypoint = ring[0]
    for polypoint in ring[1:]:
        if ((((polypoint.y <= point.y) and (point.y < lastpolypoint.y)) or \
            ((lastpolypoint.y <= point.y) and (point.y < polypoint.y))) and \
            (point.x < (lastpolypoint.x - polypoint.x) * (point.y - polypoint.y) / \
            (lastpolypoint.y - polypoint.y) + polypoint.x)):
            inside = not inside
        lastpolypoint = polypoint
    return inside
def _pointinpolygon(point, exterior, holes=[]):
    #By: Karim Bahgat
    if _pointinring(point, exterior):
        #point is inside exterior, unless it is hiding in a hole
        if holes:
            for hole in holes:
                if _PointInRing(point, hole):
                    return False
            #was not inside any holes, so must be on polygon
            return True
        else:
            #no holes to hide in, so must be on polygon
            return True
    else:
        #not inside exterior
        return False
##def _poly2containspoly1(outPt1, outPt2):
##    #NOT YET DONE
##    #Simplified to take normal xy tuples
##    #By: Karim Bahgat
##    def PointOnLineSegment(pt, linePt1, linePt2):
##        #NOT YET DONE
##        #Simplified to take normal xy tuples
##        #By: Karim Bahgat
##        return ((pt.x == linePt1.x) and (pt.y == linePt1.y)) or \
##            ((pt.x == linePt2.x) and (pt.y == linePt2.y)) or \
##            (((pt.x > linePt1.x) == (pt.x < linePt2.x)) and \
##            ((pt.y > linePt1.y) == (pt.y < linePt2.y)) and \
##            ((pt.x - linePt1.x) * (linePt2.y - linePt1.y) == \
##            (linePt2.x - linePt1.x) * (pt.y - linePt1.y)))
##    def PointOnPolygonEdge(pt, pp):
##        #NOT YET DONE
##        #Simplified to take normal xy tuples
##        #By: Karim Bahgat
##        pp2 = pp;
##        while True:
##            if (_PointOnLineSegment(pt, pp2.pt, pp2.nextOp.pt)):
##                return True
##            pp2 = pp2.nextOp
##            if (pp2 == pp): return False
##    #execute
##    pt = outPt1
##    if (_PointOnPolygon(pt.pt, outPt2)):
##        pt = pt.nextOp
##        while (pt != outPt1 and _PointOnPolygon(pt.pt, outPt2)):
##            pt = pt.nextOp
##        if (pt == outPt1): return True
##    return _PointInPolygon(pt.pt, outPt2)


# MAIN ALGORITHM
def _phase1(subjpoly, clippoly):
    """
    Takes one list of subject xy polygon coordinates, and one of clip polygon.
    Preps input polygons with nodes, and finds and inserts intersection nodes
    in correct traversal positions.
    Returns the prepped polygons as lists of nodes (subjpoly,clippoly).
    """
    subjpoly = [_Node(*xy) for xy in subjpoly]
    clippoly = [_Node(*xy) for xy in clippoly]
    for subjindex, subjline in enumerate(_pairwise(subjpoly)):
        subjline = _Line(*subjline)
        for clipindex, clipline in enumerate(_pairwise(clippoly)):
            clipline = _Line(*clipline)
            intersection = subjline.intersect(clipline)
            #insert intersection vertex
            if intersection:
                #first in subjpoly
                intsecline = _Line(subjline.tolist()[0],intersection)
                alpha = intsecline.relativelength()/float(subjline.relativelength())
                subjnode = _Node(intersection.x, intersection.y, isintersection=True, alpha=alpha)
                subjpoly.insert(subjindex+1, subjnode)
                #then in clippoly
                intsecline = _Line(clipline.tolist()[0],intersection)
                alpha = intsecline.relativelength()/float(clipline.relativelength())
                clipnode = _Node(intersection.x, intersection.y, isintersection=True, alpha=alpha)
                clippoly.insert(clipindex+1, clipnode)
                #neighbour references
                subjnode.neighbour = clipnode
                clipnode.neighbour = subjnode
    #finally assign prev and next
    for index,node in enumerate(subjpoly):
        node.prev = subjpoly[index-1]
        try: node.next = subjpoly[index+1]
        except IndexError: node.next = subjpoly[0]
    for index,node in enumerate(clippoly):
        node.prev = clippoly[index-1]
        try: node.next = clippoly[index+1]
        except IndexError: node.next = clippoly[0]
    #return
    return (subjpoly,clippoly)
def _phase2(subjpoly, clippoly):
    """
    Tags each intersection node with entry/exit flag.
    Changes them in place, and doesnt return anything.
    """
    #first subj
    print "subj"
    if _pointinpolygon(subjpoly[0], clippoly):
        entry = False
    else:
        entry = True
    for node in subjpoly:
        print node.x,node.y,entry
        if node.isintersection:
            node.entry = entry
            entry = not entry
    #then clip
    print "clip"
    if _pointinpolygon(clippoly[0], subjpoly):
        entry = False
    else:
        entry = True
    for node in clippoly:
        print node.x,node.y,entry
        if node.isintersection:
            node.entry = entry
            entry = not entry
def _phase3(subjpoly, clippoly):
    """
    Traverses the polygons based on entry exit flags, and builds new polygons
    as it goes, returning the final clipped result
    """
    #find first intersection
    for node in subjpoly:
        if node.isintersection:
            current = node
            break
    #create newpolygon
    newpoly = []
    #loop
    print "starting at intersection point",current
    while not current.visited: #until looped entire subject polygon
        ###
        current.visited = True
        if current.entry:
            isintersection = False
            while not isintersection:
                current = current.next
                isintersection = current.isintersection
                newpoly.append(current)
                print "seeking intersection forward",current, current.isintersection
        else:
            isintersection = False
            while not isintersection:
                current = current.prev
                isintersection = current.isintersection
                newpoly.append(current)
                print "seeking intersection back",current, current.isintersection
            current.visited = True
        current = current.neighbour
        print "intersection found, jumping to neighbour polygon:",current
    print "circled entire polygon?",current,current.visited,current.isintersection
    return [(node.x,node.y) for node in newpoly]
def clip(subjpoly, clippoly, cliptype):
    if cliptype == "intersect":
        preppedsubj,preppedclip = _phase1(subjpoly,clippoly)
        _phase2(preppedsubj,preppedclip)
        result = _phase3(preppedsubj,preppedclip)
        return result


if __name__ == "__main__":
    #subjpoly = [(0,0),(6,0),(6,6),(0,6),(0,0)]
    #clippoly = [(4,4),(10,4),(10,10),(4,10),(4,4)]
    subjpoly = [(0,0),(6,0),(6,6),(0,6),(0,0)]
    clippoly = [(1,4),(3,8),(5,4),(5,10),(1,10),(1,4)]
    result = clip(subjpoly,clippoly,"intersect")
    print "finished:",result
    import pydraw
    crs = pydraw.CoordinateSystem([-1,-1,11,11])
    img = pydraw.Image(400,400, crs=crs)
    img.drawpolygon(subjpoly, fillcolor=(222,0,0))
    img.drawpolygon(clippoly, fillcolor=(0,222,0))
    img.drawpolygon(result)
    img.view()


