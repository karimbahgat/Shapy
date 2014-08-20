
import itertools

import pydraw
from pydraw.geomhelper import _Line  

def _pairwise(iterable):
    a,b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a,b)

def _signed_area(coords):
    """
    From PyShp:
    Return the signed area enclosed by a ring using the linear time
    algorithm at http://www.cgafaq.info/wiki/Polygon_Area. A value >= 0
    indicates a counter-clockwise oriented ring.
    """
    xs, ys = map(list, zip(*coords))
    xs.append(xs[1])
    ys.append(ys[1])
    return sum(xs[i]*(ys[i+1]-ys[i-1]) for i in xrange(1, len(coords)))/2.0

def _remove_selfintersections(coords):
    #1 insert all selfintersection points
    #2 iterate and add each to a "checked" list
    #3 for each new, check if in the checked list
    #     if so, it means the checked list contains an inside selfintersecting polygon, so exclude from output polygon and clear checked list
    pass

def connectlines(line1, line2, jointype="miter"):
    return []

def bufferpolygon(poly, buffersize, jointype="miter"):
    """Buffer/offset the size of a polygon.
    - poly: a list of xy coordinate tuples
    - buffersize: a float value, 0 for no change, negative for shrinking, and positive for growing
    """

    if buffersize == 0: return poly
    
    # force polygon to go clockwise
    if _signed_area(poly) <= 0:
        poly = list(reversed(poly))
        
    #for first line
    newpoly = []
    previntersection = None
    line1 = _Line(poly[0][0],poly[0][1],poly[1][0],poly[1][1])
    if buffersize > 0: # grow
        bufferline1 = line1.getbuffersides(buffersize)[0]
        newpoly.append(bufferline1.start)
    elif buffersize < 0: # shrink
        bufferline1 = line1.getbuffersides(buffersize)[1]
        newpoly.append(bufferline1.start)
    #...

    # then loop
    for start,end in _pairwise(poly):
        
        line2 = _Line(start[0],start[1],end[0],end[1])

        # get line join coordinates
        if buffersize > 0: # grow
            bufferline2 = line2.getbuffersides(buffersize)[0]
            if jointype == "miter":
                intersection = bufferline1.intersect(bufferline2, infinite=True)
                if not intersection: continue  # ???
                else: connection = [intersection]
                print connection
                previntersection = intersection
            elif jointype == "bevel":
                connection = bufferline2.tolist()

            newpoly.extend(connection)
            
        elif buffersize < 0: # shrink
            bufferline2 = line2.getbuffersides(buffersize)[1]
            #if intersection == previntersection: continue  # line has disappeared (zero-length), so no use in including
            if jointype == "miter":
                pass
            elif jointype == "bevel":
                connection = bufferline2.tolist()

            newpoly.extend(connection)
        
        # prep for next iter
        line1 = line2
        bufferline1 = bufferline2

    # then last coord
    #...

    # then union and remove selfintersections
    #...
    return newpoly


if __name__ == "__main__":
    import shapy
    poly = [(4,4),(10,4),(10,10),(4,10),(4,4)]

    #
##    import pydraw
##    crs = pydraw.CoordinateSystem([-30,-30,30,30])
##    img = pydraw.Image(400,400, crs=crs)
##    img.drawpolygon(poly)
##    for line in _pairwise(poly):
##        (x1,y1),(x2,y2) = line
##        left = _Line(x1,y1,x2,y2).getbuffersides(10.2)[0]
##        (x1,y1),(x2,y2) = left.tolist()
##        print x1,y1,x2,y2
##        img.drawline(x1,y1,x2,y2, fillcolor=(222,0,0))
##    img.view()
    #
    
##    g = shapy.Polygon(poly)
##    g.view(tickunit=1)
##    
    newpoly = bufferpolygon(poly, -10.2, jointype="bevel")
    print(newpoly)
    g = shapy.Polygon(newpoly)
    g.view(tickunit=1)


    
