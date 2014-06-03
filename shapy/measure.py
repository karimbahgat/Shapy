
import math, itertools
import clipper
from clipper import PointInPoly

# MAIN USER FUNCTIONS
def dist_point2point(p1, p2, relativedist=False):
    """
    Returns the distance
    """
    x1,y1 = p1
    x2,y2 = p2
    xdiff = x1-x2
    ydiff = y1-y2
    if relativedist: dist = xdiff*xdiff + ydiff*ydiff
    else: dist = math.sqrt(xdiff*xdiff + ydiff*ydiff)
    return dist

def dist_point2lines(point, lines, getclosestpoint=False, relativedist=False):
    """
    Returns a dictionary, with optional closest point on line
    """
    _pointtuple = point
    _firstlineseg = lines[:2]
    mindist,_closestpoint = _line2point(_firstlineseg, point=_pointtuple, getclosestpoint=True, relativedist=True)
    closestpoint_line = _closestpoint
    for _lineseg in _pairwise(lines):
        dist,_closestpoint = _line2point(_lineseg, point=_pointtuple, getclosestpoint=True, relativedist=True)
        if dist < mindist:
            mindist = dist
            closestpoint_line = _closestpoint
    if not relativedist:
        mindist = math.sqrt(mindist)
    if getclosestpoint: results = {"mindist":mindist, "closestpoint_line":closestpoint_line}
    else: results = {"mindist":mindist}
    return results

def dist_lines2lines(lines1, lines2, getclosestpoints=False, relativedist=False):
    pass

def dist_lines2poly(lines, poly, getclosestpoints=False, relativedist=False):
    #loop polyedges and use line2line func
    pass

def dist_poly2point(poly, point, getclosestpoint=False, relativedist=False):
    exterior = poly[0]
    if len(poly) > 1: holes = poly[1:]
    else: holes = []
    #before anything check that point is not on polygon
    if PointInPoly(point, exterior, holes):
        #point was inside exterior and not in any hole, so must be on polygon
        minresult = {"mindist":0}
        return minresult
    #first measure distance from exterior
    minresult = dist_point2lines(point, lines=exterior, getclosestpoint=getclosestpoint, relativedist=True)
    mindist = minresult["mindist"]
    #then from holes
    for hole in holes:
        _result = dist_point2lines(point, lines=hole, getclosestpoint=getclosestpoint, relativedist=True)
        _dist = _result["mindist"]
        if _dist < mindist:
            minresult = _result
    if not relativedist:
        mindist = minresult["mindist"]
        minresult["mindist"] = math.sqrt(mindist)
    return minresult
            
def dist_poly2poly(lines, poly, getclosestpoints=False, relativedist=False):
    #loop polyedges of both and use line2line func
    pass


# INTERNAL HELPERS
def _pairwise(iterable):
    a,b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a,b)
def _line2point(line, point, getclosestpoint=False, relativedist=False):
    """
    - line is a single line as a list of two x,y tuples
    - point is an x,y tuple
    - getpoint, when True will not only return the distance but also the point on the line that was closest, in a tuple (dist, (x,y))
    - relativedist, if comparing many distances is more important than getting the actual distance then this can be set to True which will return the squared distance without the squareroot which makes it faster
    """
    x3,y3 = point
    (x1,y1),(x2,y2) = line
    #below is taken directly from http://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment
    px = x2-x1
    py = y2-y1
    something = px*px + py*py
    u =  ((x3 - x1) * px + (y3 - y1) * py) / float(something)
    if u > 1:
        u = 1
    elif u < 0:
        u = 0
    x = x1 + u * px
    y = y1 + u * py
    dx = x - x3
    dy = y - y3
    #prepare results
    if relativedist: dist = dx*dx + dy*dy
    else: dist = math.sqrt(dx*dx + dy*dy)
    if getclosestpoint: result = (dist,(x,y))
    else: result = dist
    return result
