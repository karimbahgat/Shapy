
import math
from random import randrange
from collections import defaultdict

class Point:
    def __init__(self, x,y):
        self.x = float(x)
        self.y = float(y)
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

	return Vector(p1.x + ll[0] * (p2.x - p1.x) , p1.y + ll[0] * (p2.y - p1.y) )

def __intersect_line_line_u(p1, p2, q1, q2):

	d = (q2.y - q1.y) * (p2.x - p1.x) - (q2.x - q1.x) * (p2.y - p1.y)
	n1 = (q2.x - q1.x) * (p1.y - q1.y) - (q2.y - q1.y) * (p1.x - q1.x)
	n2 = (p2.x - p1.x) * (p1.y - q1.y) - (p2.y - p1.y) * (p1.x - q1.x)

	if d == 0: return None

	u_a = float(n1) / d
	u_b = float(n2) / d

	return (u_a, u_b)

class Vector(object):
	"""Class for 2D Vectors.
	Vectors v have an x and y component that can be accessed multiple ways:
		- v.x, v.y
		- v[0], v[1]
		- x,y = v.as_tuple()
	"""

	def __init__(self, x, y):
		"""Create a new vector object.
		@type x: float
		@param x: The X component of the vector
		@type y: float
		@param y: The Y component of the vector
		"""

		self.x = x
		self.y = y


	def get_length(self):
		"""Get the length of the vector."""
		return math.sqrt(self.get_length_squared())

	def get_length_squared(self):
		"""Get the squared length of the vector, not calculating the square root for a performance gain"""
		return self.x * self.x + self.y * self.y;

	def get_slope(self):
		"""Get the slope of the vector, or float('inf') if x == 0"""
		if self.x == 0: return float('inf')
		return float(self.y)/self.x

	def normalize(self):
		"""Return a normalized version of the vector that will always have a length of 1."""
		return self / self.get_length()

	def clamp(self):
		"""Return a vector that has the same direction than the current vector, but is never longer than 1."""
		if self.get_length() > 1:
			return self.normalize()
		else:
			return self

	def clone(self):
		"""Return a copy of this vector"""
		return Vector(self.x, self.y)

	def normal(self):
		"""Return a normal vector of this vector"""
		return Vector(-self.y, self.x)

	def as_tuple(self):
		"""Convert the vector to a non-object tuple"""
		return (self.x, self.y)

	def __add__(self, b):
		return Vector(self.x + b.x, self.y + b.y)

	def __sub__(self, b):
		return Vector(self.x - b.x, self.y - b.y)

	def __mul__(self, val):

		if isinstance(val, Vector):
			return self.x * val.x + self.y * val.y
		else:
			return Vector(self.x * val, self.y * val)

	def __div__(self, val):
		return Vector(self.x / val, self.y / val)

	def __repr__(self):
		return "Vector(%.3f, %.3f)" % (self.x, self.y)

	def __eq__(self, other):
		if not isinstance(other, Vector): return False
		d = self - other
		return abs(d.x) < EPSILON and abs(d.y) < EPSILON

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return hash("%.4f %.4f" % (self.x, self.y))

	def __getitem__(self, key):
		if key == 0: return self.x
		elif key == 1: return self.y
		else: raise KeyError('Invalid key: %s. Valid keys are 0 and 1 for x and y' % key)

	def __setitem__(self, key, value):
		if key == 0: self.x = value
		elif key == 1: self.y = value
		else: raise KeyError('Invalid key: %s. Valid keys are 0 and 1 for x and y' % key)

	length = property(get_length, None, None)
	length_squared = property(get_length_squared, None, None)

	slope = property(get_slope, None, None)

VECTOR_NULL = Vector(0,0)
VECTOR_X = Vector(1,0)
VECTOR_Y = Vector(0,1)
EPSILON = 0.0001

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
    out = []
    while pts:

            # build up a list of seen points until we re-visit one - a loop!
            seen = []
            for p in pts + [pts[0]]:
                    if p not in seen:
                            seen.append(p)
                    else:
                            break

            loop = seen[seen.index(p):]

            # remove the loop from pts
            for p in loop:
                    pts.remove(p)

            out.append(loop)

    return out



crazypoly = [Point(randrange(500),randrange(500)) for _ in range(10)]
decomp = decompose(crazypoly)
print len(crazypoly), len(decomp)

import pyagg
cnv = pyagg.Canvas(500,500)
for p in decomp:
    p = [(float(pt.x),float(pt.y)) for pt in p]
    print p
    cnv.draw_polygon(p, fillcolor=(randrange(222),randrange(222),randrange(222),211))
cnv.view()

