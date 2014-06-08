#GEOMETRY HELPER CLASSES
import math

class _Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def getbuffer(self, fillsize, resolution=0.75):
        #alternative circle algorithms
            ### BEST: http://yellowsplash.wordpress.com/2009/10/23/fast-antialiased-circles-and-ellipses-from-xiaolin-wus-concepts/
            #http://stackoverflow.com/questions/1201200/fast-algorithm-for-drawing-filled-circles
            #http://willperone.net/Code/codecircle.php
            #http://www.mathopenref.com/coordcirclealgorithm.html
        #use bezier circle path
        size = fillsize
        c = 0.55191502449*size #0.55191502449 http://spencermortensen.com/articles/bezier-circle/ #alternative nr: 0.551784 http://www.tinaja.com/glib/ellipse4.pdf
        relcontrolpoints = [(0,size),(c,size),(size,c),
                 (size,0),(size,-c),(c,-size),
                 (0,-size),(-c,-size),(-size,-c),
                 (-size,0),(-size,c),(-c,size),(0,size)]
        circlepolygon = []
        oldindex = 1
        for index in xrange(4):
            cornerpoints = relcontrolpoints[oldindex-1:oldindex+3]
            cornerpoints = [(self.x+relx,self.y+rely) for relx,rely in cornerpoints]
            circlepolygon.extend(_Bezier(cornerpoints, intervals=int(round(resolution*fillsize*3))).coords)
            oldindex += 3
        return circlepolygon

class _Line:
    def __init__(self, x1,y1,x2,y2):
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
    def tolist(self):
        return ((self.x1,self.y1),(self.x2,self.y2))
    def intersect(self, otherline, infinite=False):
        """
        Input must be another line instance
        Finds real or imaginary intersect assuming lines go forever, regardless of real intersect
        Infinite is based on http://stackoverflow.com/questions/20677795/find-the-point-of-intersecting-lines
        Real is based on http://stackoverflow.com/questions/18234049/determine-if-two-lines-intersect
        """
        if infinite:
            D  = -self.ydiff * otherline.xdiff - self.xdiff * -otherline.ydiff
            Dx = self._selfprod() * otherline.xdiff - self.xdiff * otherline._selfprod()
            Dy = -self.ydiff * otherline._selfprod() - self._selfprod() * -otherline.ydiff
            if D != 0:
                x = Dx / D
                y = Dy / D
                return x,y
            else:
                return False
        else:
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
                return ix,iy
            else:
                return False
    def distance2point(self, point, getpoint=False, relativedist=False):
        """
        - point is a _Point instance with x and y attributes
        - getpoint, when True will not only return the distance but also the point on the line that was closest, in a tuple (dist, _Point instance)
        - relativedist, if comparing many distances is more important than getting the actual distance then this can be set to True which will return the squared distance without the squareroot which makes it faster
        """
        x3,y3 = point.x,point.y
        x1,y1,x2,y2 = self.x1,self.y1,self.x2,self.y2
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
        if getpoint: result = (dist,_Point(x,y))
        else: result = dist
        return result
    def getlength(self):
        return math.hypot(self.xdiff,self.ydiff)
    def getangle(self):
        "hmm, sometimes returns negative angles instead of converting..."
        try:
            angle = math.degrees(math.atan(self.ydiff/float(self.xdiff)))
            if self.xdiff < 0:
                angle = 180 - angle
            else:
                angle *= -1
        except ZeroDivisionError:
            if self.ydiff < 0:
                angle = 90
            elif self.ydiff > 0:
                angle = 270
            else:
                raise TypeError("error: the vector isnt moving anywhere, so has no angle")
        if angle < 0:
            angle = 360+angle
        return angle
    def walkdistance(self, distance):
        angl_rad = math.radians(self.getangle())
        xbuff = distance * math.cos(angl_rad)
        ybuff = distance * math.sin(angl_rad)
        newx = self.x2-xbuff
        newy = self.y2+ybuff
        return (newx,newy)
    def getbuffersides(self, linebuffer):
        x1,y1,x2,y2 = self.x1,self.y1,self.x2,self.y2
        midline = _Line(x1,y1,x2,y2)
        angl = midline.getangle()
        perpangl_rad = math.radians(angl-90) #perpendicular angle in radians
        xbuff = linebuffer * math.cos(perpangl_rad)
        ybuff = linebuffer * math.sin(perpangl_rad)
        #xs
        leftx1 = (x1-xbuff)
        leftx2 = (x2-xbuff)
        rightx1 = (x1+xbuff)
        rightx2 = (x2+xbuff)
        #ys
        lefty1 = (y1+ybuff)
        lefty2 = (y2+ybuff)
        righty1 = (y1-ybuff)
        righty2 = (y2-ybuff)
        #return lines
        leftline = _Line(leftx1,lefty1,leftx2,lefty2)
        rightline = _Line(rightx1,righty1,rightx2,righty2)
        return leftline,rightline
    def anglediff(self, otherline):
        """
        not complete.
        - is left turn, + is right turn
        """
        angl1 = self.getangle()
        angl2 = otherline.getangle()
        bwangl_rel = angl1-angl2 # - is left turn, + is right turn
        #make into shortest turn direction
        if bwangl_rel < -180:
            bwangl_rel = bwangl_rel+360
        elif bwangl_rel > 180:
            bwangl_rel = bwangl_rel-360
        return bwangl_rel
    def anglebetween_inner(self, otherline):
        "not complete"
        crossvecx = self.ydiff-otherline.ydiff
        crossvecy = otherline.xdiff-self.xdiff
        line = _Line(self.x2,self.y2,self.x2+crossvecx,self.y2+crossvecy)
        bwangl = line.getangle()
        return bwangl
    def anglebetween_outer(self, otherline):
        "not complete"
        bwangl = self.anglebetween_inner(otherline)
        if bwangl > 180:
            normangl = bwangl-180
        else:
            normangl = 180+bwangl
        return normangl
    
    #INTERNAL USE ONLY
    def _selfprod(self):
        """
        Used by the line intersect method
        """
        return -(self.x1*self.y2 - self.x2*self.y1)
    
class _Bezier:
    def __init__(self, xypoints, intervals=100):
        # xys should be a sequence of 2-tuples (Bezier control points)
        def pascal_row(n):
            # This returns the nth row of Pascal's Triangle
            result = [1]
            x, numerator = 1, n
            for denominator in range(1, n//2+1):
                # print(numerator,denominator,x)
                x *= numerator
                x /= denominator
                result.append(x)
                numerator -= 1
            if n&1 == 0:
                # n is even
                result.extend(reversed(result[:-1]))
            else:
                result.extend(reversed(result)) 
            return result
        n = len(xypoints)
        combinations = pascal_row(n-1)
        ts = (t/float(intervals) for t in xrange(intervals+1))
        # This uses the generalized formula for bezier curves
        # http://en.wikipedia.org/wiki/B%C3%A9zier_curve#Generalization
        result = []
        for t in ts:
            tpowers = (t**i for i in range(n))
            upowers = reversed([(1-t)**i for i in range(n)])
            coefs = [c*a*b for c, a, b in zip(combinations, tpowers, upowers)]
            result.append(
                tuple(sum([coef*p for coef, p in zip(coefs, ps)]) for ps in zip(*xypoints)))
        self.coords = result

def _Arc(x, y, radius, opening=None, facing=None, startangle=None, endangle=None, clockwise=True):
    """
    Original taken directly from: http://www.daniweb.com/software-development/python/threads/321181/python-bresenham-circle-arc-algorithm
    Python implementation of the modified Bresenham algorithm 
    for complete circles, arcs and pies
    radius: radius of the circle in pixels
    start and end are angles in degrees
    function will return a list of points (tuple coordinates)
    and the coordinates of the start and end point in a list xy
    """
    #define main function
    def getarc(x, y, radius, start, end, clockwise=True):
        """
        Restricted function only used by this _Arc function
        Start has to be lower than end.
        Also, start has to be bigger than 0, and end lower than 360,
        so not possible with an arc that traverses the north point.
        This is instead accounted for and support in the main _Arc function
        """
        xanchor,yanchor = x,y
        # round it to avoid rounding errors and wrong drawn pie slices
        start = math.radians(round(start))    
        end = math.radians(round(end))
        if start>=math.pi*2:
            start = math.radians(math.degrees(start)%360)
        if end>=math.pi*2:
            end = math.radians(math.degrees(end)%360)
        # always clockwise drawing, if anti-clockwise drawing desired
        # exchange start and end
        if not clockwise:
            s = start
            start = end
            end = s
        # determination which quarters and octants are necessary
        # init vars
        xy = [[0,0], [0,0]] # to locate actual start and end point for pies
        # the x/y border value for drawing the points
        q_x = []
        q_y = []
        # first q element in list q is quarter of start angle
        # second q element is quarter of end angle
        # now determine the quarters to compute
        q = []
        # 0 - 90 degrees = 12 o clock to 3 o clock = 0.0 - math.pi/2 --> q==1
        # 90 - 180 degrees = math.pi/2 - math.pi --> q==2
        # 180 - 270 degrees = math.pi - math.pi/2*3 --> q==3
        # 270 - 360 degrees = math.pi/2*3 - math.pi*2 --> q==4
        j = 0
        for i in [start, end]:
            angle = i
            if angle<math.pi/2:
                q.append(1)
                # compute the minimum x and y-axis value for plotting
                q_x.append(int(round(math.sin(angle)*radius)))
                q_y.append(int(round(math.cos(angle)*radius)))
                if j==1 and angle==0:
                    xy[1] = [0,-radius] # 90 degrees 
            elif angle>=math.pi/2 and angle<math.pi:
                q.append(2)
                # compute the minimum x and y-axis value for plotting
                q_x.append(int(round(math.cos(angle-math.pi/2)*radius)))
                q_y.append(int(round(math.sin(angle-math.pi/2)*radius)))
                if j==1 and angle==math.pi/2:
                    xy[1] = [radius,0] # 90 degrees
            elif angle>=math.pi and angle<math.pi/2*3:
                q.append(3)
                # compute the minimum x and y-axis value for plotting
                q_x.append(int(round(math.sin(angle-math.pi)*radius)))
                q_y.append(int(round(math.cos(angle-math.pi)*radius)))
                if j==1 and angle==math.pi:
                    xy[1] = [0, radius]
            else:
                q.append(4)
                # compute the minimum x and y-axis value for plotting
                q_x.append(int(round(math.cos(angle-math.pi/2*3)*radius)))
                q_y.append(int(round(math.sin(angle-math.pi/2*3)*radius)))
                if j==1 and angle==math.pi/2*3:
                    xy[1] = [-radius, 0]
            j = j + 1
        # print "q", q, "q_x", q_x, "q_y", q_y
        quarters = []
        sq = q[0]
        while 1:
            quarters.append(sq)
            if q[1] == sq and start<end or q[1] == sq and start>end and q[0]!=q[1]:
                break # we reach the final end quarter
            elif q[1] == sq and start>end:
                quarters.extend([(sq+1)%5, (sq+2)%5, (sq+3)%5, (sq+4)%5])
                break
            else:
                sq = sq + 1
                if sq>4:
                    sq = 1
        # print "quarters", quarters
        switch = 3 - (2 * radius)
        points = []
        points1 = set()
        points2 = set()
        points3 = set()
        points4 = set()
        # 
        x = 0
        y = int(round(radius))
        # first quarter/octant starts clockwise at 12 o'clock
        while x <= y:
            if 1 in quarters:
                if not (1 in q):
                    # add all points of the quarter completely
                    # first quarter first octant
                    points1.add((x,-y))
                    # first quarter 2nd octant
                    points1.add((y,-x))
                else:
                    # start or end point in this quarter?
                    if q[0] == 1: 
                        # start point
                        if q_x[0]<=x and q_y[0]>=abs(-y) and len(quarters)>1 or q_x[0]<=x and q_x[1]>=x:
                            # first quarter first octant
                            points1.add((x,-y))
                            if -y<xy[0][1]:
                                xy[0] = [x,-y]
                            elif -y==xy[0][1]:
                                if x<xy[0][0]:
                                    xy[0] = [x,-y]
                        if q_x[0]<=y and q_y[0]>=x and len(quarters)>1 or q_x[0]<=y and q_x[1]>=y and q_y[0]>=abs(-x) and q_y[1]<=abs(-x):
                            # first quarter 2nd octant
                            points1.add((y,-x))
                            if -x<xy[0][1]:
                                xy[0] = [y,-x]
                            elif -x==xy[0][1]:
                                if y<xy[0][0]:
                                    xy[0] = [y,-x]
                    if q[1] == 1:
                        # end point
                        if q_x[1]>=x and len(quarters)>1 or q_x[0]<=x and q_x[1]>=x:
                            # first quarter first octant
                            points1.add((x,-y))
                            if x>xy[1][0]:
                                xy[1] = [x,-y]
                            elif x==xy[1][0]:
                                if -y>xy[1][1]:
                                    xy[1] = [x,-y]
                        if q_x[1]>=y and q_y[1]<=x and len(quarters)>1 or q_x[0]<=y and q_x[1]>=y and q_y[0]>=abs(-x) and q_y[1]<=abs(-x):
                            # first quarter 2nd octant
                            points1.add((y,-x))
                            if y>xy[1][0]:
                                xy[1] = [y,-x]
                            elif y==xy[1][0]:
                                if -x>xy[1][1]:
                                    xy[1] = [y,-x]
            if 2 in quarters:
                if not (2 in q):
                    # add all points of the quarter completely
                    # second quarter 3rd octant
                    points2.add((y,x))
                    # second quarter 4.octant
                    points2.add((x,y))
                else:
                    # start or end point in this quarter?
                    if q[0] == 2: 
                        # start point
                        if q_x[0]>=y and q_y[0]<=x and len(quarters)>1 or q_x[0]>=y and q_x[1]<=y and q_y[0]<=x and q_y[1]>=x:
                            # second quarter 3rd octant
                            points2.add((y,x))
                            if y>xy[0][0]:
                                xy[0] = [y,x]
                            elif y==xy[0][0]:
                                if x<xy[0][1]:
                                    xy[0] = [y,x]
                        if q_x[0]>=x and q_y[0]<=y and len(quarters)>1 or q_x[0]>=x and q_x[1]<=x and q_y[0]<=y and q_y[1]>=y:
                            # second quarter 4.octant
                            points2.add((x,y))
                            if x>xy[0][0]:
                                xy[0] = [x,y]
                            elif x==xy[0][0]:
                                if y<xy[0][1]:
                                    xy[0] = [x,y]                        
                    if q[1] == 2:
                        # end point
                        if q_x[1]<=y and q_y[1]>=x and len(quarters)>1 or q_x[0]>=y and q_x[1]<=y and q_y[0]<=x and q_y[1]>=x:
                            # second quarter 3rd octant
                            points2.add((y,x))
                            if x>xy[1][1]:
                                xy[1] = [y,x]
                            elif x==xy[1][1]:
                                if y<xy[1][0]:
                                    xy[1] = [y,x]
                        if q_x[1]<=x and q_y[1]>=y and len(quarters)>1 or q_x[0]>=x and q_x[1]<=x and q_y[0]<=y and q_y[1]>=y:
                            # second quarter 4.octant
                            points2.add((x,y))
                            if y>xy[1][1]:
                                xy[1] = [x,y]
                            elif x==xy[1][1]:
                                if x<xy[1][0]:
                                    xy[1] = [x,y]
            if 3 in quarters:    
                if not (3 in q):
                    # add all points of the quarter completely
                    # third quarter 5.octant
                    points3.add((-x,y))        
                    # third quarter 6.octant
                    points3.add((-y,x))
                else:
                    # start or end point in this quarter?
                    if q[0] == 3:
                        # start point
                        if q_x[0]<=x and q_y[0]>=abs(y) and len(quarters)>1 or q_x[0]<=x and q_x[1]>=x:
                            # third quarter 5.octant
                            points3.add((-x,y))
                            if y>xy[0][1]:
                                xy[0] = [-x,y]
                            elif y==xy[0][1]:
                                if -x>xy[0][0]:
                                    xy[0] = [-x,y]                        
                        if q_x[0]<=y and q_y[0]>=x and len(quarters)>1 or q_x[0]<=y and q_x[1]>=y and q_y[0]>=x and q_y[1]<=x:
                            # third quarter 6.octant
                            points3.add((-y,x))
                            if x>xy[0][1]:
                                xy[0] = [-y,x]
                            elif x==xy[0][1]:
                                if -y>xy[0][0]:
                                    xy[0] = [-y,x]                                                
                    if q[1] == 3:
                        # end point
                        if q_x[1]>=x and len(quarters)>1 or q_x[0]<=x and q_x[1]>=x:
                            # third quarter 5.octant
                            points3.add((-x,y))
                            if -x<xy[1][0]:
                                xy[1] = [-x,y]
                            elif -x==xy[1][0]:
                                if y<xy[1][1]:
                                    xy[1] = [-x,y]
                        if q_x[1]>=y and q_y[1]<=x and len(quarters)>1 or q_x[0]<=y and q_x[1]>=y and q_y[0]>=x and q_y[1]<=x:
                            # third quarter 6.octant
                            points3.add((-y,x))
                            if -y<xy[1][0]:
                                xy[1] = [-y,x]
                            elif -y==xy[1][0]:
                                if x<xy[1][1]:
                                    xy[1] = [-y,x]                        
            if 4 in quarters:
                if not (4 in q):
                    # add all points of the quarter completely
                    # fourth quarter 7.octant
                    points4.add((-y,-x))
                    # fourth quarter 8.octant
                    points4.add((-x,-y))
                else:
                    # start or end point in this quarter?
                    if q[0] == 4: 
                        # start point
                        if q_x[0]>=y and q_y[0]<=x and len(quarters)>1 or q_x[0]>=y and q_x[1]<=y and q_y[0]<=x and q_y[1]>=x:
                            # fourth quarter 7.octant
                            points4.add((-y,-x))
                            if -y<xy[0][0]:
                                xy[0] = [-y,-x]
                            elif -y==xy[0][0]:
                                if -x>xy[0][1]:
                                    xy[0] = [-y,-x]
                        if q_x[0]>=x and q_y[0]<=abs(-y) and len(quarters)>1 or q_x[0]>=x and q_x[1]<=x and q_y[0]<=y and q_y[1]>=y:
                            # fourth quarter 8.octant
                            points4.add((-x,-y))
                            if -x<xy[0][0]:
                                xy[0] = [-x,-y]
                            elif -x==xy[0][0]:
                                if -y>xy[0][1]:
                                    xy[0] = [-x,-y]
                    if q[1] == 4:
                        # end point
                        if q_x[1]<=y and q_y[1]>=x and len(quarters)>1 or q_x[0]>=y and q_x[1]<=y  and q_y[0]<=x and q_y[1]>=x:
                            # fourth quarter 7.octant
                            points4.add((-y,-x))
                            if -x<xy[1][1]:
                                xy[1] = [-y,-x]
                            elif -x==xy[1][1]:
                                if -y>xy[1][0]:
                                    xy[1] = [-y,-x]
                        if q_x[1]<=x and q_y[1]>=abs(-y) and len(quarters)>1 or q_x[0]>=x and q_x[1]<=x and q_y[0]<=y and q_y[1]>=y:
                            # fourth quarter 8.octant
                            points4.add((-x,-y))
                            if -y<xy[1][1]:
                                xy[1] = [-x,-y]
                            elif -y==xy[1][1]:
                                if -x>xy[1][0]:
                                    xy[1] = [-x,-y]
            if switch < 0:
                switch = switch + (4 * x) + 6
            else:
                switch = switch + (4 * (x - y)) + 10
                y = y - 1
            x = x + 1
        if 1 in quarters:
            points1_s = list(points1)
            points1_s.sort() # if for some reason you need them sorted
            points.extend(points1_s)
        if 2 in quarters:
            points2_s = list(points2)
            points2_s.sort() # if for some reason you need them sorted
            points2_s.reverse() # # if for some reason you need in right order
            points.extend(points2_s)
        if 3 in quarters:        
            points3_s = list(points3)
            points3_s.sort()
            points3_s.reverse()
            points.extend(points3_s)
        if 4 in quarters:    
            points4_s = list(points4)
            points4_s.sort()
            points.extend(points4_s)
        #place the coords relative to the xy anchor point
        points = [(xanchor+arcx,yanchor+arcy) for arcx,arcy in points]
        return points #, xy

    #flexible approach of creating any type of arc
    if startangle != None and endangle != None:
        #use precomputed startend angles
        pass
    else:
        #compute angles from user input
        halfopen = opening/2.0
        startangle = facing-halfopen
        if startangle < 0:
            startangle += 360
        endangle = facing+halfopen
        if endangle > 360:
            endangle -= 360
    #collect coords
    arccoords = []
    if startangle > endangle:
        #if crosses the north 0/360 point
        arccoords.extend(getarc(x, y, radius, start=startangle, end=359))
        arccoords.extend(getarc(x, y, radius, start=0, end=endangle))
    else:
        arccoords.extend(getarc(x, y, radius, start=startangle, end=endangle))
    return arccoords

if __name__ == "__main__":
    
    import pydraw
    
    line = _Line(10,10,1,2)
    point = _Point(5,10)
    dist,closestpoint = line.distance2point(point, getpoint=True)
    print "closestpoint2line",dist,closestpoint.x,closestpoint.y,point.x,point.y

    pointdirection = _Line(closestpoint.x,closestpoint.y,point.x,point.y)
    walkdest = pointdirection.walkdistance(dist)
    print "walkdist and destination",dist,walkdest

    line1 = _Line(5,5,5.2,0)
    line2 = _Line(5,5,5,7)
    diff = line1.anglediff(line2)
    inner = line1.anglebetween_inner(line2)
    outer = line1.anglebetween_outer(line2)
    print "angles bw",line1.getangle(),line2.getangle(),diff,inner,outer
    
