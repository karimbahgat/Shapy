
import math
from random import randrange
from collections import defaultdict

class Point:
    def __init__(self, x,y):
        self.x = float(x)
        self.y = float(y)
        self.isec = False
    def __repr__(self):
        if self.isec:
            return repr(("i",self.x,self.y))
        return repr((self.x,self.y))
    def __len__(self):
        return 2
    def __iter__(self):
        yield self.x
        yield self.y
    def __getitem__(self, i):
        return (self.x,self.y)[i]

def intersect_lineseg_lineseg(p1, p2, q1, q2):
	"""Intersect two line segments
	@type p1: Vector
	@param p1: The first point on the first line segment
	@type p2: Vector
	@param p2: The second point on the first line segment
	@type q1: Vector
	@param q1: The first point on the secondline segment
	@type q2: Vector
	@param q2: The second point on the second line segment
	"""

	if max(q1.x, q2.x) < min(p1.x, p2.x): return None
	if min(q1.x, q2.x) > max(p1.x, p2.x): return None
	if max(q1.y, q2.y) < min(p1.y, p2.y): return None
	if min(q1.y, q2.y) > max(p1.y, p2.y): return None

	ll = __intersect_line_line_u(p1, p2, q1, q2)

	if ll == None: return None
	if ll[0] < 0 or ll[0] > 1: return None
	if ll[1] < 0 or ll[1] > 1: return None

	return Point(p1.x + ll[0] * (p2.x - p1.x) , p1.y + ll[0] * (p2.y - p1.y))

def __intersect_line_line_u(p1, p2, q1, q2):

	d = (q2.y - q1.y) * (p2.x - p1.x) - (q2.x - q1.x) * (p2.y - p1.y)
	n1 = (q2.x - q1.x) * (p1.y - q1.y) - (q2.y - q1.y) * (p1.x - q1.x)
	n2 = (p2.x - p1.x) * (p1.y - q1.y) - (p2.y - p1.y) * (p1.x - q1.x)

	if d == 0: return None

	u_a = float(n1) / d
	u_b = float(n2) / d

	return (u_a, u_b)

def decompose(poly_points):
    """Decompose a possibly self-intersecting polygon into multiple simple polygons."""

    def inorder_extend(v, v1, v2, ints):
            """Extend a sequence v by points ints that are on the segment v1, v2"""

            k, r = None, False
            if v1.x < v2.x:
                    k = lambda i: i.x
                    r = True
            elif v1.x > v2.x:
                    k = lambda i: i.x
                    r = False
            elif v1.y < v2.y:
                    k = lambda i: i.y
                    r = True
            else:
                    k = lambda i: i.y
                    r = False

            l = sorted(ints, key=k, reverse=r)
            i = next((i for i, p in enumerate(v) if p == v2), -1)
            assert(i>=0)

            for e in l:
                    e.isec = True
                    v.insert(i, e)

    pts = [p for p in poly_points]

    # find self-intersections
    ints = defaultdict(list)
    for i in range(len(pts)):
            for j in range(i+1, len(pts)):
                    a = pts[i]
                    b = pts[(i+1)%len(pts)]
                    c = pts[j]
                    d = pts[(j+1)%len(pts)]

                    x = intersect_lineseg_lineseg(a, b, c, d)
                    if x and x not in (a,b,c,d):
                            ints[(a,b)].append( x )
                            ints[(c,d)].append( x )

    # add self-intersection points to poly
    for k, v in ints.iteritems():
            inorder_extend(pts, k[0], k[1], v)

    # build a list of loops
    pending = []
    finished = []
    pts = (pt for pt in pts)
    def nextisec(pts):
        pt = start = next(pts, None)
        if not pt: return None
        seg = []
        while True:
            seg.append(pt)
            if pt.isec == True or pt == start:
                return seg
            pt = next(pts, None)
    seg = nextisec(pts)
    while seg:
        print "seg",seg
        for i,pend in enumerate(pending):
            # test adding on previous
            #print "pend",pend
            if seg[0] == pend[-1]:
                pend.extend(seg)
            elif seg[-1] == pend[0]:
                pend,seg = seg,pend
                pend.extend(seg)
            elif seg[0] == pend[0]:
                seg = list(reversed(seg))
                pend.extend(seg)
            elif seg[-1] == pend[-1]:
                seg = list(reversed(seg))
                pend,seg = seg,pend
                pend.extend(seg)
            # test completion
            if len(pend) > 1 and pend[0] == pend[-1]:
                finished.append(pending.pop(i))
        else:
            # no correspondance to prev pendings, so create new pending subpoly
            pend = seg
            pending.append(pend)
        seg = nextisec(pts)

    return finished



crazypoly = [Point(randrange(500),randrange(500)) for _ in range(100)]
decomp = decompose(crazypoly)
print len(crazypoly), len(decomp)

import pyagg
cnv = pyagg.Canvas(500,500)

##cnv.draw_polygon(crazypoly, fillcolor=(randrange(222),randrange(222),randrange(222),211))
##for pt in decomp:
##    print pt
##    cnv.draw_circle(pt, fillsize=2)
    
for p in decomp:
    print p
    cnv.draw_polygon(p, fillcolor=(randrange(222),randrange(222),randrange(222),211))

cnv.view()

