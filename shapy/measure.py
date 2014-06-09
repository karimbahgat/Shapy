
import math, itertools
import clipper
from clipper import PointInPoly

### MAIN USER FUNCTIONS

###### POINTS

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

def dist_point2multipoint(point, multipoint, getclosestpoint=False, relativedist=False):
    _firstdist = dist_point2point(point, multipoint[0], relativedist=True)
    _firstresult = {"mindist":_firstdist, "closestpoint_other":multipoint[0]}
    mindist = _firstresult
    minresult = _firstresult
    for eachmulti in multipoint:
        if mindist == 0: return minresult
        _dist = dist_point2point(point, eachmulti, relativedist=True)
        if _dist < mindist:
            mindist = _dist
            if getclosestpoint: minresult = {"mindist":_dist, "closestpoint_other":eachmulti}
            else: minresult = {"mindist":_dist}
    if not relativedist:
        mindist = math.sqrt(mindist)
        minresult["mindist"] = mindist
    return minresult

def dist_point2lines(point, lines, getclosestpoint=False, relativedist=False):
    """
    Returns a dictionary, with optional closest point on line
    """
    _pointtuple = point
    _firstlineseg = lines[:2]
    mindist,_closestpoint = _line2point(_firstlineseg, point=_pointtuple, getclosestpoint=True, relativedist=True)
    closestpoint_other = _closestpoint
    for _lineseg in _pairwise(lines):
        if mindist == 0: break #point is on line, so stop checking and return result
        else:
            dist,_closestpoint = _line2point(_lineseg, point=_pointtuple, getclosestpoint=True, relativedist=True)
            if dist < mindist:
                mindist = dist
                closestpoint_other = _closestpoint
    if not relativedist:
        mindist = math.sqrt(mindist)
    if getclosestpoint: results = {"mindist":mindist, "closestpoint_other":closestpoint_other}
    else: results = {"mindist":mindist}
    return results

def dist_point2multilines(point, multilines, getclosestpoint=False, relativedist=False):
    _firstresult = dist_point2lines(point, multilines[0], getclosestpoint=getclosestpoint, relativedist=True)
    mindist = _firstresult["mindist"]
    minresult = _firstresult
    for eachmulti in multilines:
        if mindist == 0: return minresult
        _result = dist_point2lines(point, eachmulti, getclosestpoint=getclosestpoint, relativedist=True)
        _dist = _result["mindist"]
        if _dist < mindist:
            mindist = _dist
            minresult = _result
    if not relativedist:
        mindist = math.sqrt(mindist)
        minresult["mindist"] = mindist
    return minresult

def dist_point2poly(point, poly, getclosestpoint=False, relativedist=False):
    exterior = poly[0]
    if len(poly) > 1: holes = poly[1:]
    else: holes = []
    #before anything check that point is not on polygon
    if PointInPoly(point, exterior, holes):
        #point was inside exterior and not in any hole, so must be on polygon
        minresult = {"mindist":0}
        return minresult
    #first measure distance from exterior
    minresult = dist_point2lines(point=point, lines=exterior, getclosestpoint=getclosestpoint, relativedist=True)
    mindist = minresult["mindist"]
    #then from holes
    for hole in holes:
        _result = dist_point2lines(point=point, lines=hole, getclosestpoint=getclosestpoint, relativedist=True)
        _dist = _result["mindist"]
        if _dist < mindist:
            mindist = _dist
            minresult = _result
    if not relativedist:
        mindist = math.sqrt(mindist)
        minresult["mindist"] = mindist
    return minresult

def dist_point2multipoly(point, multipoly, getclosestpoint=False, relativedist=False):
    _firstpolyandholes = multipoly[0]
    _firstresult = dist_point2poly(point, _firstpolyandholes, getclosestpoint=getclosestpoint, relativedist=True)
    mindist = _firstresult["mindist"]
    minresult = _firstresult
    for eachmulti in multipoly:
        if mindist == 0: return minresult
        _polyandholes = eachmulti
        _result = dist_point2poly(point, _polyandholes, getclosestpoint=getclosestpoint, relativedist=True)
        _dist = _result["mindist"]
        if _dist < mindist:
            mindist = _dist
            minresult = _result
    if not relativedist:
        mindist = math.sqrt(mindist)
        minresult["mindist"] = mindist
    return minresult

###### MULTIPOINTS

def dist_multipoint2point(multipoint, point, getclosestpoint=False, relativedist=False):
    result = dist_point2multipoint(point, multipoint, getclosestpoint=getclosestpoint, relativedist=relativedist)
    #then swap position of closestpoint bc opposite
    if getclosestpoint:
        closestpoint_self = result["closestpoint_other"]
        del result["closestpoint_other"]
        result["closestpoint_self"] = closestpoint_self
    return result

def dist_multipoint2multipoint(multipoint1, multipoint2, getclosestpoints=False, relativedist=False):
    _firstresult = dist_point2multipoint(multipoint1[0], multipoint2, getclosestpoint=getclosestpoints, relativedist=True)
    mindist = _firstresult["mindist"]
    minresult = _firstresult
    closestpoint_self = multipoint1[0]
    for eachmulti in multipoint1:
        if mindist == 0: break
        _result = dist_point2multipoint(eachmulti, multipoint2, getclosestpoint=getclosestpoints, relativedist=True)
        _dist = _result["mindist"]
        if _dist < mindist:
            mindist = _dist
            minresult = _result
            closestpoint_self = eachmulti
    if not relativedist:
        mindist = math.sqrt(mindist)
        minresult["mindist"] = mindist
    if getclosestpoints: minresult["closestpoint_self"] = closestpoint_self
    return minresult

def dist_multipoint2lines(multipoint, lines, getclosestpoints=False, relativedist=False):
    _firstresult = dist_point2lines(multipoint[0], lines, getclosestpoint=getclosestpoints, relativedist=True)
    mindist = _firstresult["mindist"]
    minresult = _firstresult
    closestpoint_self = multipoint[0]
    for eachmulti in multipoint:
        if mindist == 0: break
        _result = dist_point2lines(eachmulti, lines, getclosestpoint=getclosestpoints, relativedist=True)
        _dist = _result["mindist"]
        if _dist < mindist:
            mindist = _dist
            minresult = _result
            closestpoint_self = eachmulti
    if not relativedist:
        mindist = math.sqrt(mindist)
        minresult["mindist"] = mindist
    if getclosestpoints: minresult["closestpoint_self"] = closestpoint_self
    return minresult

def dist_multipoint2multilines(multipoint, multilines, getclosestpoints=False, relativedist=False):
    _firstresult = dist_point2multilines(multipoint[0], multilines, getclosestpoint=getclosestpoints, relativedist=True)
    mindist = _firstresult["mindist"]
    minresult = _firstresult
    closestpoint_self = multipoint[0]
    for eachmulti in multipoint:
        if mindist == 0: break
        _result = dist_point2multilines(eachmulti, multilines, getclosestpoint=getclosestpoints, relativedist=True)
        _dist = _result["mindist"]
        if _dist < mindist:
            mindist = _dist
            minresult = _result
            closestpoint_self = eachmulti
    if not relativedist:
        mindist = math.sqrt(mindist)
        minresult["mindist"] = mindist
    if getclosestpoints: minresult["closestpoint_self"] = closestpoint_self
    return minresult

def dist_multipoint2poly(multipoint, poly, getclosestpoints=False, relativedist=False):
    _firstresult = dist_point2poly(multipoint[0], poly, getclosestpoint=getclosestpoints, relativedist=True)
    mindist = _firstresult["mindist"]
    minresult = _firstresult
    closestpoint_self = multipoint[0]
    for eachmulti in multipoint:
        if mindist == 0: break
        _result = dist_point2poly(eachmulti, poly, getclosestpoint=getclosestpoints, relativedist=True)
        _dist = _result["mindist"]
        if _dist < mindist:
            mindist = _dist
            minresult = _result
            closestpoint_self = eachmulti
    if not relativedist:
        mindist = math.sqrt(mindist)
        minresult["mindist"] = mindist
    if getclosestpoints: minresult["closestpoint_self"] = closestpoint_self
    return minresult

def dist_multipoint2multipoly(multipoint, multipoly, getclosestpoints=False, relativedist=False):
    _firstresult = dist_point2multipoly(multipoint[0], multipoly, getclosestpoint=getclosestpoints, relativedist=True)
    mindist = _firstresult["mindist"]
    minresult = _firstresult
    closestpoint_self = multipoint[0]
    for eachmulti in multipoint:
        if mindist == 0: break
        _result = dist_point2multipoly(eachmulti, multipoly, getclosestpoint=getclosestpoints, relativedist=True)
        _dist = _result["mindist"]
        if _dist < mindist:
            mindist = _dist
            minresult = _result
            closestpoint_self = eachmulti
    if not relativedist:
        mindist = math.sqrt(mindist)
        minresult["mindist"] = mindist
    if getclosestpoints: minresult["closestpoint_self"] = closestpoint_self
    return minresult

###### LINES

def dist_lines2point(lines, point, getclosestpoint=False, relativedist=False):
    result = dist_point2lines(point, lines, getclosestpoint=getclosestpoint, relativedist=relativedist)
    #then swap position of closestpoint bc opposite
    if getclosestpoint:
        closestpoint_self = result["closestpoint_other"]
        del result["closestpoint_other"]
        result["closestpoint_self"] = closestpoint_self
    return result

def dist_lines2multipoint(lines, multipoint, getclosestpoints=False, relativedist=False):
    result = dist_multipoint2lines(multipoint, lines, getclosestpoints=getclosestpoints, relativedist=relativedist)
    #then swap position of closestpoint bc opposite
    if getclosestpoints:
        result["closestpoint_self"],result["closestpoint_other"] = result["closestpoint_other"],result["closestpoint_self"]
    return result

def dist_lines2lines(lines1, lines2, getclosestpoints=False, relativedist=False):
    _firstlineseg1 = lines1[:2]
    _firstlineseg2 = lines2[:2]
    #first the first one
    minresult = _line2line(_firstlineseg1, _firstlineseg2, getclosestpoints=getclosestpoints, relativedist=True)
    mindist = minresult["mindist"]
    #then the rest
    for _lineseg1 in _pairwise(lines1):
        for _lineseg2 in _pairwise(lines2):
            if mindist == 0: break #point is on line, so stop checking and return result
            else:
                _result = _line2line(_lineseg1, _lineseg2, getclosestpoints=getclosestpoints, relativedist=True)
                _dist = _result["mindist"]
                if _dist < mindist:
                    minresult = _result
                    mindist = _dist
    #prepare results
    if not relativedist:
        mindist = math.sqrt(mindist)
        minresult["mindist"] = mindist
    return minresult

def dist_lines2multilines(lines, multilines, getclosestpoints=False, relativedist=False):
    pass

def dist_lines2poly(lines, poly, getclosestpoints=False, relativedist=False):
    #loop polyedges and use lines2lines func
    pass

def dist_lines2multipoly(lines, multipoly, getclosestpoints=False, relativedist=False):
    pass

###### MULTILINES

def dist_multilines2point(multilines, point, getclosestpoint=False, relativedist=False):
    result = dist_point2multilines(point, multilines, getclosestpoint=getclosestpoint, relativedist=relativedist)
    #then swap position of closestpoint bc opposite
    if getclosestpoint:
        closestpoint_self = result["closestpoint_other"]
        del result["closestpoint_other"]
        result["closestpoint_self"] = closestpoint_self
    return result

def dist_multilines2multipoint(multilines, multipoint, getclosestpoints=False, relativedist=False):
    result = dist_multipoint2multilines(multipoint, multilines, getclosestpoints=getclosestpoints, relativedist=relativedist)
    #then swap position of closestpoint bc opposite
    if getclosestpoints:
        result["closestpoint_self"],result["closestpoint_other"] = result["closestpoint_other"],result["closestpoint_self"]
    return result

def dist_multilines2lines(multilines, lines, getclosestpoints=False, relativedist=False):
    #see eg http://mathforum.org/library/drmath/view/51980.html
    # or http://mathforum.org/library/drmath/view/51926.html
    # or https://answers.yahoo.com/question/index?qid=20110507163534AAgvfQF
    pass

def dist_multilines2multilines(multilines1, multilines2, getclosestpoints=False, relativedist=False):
    pass

def dist_multilines2poly(multilines, poly, getclosestpoints=False, relativedist=False):
    #loop polyedges and use line2line func
    pass

def dist_multilines2multipoly(multilines, multipoly, getclosestpoints=False, relativedist=False):
    pass

###### POLYGONS

def dist_poly2point(poly, point, getclosestpoint=False, relativedist=False):
    result = dist_point2poly(point, poly, getclosestpoint=getclosestpoint, relativedist=relativedist)
    #then swap position of closestpoint bc opposite
    if getclosestpoint:
        closestpoint_other = result["closestpoint_self"]
        del result["closestpoint_self"]
        result["closestpoint_other"] = closestpoint_other
    return result

def dist_poly2multipoint(poly, multipoint, getclosestpoints=False, relativedist=False):
    result = dist_multipoint2poly(multipoint, poly, getclosestpoints=getclosestpoints, relativedist=relativedist)
    #then swap position of closestpoint bc opposite
    if getclosestpoints:
        result["closestpoint_self"],result["closestpoint_other"] = result["closestpoint_other"],result["closestpoint_self"]
    return result

def dist_poly2lines(poly, lines, getclosestpoints=False, relativedist=False):
    pass

def dist_poly2multilines(poly, multilines, getclosestpoints=False, relativedist=False):
    pass
            
def dist_poly2poly(poly1, poly2, getclosestpoints=False, relativedist=False):
    #loop polyedges of both and use line2line func
    pass

def dist_poly2multipoly(poly, multipoly, getclosestpoints=False, relativedist=False):
    pass

###### MULTIPOLYGON

def dist_multipoly2point(multipoly, point, getclosestpoint=False, relativedist=False):
    result = dist_point2multipoly(point, multipoly, getclosestpoint=getclosestpoint, relativedist=relativedist)
    #then swap position of closestpoint bc opposite
    if getclosestpoint:
        closestpoint_self = result["closestpoint_other"]
        del result["closestpoint_other"]
        result["closestpoint_self"] = closestpoint_self
    return result

def dist_multipoly2multipoint(multipoly, multipoint, getclosestpoints=False, relativedist=False):
    result = dist_multipoint2multipoly(multipoint, multipoly, getclosestpoints=getclosestpoints, relativedist=relativedist)
    #then swap position of closestpoint bc opposite
    if getclosestpoints:
        result["closestpoint_self"],result["closestpoint_other"] = result["closestpoint_other"],result["closestpoint_self"]
    return result

def dist_multipoly2lines(multipoly, lines, getclosestpoints=False, relativedist=False):
    pass

def dist_multipoly2multilines(multipoly, multilines, getclosestpoints=False, relativedist=False):
    pass
            
def dist_multipoly2poly(multipoly, poly, getclosestpoints=False, relativedist=False):
    #loop polyedges of both and use line2line func
    pass

def dist_multipoly2multipoly(multipoly1, multipoly2, getclosestpoints=False, relativedist=False):
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
    try: u =  ((x3 - x1) * px + (y3 - y1) * py) / float(something)
    except ZeroDivisionError:
        #line isnt moving anywhere, so treat it as a point instead
        linepoint = line[0]
        dist = dist_point2point(point, linepoint, relativedist=relativedist)
        if getclosestpoint: result = (dist,linepoint)
        else: result = dist
        return result
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
def _line2line(line1, line2, getclosestpoints=False, relativedist=False):
    """
    Returns a dictionary of info...
    
    Note: Will not test if lines intersect, this has to be checked prior.
    BUT maybe should add afterall...

    Based on: http://stackoverflow.com/questions/2824478/shortest-distance-between-two-line-segments
    """
    L1start,L1stop = line1
    L2start,L2stop = line2
    # try each of the 4 vertices w/the other segment
    pointlinecombis = [ (L1start, [L2start,L2stop]),
                        (L1stop, [L2start,L2stop]),
                        (L2start, [L1start,L1stop]),
                        (L2stop, [L1start,L1stop]) ]
    #first one
    _point,_line = pointlinecombis[0]
    minresult = dist_point2lines(_point, _line, getclosestpoint=getclosestpoints, relativedist=True)
    mindist = minresult["mindist"]
    closestpoint_self = _point
    #then the rest
    for point,line in pointlinecombis[1:]:
        _result = dist_point2lines(point, line, getclosestpoint=getclosestpoints, relativedist=True)
        _dist = _result["mindist"]
        if _dist < mindist:
            minresult = _result
            mindist = _dist
            closestpoint_self = point
    #prepare results
    if not relativedist:
        mindist = math.sqrt(mindist)
        minresult["mindist"] = mindist
    if getclosestpoints: minresult["closestpoint_self"] = closestpoint_self
    return minresult

    #OLD BELOW
##    #see eg http://mathforum.org/library/drmath/view/51980.html
##    # or http://mathforum.org/library/drmath/view/51926.html
##    # or https://answers.yahoo.com/question/index?qid=20110507163534AAgvfQF
##    #step1: cross prod the two lines to find common perp vector
##    (L1x1,L1y1),(L1x2,L1y2) = line1
##    (L2x1,L2y1),(L2x2,L2y2) = line2
##    L1dx,L1dy = L1x2-L1x1,L1y2-L1y1
##    L2dx,L2dy = L2x2-L2x1,L2y2-L2y1
##    commonperp_dx,commonperp_dy = (L1dy - L2dy, L2dx-L1dx)
##    #step2: normalized_perp = perp vector / distance of common perp
##    if relativedist:
##        commonperp_length = commonperp_dx*commonperp_dx + commonperp_dy*commonperp_dy
##    else: commonperp_length = math.hypot(commonperp_dx,commonperp_dy)
##    commonperp_normalized_dx = commonperp_dx/float(commonperp_length)
##    commonperp_normalized_dy = commonperp_dy/float(commonperp_length)
##    #step3: length of (pointonline1-pointonline2 dotprod normalized_perp).
##    shortestvector_dx = (L1x1-L2x1)*commonperp_normalized_dx
##    shortestvector_dy = (L1y1-L2y1)*commonperp_normalized_dy
##    if relativedist:
##        mindist = shortestvector_dx*shortestvector_dx + shortestvector_dy*shortestvector_dy
##    else: mindist = math.hypot(shortestvector_dx,shortestvector_dy)
##    #return results
##    if getclosestpoints: pass
##    else: result = mindist
##    return result

if __name__ == "__main__":
    l1 = [(1,7),(5,10),(7,9)]
    l2 = [(0,0),(4,3),(10,10)]
    print dist_lines2lines(l1, l2, getclosestpoints=True)
    #print _line2line(l1,l2, getclosestpoints=True)
    import shapy
    ml = shapy.MultiLineString([l1,l2])
    ml.view(tickunit=1)
