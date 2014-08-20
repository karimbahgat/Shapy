# -*- coding: UTF-8 -*-
# Efficient Clipping of Arbitrary Polygons
#
# Copyright (c) 2011, 2012 Helder Correia <helder.mc@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""Efficient Clipping of Arbitrary Polygons

Based on the paper "Efficient Clipping of Arbitrary Polygons" by Günther
Greiner (greiner[at]informatik.uni-erlangen.de) and Kai Hormann
(hormann[at]informatik.tu-clausthal.de), ACM Transactions on Graphics
1998;17(2):71-83.

Available at: http://www.inf.usi.ch/hormann/papers/Greiner.1998.ECO.pdf

You should have received the README file along with this program.
If not, see <https://github.com/helderco/polyclip>
"""


class Vertex(object):
    """Node in a circular doubly linked list.

    This class is almost exactly as described in the paper by Günther/Greiner.
    """

    def __init__(self, vertex, alpha=0.0, intersect=False, entry=True, checked=False):
        if isinstance(vertex, Vertex):
            vertex = (vertex.x, vertex.y)
            # checked = True

        self.x, self.y = vertex     # point coordinates of the vertex
        self.next = None            # reference to the next vertex of the polygon
        self.prev = None            # reference to the previous vertex of the polygon
        self.neighbour = None       # reference to the corresponding intersection vertex in the other polygon
        self.entry = entry          # True if intersection is an entry point, False if exit
        self.alpha = alpha          # intersection point's relative distance from previous vertex
        self.intersect = intersect  # True if vertex is an intersection
        self.checked = checked      # True if the vertex has been checked (last phase)

##    def isInside(self, poly):
##        """Test if a vertex lies inside a polygon (odd-even rule).
##
##        This function calculates the "winding" number for a point, which
##        represents the number of times a ray emitted from the point to
##        infinity intersects any edge of the polygon.
##
##        An even winding number means the point lies OUTSIDE the polygon;
##        an odd number means it lies INSIDE it.
##        """
##        winding_number = 0
##        infinity = Vertex((1000000000, self.y))
##        for q in poly.iter():
##            if not q.intersect and intersect(self, infinity, q, poly.next(q.next)):
##                winding_number += 1
##
##        return (winding_number % 2) != 0

    def testLocation(self, poly):
        """Test if a vertex lies inside, outside, or on a polygon (odd-even rule).

        This function calculates the "winding" number for a point, which
        represents the number of times a ray emitted from the point to
        infinity intersects any edge of the polygon.

        An even winding number means the point lies OUTSIDE the polygon;
        an odd number means it lies INSIDE it.
        """
        winding_number = 0
        infinity = Vertex((1000000000, self.y))
        for q in poly.iter():
            location = intersect_or_on(self, infinity, q, poly.next(q.next))
            if location == "on":
                return location
            if not q.intersect and location:
                winding_number += 1

        if location == "intersect":
            _inside = (winding_number % 2) != 0
            if _inside: location = "in"
            else: location = "out"

        return location

    def isInside(self, poly):
        """
        Originally from Angus Johnson's Clipper module
        Modified slightly by Karim Bahgat
        """
        pointx,pointy = self.x,self.y
        inside = False
        polypoint = poly.first
        lastpolypointx,lastpolypointy = polypoint.x,polypoint.y
        while True:
            polypoint = polypoint.next
            polypointx,polypointy = polypoint.x,polypoint.y
            if ((((polypointy <= pointy) and (pointy < lastpolypointy)) or \
                ((lastpolypointy <= pointy) and (pointy < polypointy))) and \
                (pointx < (lastpolypointx - polypointx) * (pointy - polypointy) / \
                (lastpolypointy - polypointy) + polypointx)):
                inside = not inside
            lastpolypointx,lastpolypointy = polypoint.x,polypoint.y
            if polypoint.next == poly.first: break
        return inside

    def setChecked(self):
        self.checked = True
        if self.neighbour and not self.neighbour.checked:
            self.neighbour.setChecked()

    def __repr__(self):
        """String representation of the vertex for debugging purposes."""
        return "(%.2f, %.2f) <-> %s(%.2f, %.2f)%s <-> (%.2f, %.2f) %s" % (
            self.prev.x, self.prev.y,
            'i' if self.intersect else ' ',
            self.x, self.y,
            ('e' if self.entry else 'x') if self.intersect else ' ',
            self.next.x, self.next.y,
            ' !' if self.intersect and not self.checked else ''
            )


class Polygon(object):
    """Manages a circular doubly linked list of Vertex objects that represents a polygon."""

    first = None

    def add(self, vertex):
        """Add a vertex object to the polygon (vertex is added at the 'end' of the list")."""
        if not self.first:
            self.first = vertex
            self.first.next = vertex
            self.first.prev = vertex
        else:
            next = self.first
            prev = next.prev
            next.prev = vertex
            vertex.next = next
            vertex.prev = prev
            prev.next = vertex

    def insert(self, vertex, start, end):
        """Insert and sort a vertex between a specified pair of vertices.

        This function inserts a vertex (most likely an intersection point)
        between two other vertices (start and end). These other vertices
        cannot be intersections (that is, they must be actual vertices of
        the original polygon). If there are multiple intersection points
        between the two vertices, then the new vertex is inserted based on
        its alpha value.
        """
        curr = start
        while curr != end and curr.alpha < vertex.alpha:
            curr = curr.next

        vertex.next = curr
        prev = curr.prev
        vertex.prev = prev
        prev.next = vertex
        curr.prev = vertex

    def next(self, v):
        """Return the next non intersecting vertex after the one specified."""
        c = v
        while c.intersect:
            c = c.next
        return c

    @property
    def nextPoly(self):
        """Return the next polygon (pointed by the first vertex)."""
        return self.first.nextPoly

    @property
    def first_intersect(self):
        """Return the first unchecked intersection point in the polygon."""
        for v in self.iter():
            if v.intersect and not v.checked:
                break
        return v

    @property
    def points(self):
        """Return the polygon's points as a list of tuples (ordered coordinates pair)."""
        p = []
        for v in self.iter():
            p.append((v.x, v.y))
        return p

    def unprocessed(self):
        """Check if any unchecked intersections remain in the polygon."""
        for v in self.iter():
            if v.intersect and not v.checked:
                return True
        return False

    def union(self, clip):
        return self.clip(clip, False, False)

    def intersection(self, clip):
        return self.clip(clip, True, True)

    def difference(self, clip):
        return self.clip(clip, False, True)

    def clip(self, clip, s_entry, c_entry):
        """Clip this polygon using another one as a clipper.

        This is where the algorithm is executed. It allows you to make
        a UNION, INTERSECT or DIFFERENCE operation between two polygons.

        Given two polygons A, B the following operations may be performed:

        A|B ... A OR B  (Union of A and B)
        A&B ... A AND B (Intersection of A and B)
        A\B ... A - B
        B\A ... B - A

        The entry records store the direction the algorithm should take when
        it arrives at that entry point in an intersection. Depending on the
        operation requested, the direction is set as follows for entry points
        (f=forward, b=backward; exit points are always set to the opposite):

              Entry
              A   B
              -----
        A|B   b   b
        A&B   f   f
        A\B   b   f
        B\A   f   b

        f = True, b = False when stored in the entry record
        """
        # phase one - find intersections
        anyintersection = False
        for s in self.iter(): # for each vertex Si of subject polygon do
            if not s.intersect:
                for c in clip.iter(): # for each vertex Cj of clip polygon do
                    if not c.intersect:
                        try:
                            i, alphaS, alphaC = intersect(s, self.next(s.next),
                                                          c, clip.next(c.next))
                            iS = Vertex(i, alphaS, intersect=True, entry=False)
                            iC = Vertex(i, alphaC, intersect=True, entry=False)
                            iS.neighbour = iC
                            iC.neighbour = iS

                            self.insert(iS, s, self.next(s.next))
                            clip.insert(iC, c, clip.next(c.next))

                            anyintersection = True
                        except TypeError:
                            pass # this simply means intersect() returned None

        if not anyintersection: # spesial case, no intersections between subject and clip
            resultpolys = []
            if not s_entry and not c_entry: # union
                if clip.first.isInside(self):
                    # clip polygon is entirely inside subject, so just return subject shell
                    clipped = Polygon()
                    for s in self.iter():
                        clipped.add(Vertex(s))
                    polytuple = (clipped, [])
                    resultpolys.append(polytuple)
                elif self.first.isInside(clip):
                    # subject polygon is entirely inside clip, so just return clip shell
                    clipped = Polygon()
                    for c in clip.iter():
                        clipped.add(Vertex(c))
                    polytuple = (clipped, [])
                    resultpolys.append(polytuple)
                else:
                    #clip polygon is entirely outside subject, so return both
                    clipped = Polygon()
                    for s in self.iter():
                        clipped.add(Vertex(s))
                    polytuple = (clipped, [])
                    resultpolys.append(polytuple)
                    clipped = Polygon()
                    for c in clip.iter():
                        clipped.add(Vertex(c))
                    polytuple = (clipped, [])
                    resultpolys.append(polytuple)
            elif s_entry and c_entry: # intersection
                if clip.first.isInside(self):
                    # clip polygon is entirely inside subject, so the intersection is only the clip polygon
                    clipped = Polygon()
                    for c in clip.iter():
                        clipped.add(Vertex(c))
                    polytuple = (clipped, [])
                    resultpolys.append(polytuple)
                elif self.first.isInside(clip):
                    # subject polygon is entirely inside clip, so the intersection is only the subject polygon
                    clipped = Polygon()
                    for s in self.iter():
                        clipped.add(Vertex(s))
                    polytuple = (clipped, [])
                    resultpolys.append(polytuple)
                else:
                    #clip polygon is entirely outside subject, so no intersection to return
                    pass
            elif not s_entry and c_entry: # difference
                if clip.first.isInside(self):
                    # clip polygon is entirely inside subject, so the difference is subject with clip as a hole
                    clipped = Polygon()
                    for s in self.iter():
                        clipped.add(Vertex(s))
                    hole = Polygon()
                    for c in clip.iter():
                        hole.add(Vertex(c))
                    polytuple = (clipped, [hole])
                    resultpolys.append(polytuple)
                elif self.first.isInside(clip):
                    # subject polygon is entirely inside clip, so there is no difference
                    pass
                else:
                    #clip polygon is entirely outside subject, so difference is simply the subject
                    clipped = Polygon()
                    for s in self.iter():
                        clipped.add(Vertex(s))
                    polytuple = (clipped, [])
                    resultpolys.append(polytuple)
            # no need to continue so just return result
            return resultpolys

        # phase two - identify entry/exit points
        s_entry ^= self.first.isInside(clip)
        for s in self.iter():
            if s.intersect:
                s.entry = s_entry
                s_entry = not s_entry

        c_entry ^= clip.first.isInside(self)
        for c in clip.iter():
            if c.intersect:
                c.entry = c_entry
                c_entry = not c_entry

        # phase two - DEGEN SUPPORT ALTERNATIVE
        #(prereq, during intersection phase mark .on flag as True if alphas are 0 or 1)
        #then mark entry/exit as usual, but if .on flag then check prev and next and neighbour location first
##        def testLocation():
##            #do the winding nr inside/outside/on algorithm from holman article, referenced in greiner algo
##            pass
##        def labelEntryExit(s)
##            # degenerate point, ie subject line starts or ends on clipline
##            if s.prev.on:
##                if s.next.on:
##                    # on -> on -> on, ie lines run along each other
##                    pass
##                elif s.next.testLocation == "in":
##                    # on -> on -> inside
##                    pass
##                elif s.next.testLocation == "out":
##                    # on -> on -> outside
##                    pass
##            elif s.prev.testLocation == "in":
##                if s.next.on:
##                    pass
##                elif s.next.testLocation == "in":
##                    pass
##                elif s.next.testLocation == "out":
##                    # in -> on -> out #normal toggle?
##                    pass
##            elif s.prev.testLocation == "out":
##                if s.next.on:
##                    pass
##                elif s.next.testLocation == "in":
##                    # out -> on -> in #normal toggle?
##                    pass
##                elif s.next.testLocation == "out":
##                    pass
##        s_entry ^= self.first.isInside(clip)
##        for s in self.iter():
##            if s.intersect:
##                if s.on:
##                    #intersection is degenerate, is the start/endpoint of a line
##                    #so label entry/exit based on prev/next locations
##                    labelEntryExit(s)
##                    # finally do all the same for neighbour
##                    labelEntryExit(s.neighbour)
##                    pass
##                else:
##                    #pure inside or outside, so use normal entry toggle
##                    s.entry = s_entry
##                    s_entry = not s_entry

        # phase three - construct a list of clipped polygons
        resultpolys = []
        while self.unprocessed():
            current = self.first_intersect
            clipped = Polygon()
            clipped.add(Vertex(current))
            while True:
                current.setChecked()
                if current.entry:
                    while True:
                        current = current.next
                        clipped.add(Vertex(current))
                        if current.intersect:
                            break
                else:
                    while True:
                        current = current.prev
                        clipped.add(Vertex(current))
                        if current.intersect:
                            break

                current = current.neighbour
                if current.checked:
                    break

            polytuple = (clipped, [])
            resultpolys.append(polytuple)

        #sort into exteriors and holes
        for pindex,(polyext,polyholes) in enumerate(resultpolys):
            for otherext,otherholes in resultpolys:
                if polyext == otherext:
                    continue # don't compare to self
                if polyext.first.isInside(otherext):
                    otherholes.append(polyext) #poly is within other so make into a hole
                    del resultpolys[pindex] #and delete poly from being an independent poly
        return resultpolys

    def __repr__(self):
        """String representation of the polygon for debugging purposes."""
        count, out = 1, "\n"
        for s in self.iter():
            out += "%02d: %s\n" % (count, str(s))
            count += 1
        return out

    def iter(self):
        """Iterator generator for this doubly linked list."""
        s = self.first
        while True:
            yield s
            s = s.next
            if s == self.first:
                return

    def show_points(self):
        """Draw points in screen for debugging purposes. Depends on OpenGL."""
        glBegin(GL_POINTS)
        for s in self.iter():
            glVertex2f(s.x, s.y)
        glEnd()


def intersect(s1, s2, c1, c2):
    """Test the intersection between two lines (two pairs of coordinates for two points).

    Return the coordinates for the intersection and the subject and clipper alphas if the test passes.

    Algorithm based on: http://paulbourke.net/geometry/lineline2d/
    """
    den = float( (c2.y - c1.y) * (s2.x - s1.x) - (c2.x - c1.x) * (s2.y - s1.y) )

    if not den:
        return None

    us = ((c2.x - c1.x) * (s1.y - c1.y) - (c2.y - c1.y) * (s1.x - c1.x)) / den
    uc = ((s2.x - s1.x) * (s1.y - c1.y) - (s2.y - s1.y) * (s1.x - c1.x)) / den

    if (us == 0 or us == 1) and (0 <= uc <= 1) or\
       (uc == 0 or uc == 1) and (0 <= us <= 1):
        print "whoops! degenerate case!"
        return None

    elif (0 < us < 1) and (0 < uc < 1):
        x = s1.x + us * (s2.x - s1.x)
        y = s1.y + us * (s2.y - s1.y)
        return (x, y), us, uc

    return None

def intersect_or_on(s1, s2, c1, c2):
    """Same as intersect(), except returns
    either "intersect","on",or None if no intersection.
    """
    den = float( (c2.y - c1.y) * (s2.x - s1.x) - (c2.x - c1.x) * (s2.y - s1.y) )

    if not den:
        return None

    us = ((c2.x - c1.x) * (s1.y - c1.y) - (c2.y - c1.y) * (s1.x - c1.x)) / den
    uc = ((s2.x - s1.x) * (s1.y - c1.y) - (s2.y - s1.y) * (s1.x - c1.x)) / den

    if (us == 0 or us == 1) and (0 <= uc <= 1) or\
       (uc == 0 or uc == 1) and (0 <= us <= 1):
        return "on"

    elif (0 < us < 1) and (0 < uc < 1):
        return "intersect"

    return None

def find_origin(subject, clipper):
    """Find the center coordinate for the given points."""
    x, y = [], []

    for s in subject:
        x.append(s[0])
        y.append(s[1])

    for c in clipper:
        x.append(c[0])
        y.append(c[1])

    x_min, x_max = min(x), max(x)
    y_min, y_max = min(y), max(y)

    width = x_max - x_min
    height = y_max - y_min

    return -x_max / 2, -y_max / 2, -(1.5 * width + 1.5 * height) / 2


def clip_polygon(subject, clipper, operation = 'difference'):
    """
    Higher level function for clipping two polygons (from a list of points).
    Since input polygons are lists of points, output is also in list format.
    Each polygon in the resultlist is a tuple of: (polygon exterior, list of polygon holes)
    """
    Subject = Polygon()
    Clipper = Polygon()

    for s in subject:
        Subject.add(Vertex(s))

    for c in clipper:
        Clipper.add(Vertex(c))

    clipped = Clipper.difference(Subject)\
    if operation == 'reversed-diff'\
    else Subject.__getattribute__(operation)(Clipper)

    clipped = [(ext.points,[hole.points for hole in holes]) for ext,holes in clipped]
    return clipped


def parse_polygon(input_str):
    """construct a polygon based on a string.

    Example input: "1.5,1.25;7.5,2.5;4,3;4.5,6.5"
    """
    try:
        poly = []
        for vertex in input_str.split(';'):
            x, y = vertex.split(',', 2)
            poly.append((float(x), float(y)))

        return poly

    except ValueError:
        return None


if __name__ == "__main__":
    import random
    subjpoly = [(0,0),(6,0),(6,6),(0,6),(0,0)]
    #clippoly = [(4,4),(10,4),(10,10),(4,10),(4,4)] #simple overlap
    clippoly = [(1,4),(3,8),(5,4),(5,10),(1,10),(1,4)] #jigzaw overlap
    #clippoly = [(7,7),(7,9),(9,9),(9,7),(7,7)] #smaller, outside
    #clippoly = [(2,2),(2,4),(4,4),(4,2),(2,2)] #smaller, inside
    #clippoly = [(-1,-1),(-1,7),(7,7),(7,-1),(-1,-1)] #larger, covering all
    #clippoly = [(-10,-10),(-10,-70),(-70,-70),(-70,-10),(-10,-10)] #larger, outside
    #clippoly = [(random.randrange(0,10),random.randrange(0,10)) for _ in range(10)] #random
    resultpolys = clip_polygon(subjpoly,clippoly,"union")
    print "finished:",resultpolys
    import pydraw
    crs = pydraw.CoordinateSystem([-1,-1,11,11])
    img = pydraw.Image(400,400, crs=crs)
    img.drawpolygon(subjpoly, fillcolor=(222,0,0))
    img.drawpolygon(clippoly, fillcolor=(0,222,0))
    for ext,holes in resultpolys:
        img.drawpolygon(ext,holes)
    img.drawgridticks(1,1)
    img.view()
    
