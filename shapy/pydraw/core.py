# Pydraw submodule
# The main core for creating, loading, and drawing on images

import sys,os,math,operator,itertools
#import submodules
import _fileformats
from _fileformats import png,bmp
import geomhelper
from geomhelper import _Line, _Bezier, _Arc


#PYTHON VERSION CHECKING
PYTHON3 = int(sys.version[0]) == 3
if PYTHON3:
    xrange = range
    range = list(range)
    import tkinter as tk
else:
    import Tkinter as tk


#THE CLASSES

class Image(object):
    #STARTING
    def __init__(self,width=None,height=None,background=None,filepath=None,data=None,crs=None):
        """
        The main image instance, which can load or create a new image.
        Also has various methods for drawing and transforming the image.

        The following set of options creates and returns a new image instance.

        | **option** | **description**
        | --- | --- 
        | width | the width of the image in pixels, integer
        | height | the height of the image in pixels, integer
        | *background | an RGB color tuple to use as the background for the image, default is white/grayish.

        The next set of options loads an existing image, either from a file,
        or from a list of lists containing RGB color tuples.
        If both are provided, the filepath will be used.

        | **option** | **description**
        | --- | --- 
        | *filepath | the string path of the image file to load, with extension
        | *data | a list of lists containing RGB color tuples

        Regardless of how the image is initialized, if a coordinate system instance
        is passed as an argument then all subsequent drawing coordinates will
        relate to that coordinate system (instead of pixels) and be automatically
        converted to pixel coordinates. After assigning a coordinate system to the
        image, the user can continue to draw to pixel coordinates by setting the
        ".coordmode" property to False.

        | **option** | **description**
        | --- | --- 
        | *crs | a coordinate system instance that defines the desired coordinate space of the image. 
        
        """
        #initiate image
        if filepath or data:
            self._loadimage(filepath, data)
        else:
            self.width = width
            self.height = height
            if not background:
                background = (200,200,200)
            horizline = [background for _ in xrange(width)]
            self.imagegrid = [list(horizline) for _ in xrange(height)]
        #set coordinate system
        self.crs = crs
        if crs:
            crs.bindimage(img=self)
            self.coordmode = True
        else:
            self.coordmode = False

    #TRANSFORM
##    def rotate(self):
##        """
##        not working yet
##        """
##        self.imagegrid = [list(each) for each in zip(*listoflists)]
##        #and update width/height
    def spheremapping(self, sphereradius, xoffset=0, yoffset=0, zdist=0):
        """
        Map the image onto a 3d globe-like sphere.
        Return a new transformed image instance.
        Note: still work in progress, not fully correct.

        | **option** | **description**
        | --- | --- 
        | sphereradius | the radius of the sphere to wrap the image around in pixel integers
        | xoffset/yoffset/zdist | don't use, not working properly

        """
        #what happens is that the entire output image is like a window looking out on a globe from a given dist and angle, and the original image is like a sheet of paper filling the window and then gets sucked and wrapped from its position directly onto the globe, actually the origpic does not necessarily originate from the window/camera pos
        #need to figure out viewopening and viewdirection
        #based on http://stackoverflow.com/questions/9604132/how-to-project-a-point-on-to-a-sphere
        #alternatively use: point = centervect + radius*(point-centervect)/(norm(point-centervect))

        #sphereboxwidth,sphereboxheight,sphereboxdepth = (sphereradius*2,sphereradius*2,sphereradius*2)
        midx,midy,midz = (sphereradius+xoffset,sphereradius+yoffset,sphereradius+zdist)
        def pixel2sphere(x,y,z):
            newx,newy,newz = (x-midx,y-midy,z-midz)
            newmagn = math.sqrt(newx*newx+newy*newy+newz*newz)
            try:
                scaledx,scaledy,scaledz = [(sphereradius/newmagn)*each for each in (newx,newy,newz)]
                newpoint = (scaledx+midx,scaledy+midy,scaledz+midz)
                return newpoint
            except ZeroDivisionError:
                pass
        newimg = Image().new(self.width,self.height)
        for y in xrange(len(self.imagegrid)):
            for x in xrange(len(self.imagegrid[0])):
                color = self._get(x,y)
                newpos = pixel2sphere(x,y,z=0)
                if newpos:
                    newx,newy,newz = newpos
                    newimg._put(int(newx),int(newy),color)
        return newimg
    def tilt(self, oldplane, newplane):
        """
        Performs a perspective transform, ie tilts it, and returns the transformed image.
        Note: it is not very obvious how to set the oldplane and newplane arguments
        in order to tilt an image the way one wants. Need to make the arguments more
        user-friendly and handle the oldplane/newplane behind the scenes.
        Some hints on how to do that at http://www.cs.utexas.edu/~fussell/courses/cs384g/lectures/lecture20-Z_buffer_pipeline.pdf

        | **option** | **description**
        | --- | --- 
        | oldplane | a list of four old xy coordinate pairs
        | newplane | four points in the new plane corresponding to the old points

        """
##        oldplane = (0,0),(self.width,0),(self.width,self.height),(0,self.height)
##        nw,ne,se,sw = oldplane
##        nnw,nne,nse,nsw = (nw[0]-topdepth,nw[1]+topdepth),(ne[0]+topdepth,ne[1]+topdepth),se,sw
##        newplane = [nnw,nne,nse,nsw]
        #first find the transform coefficients, thanks to http://stackoverflow.com/questions/14177744/how-does-perspective-transformation-work-in-pil
        pb,pa = oldplane,newplane
        grid = []
        for p1,p2 in zip(pa, pb):
            grid.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
            grid.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])
        import pydraw.advmatrix as mt
        A = mt.Matrix(grid)
        B = mt.Vec([xory for xy in pb for xory in xy])
        AT = A.tr()
        ATA = AT.mmul(A)
        gridinv = ATA.inverse()
        invAT = gridinv.mmul(AT)
        res = invAT.mmul(B)
        transcoeff = res.flatten()
        #then calculate new coords, thanks to http://math.stackexchange.com/questions/413860/is-perspective-transform-affine-if-it-is-why-its-impossible-to-perspective-a"
        k = 1
        a,b,c,d,e,f,g,h = transcoeff
        outimg = Image().new(self.width,self.height)
        for y in xrange(len(self.imagegrid)):
            for x in xrange(len(self.imagegrid[0])):
                color = self._get(x,y)
                newx = int(round((a*x+b*y+c)/float(g*x+h*y+k)))
                newy = int(round((d*x+e*y+f)/float(g*x+h*y+k)))
                try:
                    outimg._put(newx,newy,color)
                    #print x,y,newx,newy
                except IndexError:
                    #out of bounds
                    pass
        return outimg

    #DRAWING
    def get(self,x,y):
        """
        Get the color of pixel at specified xy position.
        Note: mostly used internally, but may sometimes be useful for end-user too.

        | **option** | **description**
        | --- | --- 
        | x/y | width/height position of the pixel to retrieve, with 0,0 being in topleft corner
        
        """
        if self.coordmode:
            x,y = self.crs.point2pixel(x,y)
        self._get(x,y,color)
        
    def _get(self,x,y):
        rgb = self.imagegrid[y][x]
        return rgb
    
    def put(self,x,y,color):
        """
        Set the color of a pixel at specified xy position.
        Floating point subpixel accuracy will draw antialiased point.
        Note: mostly used internally, but may sometimes be useful for end-user too.

        | **option** | **description**
        | --- | --- 
        | x/y | width/height position of the pixel to set, with 0,0 being in topleft corner
        | color | RGB color tuple to set to the pixel

        """
        if self.coordmode:
            x,y = self.crs.point2pixel(x,y)
        self._put(x,y,color)
        
    def _put(self, x,y,color):
        #normal pixel drawing
        if x < 0 or y < 0:
            #out of bounds
            return
        #if floating xy coords, make into semitransparent colors
        if isinstance(x, float) or isinstance(y, float):
            #calc values
            xint,yint = int(x), int(y)
            xfloat,yfloat = x-xint, y-yint
            if xfloat:
                x1,x2 = xint,xint+1
                x1transp,x2transp = 1-xfloat,xfloat
            if yfloat:
                y1,y2 = yint,yint+1
                y1transp,y2transp = 1-yfloat,yfloat
            #allow transp color
            if len(color)==3:
                r,g,b = color
                color = (r,g,b,255)
            #disperse pixels
            if xfloat and yfloat:
                newcolor = (color[0],color[1],color[2],color[3]*x1transp*y1transp)
                self._put(x1,y1,newcolor)
                newcolor = (color[0],color[1],color[2],color[3]*x1transp*y2transp)
                self._put(x1,y2,newcolor)
                newcolor = (color[0],color[1],color[2],color[3]*x2transp*y1transp)
                self._put(x2,y1,newcolor)
                newcolor = (color[0],color[1],color[2],color[3]*x2transp*y2transp)
                self._put(x2,y2,newcolor)
            elif xfloat:
                newcolor = (color[0],color[1],color[2],color[3]*x1transp)
                self._put(x1,yint,newcolor)
                newcolor = (color[0],color[1],color[2],color[3]*x2transp)
                self._put(x2,yint,newcolor)
            elif yfloat:
                newcolor = (color[0],color[1],color[2],color[3]*y1transp)
                self._put(xint,y1,newcolor)
                newcolor = (color[0],color[1],color[2],color[3]*y2transp)
                self._put(xint,y2,newcolor)
            return
        #or plot normal whole pixels
        elif len(color)==3:
            #solid color
            pass
        elif len(color)==4:
            #transparent color, blend with background
            t = color[3]/255.0
            try:
                p = self._get(int(x),int(y))
            except IndexError:
                return #pixel outside img boundary
            color = (int((p[0]*(1-t)) + color[0]*t), int((p[1]*(1-t)) + color[1]*t), int((p[2]*(1-t)) + color[2]*t))
        #finally draw it
        try: self.imagegrid[y][x] = color
        except IndexError:
            pass #pixel outside img boundary

    def pastedata(self, x, y, data, anchor="nw", transparency=0):
        """
        Pastes a list of lists of pixels onto the image at the specified position
        Note: for now, data has to be 3(rgb) tuples, not 4(rgba)
        and only nw anchor supported for now
        """
        if self.coordmode:
            x,y = self.crs.point2pixel(x,y)
        dataheight = len(data)
        datawidth = len(data[0])
        alpha = 255*transparency
        if "n" in anchor:
            if "w" in anchor:
                datay = 0
                for puty in xrange(y,y+dataheight):
                    datax = 0
                    for putx in xrange(x,x+datawidth):
                        dpixel = data[datax][datay]
                        r,g,b = dpixel
                        dpixel = (r,g,b,alpha)
                        self._put(putx,puty,dpixel)
                        datax += 1
                    datay += 1
            
    def drawline(self, x1, y1, x2, y2, fillcolor=(0,0,0), outlinecolor=None, fillsize=1, outlinewidth=1, capstyle="butt"): #, bendfactor=None, bendside=None, bendanchor=None):
        """
        Draws a single line.

        | **option** | **description**
        | --- | --- 
        | x1,y1,x2,y2 | start and end coordinates of the line, integers
        | *fillcolor | RGB color tuple to fill the body of the line with (currently not working)
        | *outlinecolor | RGB color tuple to fill the outline of the line with, default is no outline
        | *fillsize | the thickness of the main line, as pixel integers
        | *outlinewidth | the width of the outlines, as pixel integers
        
        """
##        maybe add these options in future
##        - bendfactor is strength/how far out the curve should extend from the line
##        - bendside is left or right side to bend
##        - bendanchor is the float ratio to offset the bend from its default anchor point at the center of the line.
        if self.coordmode:
            (x1,y1),(x2,y2) = self.crs.coords2pixels([(x1,y1),(x2,y2)])
        self._drawline(x1,y1,x2,y2,fillcolor=fillcolor,outlinecolor=outlinecolor,fillsize=fillsize,outlinewidth=outlinewidth,capstyle=capstyle)

    def _drawline(self, x1, y1, x2, y2, fillcolor=(0,0,0), outlinecolor=None, fillsize=1, outlinewidth=1, capstyle="butt"): #, bendfactor=None, bendside=None, bendanchor=None):
        #decide to draw single or thick line with outline
        if fillsize <= 1:
            #draw single line
            self._drawsimpleline(x1, y1, x2, y2, col=fillcolor, thick=fillsize)
        else:
            if outlinecolor or fillcolor:
                linepolygon = []
                #get orig params
                buff = fillsize/2.0
                xchange = x2-x1
                ychange = y2-y1
                try:
                    origslope = ychange/float(xchange)
                except ZeroDivisionError:
                    origslope = ychange
                angl = math.degrees(math.atan(origslope))
                perpangl_rad = math.radians(angl-90) #perpendicular angle in radians
                xbuff = buff * math.cos(perpangl_rad)
                ybuff = buff * math.sin(perpangl_rad)
                #leftline
                leftx1,leftx2 = (x1-xbuff,x2-xbuff)
                lefty1,lefty2 = (y1-ybuff,y2-ybuff)
                leftlinecoords = (leftx1,lefty1,leftx2,lefty2)
                #rightline
                rightx1,rightx2 = (x1+xbuff,x2+xbuff)
                righty1,righty2 = (y1+ybuff,y2+ybuff)
                rightlinecoords = (rightx2,righty2,rightx1,righty1)
                #finally draw the thick line as a polygon
                if capstyle == "butt":
                    linepolygon.extend(leftlinecoords)
                    linepolygon.extend(rightlinecoords)
                    def groupby2(iterable):
                        args = [iter(iterable)] * 2
                        return itertools.izip(*args)
                    linepolygon = list(groupby2(linepolygon))
                    self._drawpolygon(linepolygon, fillcolor=fillcolor, outlinecolor=outlinecolor, outlinewidth=outlinewidth)
                elif capstyle == "round":
                    #left side
                    linepolygon.extend(leftlinecoords)
                    #right round tip
                    ytipbuff = buff*2 * math.sin(math.radians(angl))
                    xtipbuff = buff*2 * math.cos(math.radians(angl))
                    xtipright = x2+xtipbuff
                    ytipright = y2+ytipbuff
                    roundcurve = _Bezier([leftlinecoords[-2:],(xtipright,ytipright),rightlinecoords[:2]], intervals=buff)
                    def flatten(iterable):
                        return itertools.chain.from_iterable(iterable)
                    linepolygon.extend(list(flatten(roundcurve.coords)))
                    #right side
                    linepolygon.extend(rightlinecoords)
                    #left round tip
                    xtipleft = x1-xtipbuff
                    ytipleft = y1-ytipbuff
                    roundcurve = _Bezier([rightlinecoords[-2:],(xtipleft,ytipleft),leftlinecoords[:2]], intervals=buff)
                    def flatten(iterable):
                        return itertools.chain.from_iterable(iterable)
                    linepolygon.extend(list(flatten(roundcurve.coords)))
                    #draw as polygon
                    def groupby2(iterable):
                        args = [iter(iterable)] * 2
                        return itertools.izip(*args)
                    linepolygon = list(groupby2(linepolygon))
                    self._drawpolygon(linepolygon, fillcolor=fillcolor, outlinecolor=outlinecolor, outlinewidth=outlinewidth)
                elif capstyle == "projecting":
                    #left side
                    ytipbuff = buff * math.sin(math.radians(angl))
                    xtipbuff = buff * math.cos(math.radians(angl))
                    linepolygon.extend([leftx2+xtipbuff, lefty2+ytipbuff, leftx1+xtipbuff, lefty1+ytipbuff])
                    #right side
                    linepolygon.extend([rightx1+xtipbuff, righty1+ytipbuff, rightx2+xtipbuff, righty2+ytipbuff])
                    #draw as polygon
                    def groupby2(iterable):
                        args = [iter(iterable)] * 2
                        return itertools.izip(*args)
                    linepolygon = list(groupby2(linepolygon))
                    self._drawpolygon(linepolygon, fillcolor=fillcolor, outlinecolor=outlinecolor, outlinewidth=outlinewidth)

    def drawmultiline(self, coords, fillcolor=(0,0,0), outlinecolor=None, fillsize=1, outlinewidth=1, joinstyle="miter"): #, bendfactor=None, bendside=None, bendanchor=None):
        """
        Draws multiple lines between a list of coordinates, useful for making them connect together.
        
        | **option** | **description**
        | --- | --- 
        | coords | list of coordinate point pairs to be connected by lines
        | **other | also accepts various color and size arguments, see the docstring for drawline.
        """
        if self.coordmode:
            coords = self.crs.coords2pixels(coords)
        self._drawmultiline(coords,fillcolor=fillcolor,outlinecolor=outlinecolor,fillsize=fillsize,outlinewidth=outlinewidth,joinstyle=joinstyle)

    def _drawmultiline(self, coords, fillcolor=(0,0,0), outlinecolor=None, fillsize=1, outlinewidth=1, joinstyle="miter"): #, bendfactor=None, bendside=None, bendanchor=None):
        if fillsize <= 1:
            for index in xrange(len(coords)-1):
                start,end = coords[index],coords[index+1]
                linecoords = list(start)
                linecoords.extend(list(end))
                self._drawline(*linecoords, fillcolor=fillcolor, outlinecolor=outlinecolor, fillsize=fillsize)
        elif not joinstyle:
            for index in xrange(len(coords)-1):
                start,end = coords[index],coords[index+1]
                linecoords = list(start)
                linecoords.extend(list(end))
                self._drawline(*linecoords, fillcolor=fillcolor, outlinecolor=outlinecolor, fillsize=fillsize)
        else:
            #lines are thick so they have to be joined
            def threewise(iterable):
                a,_ = itertools.tee(iterable)
                b,c = itertools.tee(_)
                next(b, None)
                next(c, None)
                next(c, None)
                return itertools.izip(a,b,c)
            linepolygon_left = []
            linepolygon_right = []
            buffersize = fillsize/2.0
            #the first line
            (x1,y1),(x2,y2),(x3,y3) = coords[:3]
            line1 = _Line(x1,y1,x2,y2)
            line2 = _Line(x2,y2,x3,y3)
            leftline,rightline = line1.getbuffersides(linebuffer=buffersize)
            leftlinestart = leftline.tolist()[0]
            rightlinestart = rightline.tolist()[0]
            linepolygon_left.append(leftlinestart)
            linepolygon_right.append(rightlinestart)
            #then all mid areas
            if joinstyle == "miter":
                #sharp join style
                for start,mid,end in threewise(coords):
                    (x1,y1),(x2,y2),(x3,y3) = start,mid,end
                    line1 = _Line(x1,y1,x2,y2)
                    line2 = _Line(x2,y2,x3,y3)
                    line1_left,line1_right = line1.getbuffersides(linebuffer=buffersize)
                    line2_left,line2_right = line2.getbuffersides(linebuffer=buffersize)
                    midleft = line1_left.intersect(line2_left, infinite=True)
                    midright = line1_right.intersect(line2_right, infinite=True)
                    if not midleft or not midright:
                        #PROB FLOAT ERROR,SO NO INTERSECTION FOUND
                        #CURRENTLY JUST SKIP DRAWING,BUT NEED BETTER HANDLING
                        return
                    #add coords
                    linepolygon = []
                    linepolygon.extend([linepolygon_left[-1],midleft])
                    linepolygon.extend([midright,linepolygon_right[-1]])
                    self._drawpolygon(linepolygon, fillcolor=fillcolor, outlinecolor=outlinecolor, outlinewidth=outlinewidth)
                    linepolygon_left.append(midleft)
                    linepolygon_right.append(midright)
            elif joinstyle == "round":
                #round
                for start,mid,end in threewise(coords):
                    (x1,y1),(x2,y2),(x3,y3) = start,mid,end
                    line1 = _Line(x1,y1,x2,y2)
                    line2 = _Line(x2,y2,x3,y3)
                    line1_left,line1_right = line1.getbuffersides(linebuffer=buffersize)
                    line2_left,line2_right = line2.getbuffersides(linebuffer=buffersize)
                    midleft = line1_left.intersect(line2_left, infinite=True)
                    midright = line1_right.intersect(line2_right, infinite=True)
                    if not midleft or not midright:
                        #PROB FLOAT ERROR,SO NO INTERSECTION FOUND
                        #CURRENTLY JUST SKIP DRAWING,BUT NEED BETTER HANDLING
                        return
                    #ARC approach
                    ##midx,midy = x2,y2
                    ##oppositeangle = line1.anglebetween_inv(line2)
                    ##bwangle = line1.anglebetween_abs(line2)
                    ##leftangl,rightangl = oppositeangle-bwangle,oppositeangle+bwangle
                    ##leftcurve = _Arc(midx,midy,radius=buffersize,startangle=leftangl,endangle=rightangl)
                    ##rightcurve = _Arc(midx-buffersize,midy-buffersize,radius=buffersize,startangle=leftangl,endangle=rightangl) #[(midx,midy)] #how do inner arc?

                    leftcurve = _Bezier([line1_left.tolist()[1],midleft,line2_left.tolist()[0]], intervals=20).coords
                    rightcurve = _Bezier([line1_right.tolist()[1],midright,line2_right.tolist()[0]], intervals=20).coords
                    #add coords
                    linepolygon = []
                    linepolygon.append(linepolygon_left[-1])
                    linepolygon.extend(leftcurve)
                    linepolygon.extend(list(reversed(rightcurve)))
                    linepolygon.append(linepolygon_right[-1])
                    self._drawpolygon(linepolygon, fillcolor=fillcolor, outlinecolor=outlinecolor, outlinewidth=outlinewidth)
                    linepolygon_left.extend(leftcurve)
                    linepolygon_right.extend(rightcurve)
            elif joinstyle == "bevel":
                #flattened
                pass
            #finally add last line coords
            (x1,y1),(x2,y2) = coords[-2:]
            lastline = _Line(x1,y1,x2,y2)
            leftline,rightline = lastline.getbuffersides(linebuffer=buffersize)
            leftlinestart = leftline.tolist()[1]
            rightlinestart = rightline.tolist()[1]
            
            linepolygon = []
            linepolygon.extend([linepolygon_left[-1],leftlinestart])
            linepolygon.extend([rightlinestart,linepolygon_right[-1]])
            self._drawpolygon(linepolygon, fillcolor=fillcolor, outlinecolor=outlinecolor, outlinewidth=outlinewidth)
            ##linepolygon_left.append(leftlinestart)
            ##linepolygon_right.append(rightlinestart)
            
            #draw as polygon
            ##linepolygon = []
            ##linepolygon.extend(linepolygon_left)
            ##linepolygon.extend(list(reversed(linepolygon_right)))
            #self._drawpolygon(linepolygon, fillcolor=fillcolor, outlinecolor=outlinecolor, outlinewidth=outlinewidth)
        
    def _drawsimpleline(self, x1, y1, x2, y2, col, thick=1):
        """
        Backend being used internally, holds the basic line algorithm, including antialiasing.
        taken and modified from a Stackoverflow post...
        appears to be a bit jagged, not as smooth as preferred, so
        need to look into how to improve/fix it.
        Note: the "col" argument is the color tuple of the line.
        """
        def plot(x, y, c, col,steep):
            if steep:
                x,y = y,x
            #not entirely satisfied with quality yet, does some weird stuff when overlapping
            #p = self._get(int(x),int(y))
            newtransp = c*255*thick #int(col[3]*c)
            newcolor = (col[0], col[1], col[2], newtransp)
            #newcolor = (int((p[0]*(1-c)) + col[0]*c), int((p[1]*(1-c)) + col[1]*c), int((p[2]*(1-c)) + col[2]*c))
            self._put(int(round(x)),int(round(y)),newcolor)

        def iround(x):
            return ipart(x + 0.5)

        def ipart(x):
            return math.floor(x)

        def fpart(x):
            return x-math.floor(x)

        def rfpart(x):
            return 1 - fpart(x)
        
        dx = x2 - x1
        dy = y2 - y1

        steep = abs(dx) < abs(dy)
        if steep:
            x1,y1=y1,x1
            x2,y2=y2,x2
            dx,dy=dy,dx
        if x2 < x1:
            x1,x2=x2,x1
            y1,y2=y2,y1
        try:
            gradient = float(dy) / float(dx)
        except ZeroDivisionError:
            #pure vertical line, so just draw it without antialias
            newtransp = 255*thick #int(col[3]*c)
            newcolor = (col[0], col[1], col[2], newtransp)
            for y in xrange(y1,y2+1):
                self._put(x1,y,newcolor)
            return

        #handle first endpoint
        xend = round(x1)
        yend = y1 + gradient * (xend - x1)
        xgap = rfpart(x1 + 0.5)
        xpxl1 = xend    #this will be used in the main loop
        ypxl1 = ipart(yend)
        plot(xpxl1, ypxl1, rfpart(yend)*xgap, col, steep)
        plot(xpxl1, ypxl1 + 1, fpart(yend)*xgap, col, steep)
        intery = yend + gradient # first y-intersection for the main loop

        #handle second endpoint
        xend = round(x2)
        yend = y2 + gradient * (xend - x2)
        xgap = fpart(x2 + 0.5)
        xpxl2 = xend    # this will be used in the main loop
        ypxl2 = ipart(yend)
        plot(xpxl2, ypxl2, rfpart(yend)*xgap, col, steep)
        plot(xpxl2, ypxl2 + 1, fpart(yend)*xgap, col, steep)

        #main loop
        for x in xrange(int(xpxl1 + 1), int(xpxl2 )):
            ybase = math.floor(intery)
            ydeci = intery-ybase
            plot(x, ybase, 1-ydeci, col, steep)
            plot(x, ybase+1, ydeci, col, steep)
            intery += gradient

    def drawbezier(self, xypoints, fillcolor=(0,0,0), outlinecolor=None, fillsize=1, intervals=100):
        """
        Draws a bezier curve given a list of coordinate control point pairs.
        Mostly taken directly from a stackoverflow post...
        
        | **option** | **description**
        | --- | --- 
        | xypoints | list of coordinate point pairs, at least 3. The first and last points are the endpoints, and the ones in between are control points used to inform the curvature.
        | **other | also accepts various color and size arguments, see the docstring for drawline.
        | *intervals | how finegrained/often the curve should be bent, default is 100, ie curves every one percent of the line.
        
        """
        if self.coordmode:
            xypoints = self.crs.coords2pixels(xypoints)
        self._drawbezier(xypoints,fillcolor=fillcolor,outlinecolor=outlinecolor,fillsize=fillsize,intervals=intervals)

    def _drawbezier(self, xypoints, fillcolor=(0,0,0), outlinecolor=None, fillsize=1, intervals=100):
        curve = _Bezier(xypoints, intervals)
        self._drawmultiline(curve.coords, fillcolor=fillcolor, outlinecolor=outlinecolor, fillsize=fillsize)

    def drawarc(self, x, y, radius, opening=None, facing=None, startangle=None, endangle=None, fillcolor=(0,0,0), outlinecolor=None, outlinewidth=1):
        """
        Experimental, but seems to work correctly
        Optional to use opening and facings args, or start and end angle args
        """
        if self.coordmode:
            x,y = self.crs.point2pixel(x,y)
        self._drawarc(x,y,radius,opening,facing,startangle,endangle,fillcolor=fillcolor,outlinecolor=outlinecolor,outlinewidth=outlinewidth)
        
    def _drawarc(self, x, y, radius, opening=None, facing=None, startangle=None, endangle=None, fillcolor=(0,0,0), outlinecolor=None, outlinewidth=1):        
        arcpolygon = [(x,y)]
        arcpolygon.extend(_Arc(x, y, radius, opening=opening, facing=facing, startangle=startangle, endangle=endangle))
        self._drawpolygon(arcpolygon, fillcolor=fillcolor, outlinecolor=outlinecolor, outlinewidth=outlinewidth)

    def drawcircle(self, x, y, fillsize, fillcolor=(0,0,0), outlinecolor=None, outlinewidth=1): #, flatten=None, flatangle=None):
        """
        Draws a circle at specified centerpoint.
        
        | **option** | **description**
        | --- | --- 
        | x/y | the integer x/y position to be the midpoint of the circle.
        | fillsize | required to specify the fillsize of the circle, as pixel integers
        | **other | also accepts various color and size arguments, see the docstring for drawline.
        
        """
        #later on add ability to make that circle an ellipse with these args:
        #flatten=...
        #flatangle=...
        if self.coordmode:
            x,y = self.crs.point2pixel(x,y)
        self._drawcircle(x,y,fillsize, fillcolor=fillcolor, outlinecolor=outlinecolor, outlinewidth=outlinewidth)

    def _drawcircle(self, x, y, fillsize, fillcolor=(0,0,0), outlinecolor=None, outlinewidth=1): #, flatten=None, flatangle=None):
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
            cornerpoints = [(x+relx,y+rely) for relx,rely in cornerpoints]
            #self._drawbezier(cornerpoints, fillsize=outlinewidth, fillcolor=outlinecolor, outlinecolor=None, intervals=int(fillsize*20))
            circlepolygon.extend(_Bezier(cornerpoints, intervals=int(fillsize*3)).coords)
            oldindex += 3
        #then draw and fill as polygon
        self._drawpolygon(circlepolygon, fillcolor=fillcolor, outlinecolor=outlinecolor, outlinewidth=outlinewidth)

    def drawsquare(self, x,y,fillsize, fillcolor=(0,0,0), outlinecolor=None, outlinewidth=1, outlinejoinstyle=None):
        if self.coordmode:
            x,y = self.crs.point2pixel(x,y)
        self._drawsquare(x,y,fillsize, fillcolor=fillcolor, outlinecolor=outlinecolor, outlinewidth=outlinewidth, outlinejoinstyle=outlinejoinstyle)

    def _drawsquare(self, x,y,fillsize, fillcolor=(0,0,0), outlinecolor=None, outlinewidth=1, outlinejoinstyle=None):
        halfsize = fillsize/2.0
        rectanglecoords = [(x-halfsize,y-halfsize),(x+halfsize,y-halfsize),(x+halfsize,y+halfsize),(x-halfsize,y+halfsize),(x-halfsize,y-halfsize)]
        self._drawpolygon(coords=rectanglecoords, fillcolor=fillcolor, outlinecolor=outlinecolor, outlinewidth=outlinewidth, outlinejoinstyle=outlinejoinstyle)
  
    def drawpolygon(self, coords, holes=[], fillcolor=(0,0,0), outlinecolor=None, outlinewidth=1, outlinejoinstyle="miter"):
        """
        Draws a polygon based on input coordinates.
        Note: as with other primitives, fillcolor does not work properly.
        
        | **option** | **description**
        | --- | --- 
        | coords | list of coordinate point pairs that make up the polygon. Automatically detects whether to enclose the polygon.
        | *holes | optional list of one or more polygons that represent holes in the polygon, each hole being a list of coordinate point pairs. Hole polygon coordinates are automatically closed if they aren't already. 
        | **other | also accepts various color and size arguments, see the docstring for drawline.
        
        """
        if self.coordmode:
            coords = self.crs.coords2pixels(coords)
            if holes:
                holes = [self.crs.coords2pixels(hole) for hole in holes]
        self._drawpolygon(coords,holes=holes,fillcolor=fillcolor, outlinecolor=outlinecolor, outlinewidth=outlinewidth, outlinejoinstyle=outlinejoinstyle)

    def _drawpolygon(self, coords, holes=[], fillcolor=(0,0,0), outlinecolor=None, outlinewidth=1, outlinejoinstyle="miter"):
        #maybe autocomplete polygon and holes
        if coords[-1] != coords[0]:
            coords = list(coords)
            coords.append(coords[0])
        for hole in holes:
            if hole[-1] != hole[0]:
                hole = list(hole)
                hole.append(hole[0])
        #first fill insides of polygon
        if fillcolor:
            def pairwise(iterable):
                a,b = itertools.tee(iterable)
                next(b, None)
                return itertools.izip(a,b)
            def flatten(iterable):
                return itertools.chain.from_iterable(iterable)
            def groupby2(iterable):
                args = [iter(iterable)] * 2
                return itertools.izip(*args)
            #main
            def coordsandholes():
                #generator for exterior coords and holes
                for edge in pairwise(coords):
                    yield edge
                if holes:
                    for hole in holes:
                        for edge in pairwise(hole):
                            yield edge
            ysortededges = [ list(flatten(sorted(eachedge, key=operator.itemgetter(1)))) for eachedge in coordsandholes() ]
            ysortededges = list(sorted(ysortededges, key=operator.itemgetter(1)))
            edgeindex = 0
            curedge = ysortededges[edgeindex]
            checkedges = []
            #get bbox
            xs, ys = zip(*coords)
            bbox = [min(xs), min(ys), max(xs), max(ys)]
            #begin
            xmin,ymin,xmax,ymax = bbox
            ymin,ymax = map(int, map(round, (ymin,ymax)))
            for y in xrange(ymin,ymax+1):
                fillxs = []
                fillxs_half = []
                #collect relevant edges
                "first from previous old ones"
                tempcollect = [tempedge for tempedge in checkedges if tempedge[3] > y]
                "then from new ones"
                while curedge[1] <= y and edgeindex < len(ysortededges):
                    tempcollect.append(curedge)
                    edgeindex += 1
                    try:
                        curedge = ysortededges[edgeindex]
                    except IndexError:
                        break   #just to make higher
                if tempcollect:
                    checkedges = tempcollect
                #find intersect
                scanline = _Line(xmin,y,xmax,y)
                for edge in checkedges:
                    edge = _Line(*edge)
                    intersection = scanline.intersect(edge)
                    if intersection:
                        ix,iy = intersection
                        fillxs.append(ix)
                #scan line and fill
                fillxs = sorted(fillxs)
                if fillxs:
                    for fillmin,fillmax in groupby2(fillxs):
                        fillmin,fillmax = map(int,map(round,(fillmin,fillmax)))
                        for x in xrange(fillmin,fillmax+1):
                            self._put(x,y,fillcolor)
            #cheating to draw antialiased edges as lines
            self._drawmultiline(coords, fillcolor=fillcolor, outlinecolor=None, fillsize=1)
            for hole in holes:
                self._drawmultiline(hole, fillcolor=fillcolor, outlinecolor=None, fillsize=1)
        #then draw outline
        if outlinecolor:
            coords.append(coords[1])
            self._drawmultiline(coords, fillcolor=outlinecolor, fillsize=outlinewidth, outlinecolor=None, joinstyle=outlinejoinstyle)
            for hole in holes:
                hole.append(hole[1])
                self._drawmultiline(hole, fillcolor=outlinecolor, fillsize=outlinewidth, outlinecolor=None, joinstyle=outlinejoinstyle)

    def drawrectangle(self, bbox, fillcolor=(0,0,0), outlinecolor=None, outlinewidth=1, outlinejoinstyle=None):
        if self.coordmode:
            x1,y1,x2,y2 = bbox
            (x1,y1),(x2,y2) = self.crs.coords2pixels([(x1,y1),(x2,y2)])
            bbox = [x1,y1,x2,y2]
        self._drawrectangle(bbox, fillcolor=fillcolor, outlinecolor=outlinecolor, outlinewidth=outlinewidth, outlinejoinstyle=outlinejoinstyle)
    def _drawrectangle(self, bbox, fillcolor=(0,0,0), outlinecolor=None, outlinewidth=1, outlinejoinstyle=None):
        x1,y1,x2,y2 = bbox
        rectanglecoords = [(x1,y1),(x1,y2),(x2,y2),(x2,y1),(x1,y1)]
        self._drawpolygon(coords=rectanglecoords, fillcolor=fillcolor, outlinecolor=outlinecolor, outlinewidth=outlinewidth, outlinejoinstyle=outlinejoinstyle)

    def drawarrow(self, x1, y1, x2, y2, fillcolor=(0,0,0), outlinecolor=None, fillsize=1, outlinewidth=1, capstyle="butt"): #, bendfactor=None, bendside=None, bendanchor=None):
        pass

    def drawgridticks(self, every_x=10, every_y=10):
        #set some params
        if self.width < self.height:
            tickindent = self.width*0.02
        else:
            tickindent = self.height*0.02
        tickthick = tickindent*0.10
        #loop thru tickmarks
        if every_x:
            if self.crs:
                if self.crs.xleft > self.crs.xright:
                    every_x *= -1
                    tickindent *= -1
                topy = self.crs.ytop
                xpos = self.crs.xleft
                while xpos < self.crs.xright:
                    tickpixelcoords = self.crs.coords2pixels([(xpos,topy),(xpos,topy)])
                    (x1,y1),(x2,y2) = tickpixelcoords
                    y2 += tickindent
                    self._drawline(x1,y1,x2,y2,fillcolor=(0,0,0),fillsize=tickthick)
                    xpos += every_x
            else:
                topy = 0
                xpos = 0
                while xpos < self.width:
                    self._drawline(xpos,topy,xpos,topy+tickindent,fillcolor=(0,0,0),fillsize=tickthick)
                    xpos += every_x
        if every_y:
            if self.crs:
                if self.crs.ytop > self.crs.ybottom:
                    every_y *= -1
                    tickindent *= -1
                leftx = self.crs.xleft
                ypos = self.crs.ytop
                while ypos < self.crs.ybottom:
                    tickpixelcoords = self.crs.coords2pixels([(leftx,ypos),(leftx,ypos)])
                    (x1,y1),(x2,y2) = tickpixelcoords
                    x2 += tickindent+1
                    self._drawline(x1,y1,x2,y2,fillcolor=(0,0,0),fillsize=tickthick)
                    ypos += every_y
            else:
                leftx = 0
                ypos = 0
                while ypos < self.yheight:
                    self._drawline(ypos,bottomy,xpos+tickindent+1,bottomy,fillcolor=(0,0,0),fillsize=tickthick)
                    ypos += self.yheight

    def drawgeojson(self, geojobj, fillcolor=(0,0,0), outlinecolor=None, fillsize=1, outlinewidth=1, joinstyle="miter", outlinejoinstyle="miter", capstyle="butt"): #, bendfactor=None, bendside=None, bendanchor=None):
        """
        Takes any object that has the __geo_interface__ attribute
        """
        geojson = geojobj.__geo_interface__
        geotype = geojson["type"]
        coords = geojson["coordinates"]
        if geotype == "Point":
            if self.coordmode:
                coords = self.crs.point2pixel(*coords)
            self._drawcircle(*coords, fillsize=fillsize, outlinecolor=outlinecolor, fillcolor=fillcolor, outlinewidth=outlinewidth)
        elif geotype == "MultiPoint":
            if self.coordmode:
                coords = self.crs.coords2pixels(coords)
            for point in coords:
                self._drawcircle(*point, fillsize=fillsize, outlinecolor=outlinecolor, fillcolor=fillcolor, outlinewidth=outlinewidth)
        elif geotype == "LineString":
            if self.coordmode:
                coords = self.crs.coords2pixels(coords)
            self._drawmultiline(coords, fillcolor=fillcolor, outlinecolor=outlinecolor, fillsize=fillsize, outlinewidth=outlinewidth, joinstyle=joinstyle)
        elif geotype == "MultiLineString":
            if self.coordmode:
                coords = (self.crs.coords2pixels(eachmulti) for eachmulti in coords)
            for eachmulti in coords:
                self._drawmultiline(eachmulti, fillcolor=fillcolor, outlinecolor=outlinecolor, fillsize=fillsize, outlinewidth=outlinewidth, joinstyle=joinstyle)
        elif geotype == "Polygon":
            if self.coordmode:
                coords = [self.crs.coords2pixels(polyorhole) for polyorhole in coords]
            exterior = coords[0]
            interiors = []
            if len(coords) > 1:
                interiors.extend(coords[1:])
            self._drawpolygon(exterior, holes=interiors, fillcolor=fillcolor, outlinecolor=outlinecolor, outlinewidth=outlinewidth, outlinejoinstyle=outlinejoinstyle)
        elif geotype == "MultiPolygon":
            if self.coordmode:
                coords = ([self.crs.coords2pixels(polyorhole) for polyorhole in eachmulti] for eachmulti in coords)
            for eachmulti in coords:
                exterior = eachmulti[0]
                interiors = []
                if len(eachmulti) > 1:
                    interiors.extend(eachmulti[1:])
                self._drawpolygon(exterior, holes=interiors, fillcolor=fillcolor, outlinecolor=outlinecolor, outlinewidth=outlinewidth, outlinejoinstyle=outlinejoinstyle)
    
    def floodfill(self,x,y,fillcolor,fuzzythresh=1.0):
        """
        Fill a large area of similarly colored neighboring pixels to the color at the origin point.
        Adapted from http://inventwithpython.com/blog/2011/08/11/recursion-explained-with-the-flood-fill-algorithm-and-zombies-and-cats/comment-page-1/
        Note: needs to be optimized, bc now checks all neighbours multiple times regardless of whether checked before bc has no memory.
        Also, lowering the fuzzythreshhold is not a good idea as it is incredibly slow.

        | **option** | **description**
        | --- | --- 
        | x/t | the xy coordinate integers of where to begin the floodfill.
        | fillcolor | the new RGB color tuple to replace the old colors with
        
        """
        if self.coordmode:
            x,y = self.crs.point2pixel(x,y)
        self._floodfill(x,y,fillcolor,fuzzythresh=fuzzythresh)

    def _floodfill(self,x,y,fillcolor,fuzzythresh=1.0):
        #test and fill all neighbouring cells
        fillcolor = list(fillcolor)
        colortofollow = self._get(x,y)
        sqrt = math.sqrt
        def notexactcolor(x,y):
            if self._get(x,y) != colortofollow:
                return True
        def notfuzzycolor(x,y):
            """based on W3 principles, http://www.had2know.com/technology/color-contrast-calculator-web-design.html
            but doesnt really work yet, super slow, likely due to the if bigger than test operation"""
            #r,g,b = self._get(x,y)
            #checkbrightness = ( 299*r + 587*g + 114*b )/1000
            #r,g,b = colortofollow
            #comparebrightness = ( 299*r + 587*g + 114*b )/1000
            #brightnessdiff = float(str((checkbrightness-comparebrightness)/255.0).replace("-",""))#sqrt(((checkbrightness-comparebrightness)/255.0)**2)
            main = self._get(x,y)
            compare = colortofollow
            colordiff = sum([spec[0]-spec[1] for spec in zip(main,compare)])/255.0
            if colordiff > fuzzythresh:
                return True
        if fuzzythresh == 1.0: reachedboundary = notexactcolor
        else: reachedboundary = notfuzzycolor
        theStack = [ (x, y) ]
        while len(theStack) > 0:
            x, y = theStack.pop()
            try:
                if reachedboundary(x,y):
                    continue
            except IndexError:
                continue
            self._put(x,y,fillcolor)
            theStack.append( (x + 1, y) )  # right
            theStack.append( (x - 1, y) )  # left
            theStack.append( (x, y + 1) )  # down
            theStack.append( (x, y - 1) )  # up

    #AFTERMATH
    def view(self):
        """
        Pops up a Tkinter window in which to view the image
        """
        window = tk.Tk()
        canvas = tk.Canvas(window, width=self.width, height=self.height)
        canvas.create_text((self.width/2, self.height/2), text="error\nviewing\nimage")
        self.tkimg = self._tkimage()
        canvas.create_image((self.width/2, self.height/2), image=self.tkimg, state="normal")
        canvas.pack()
        tk.mainloop()
    def updateview(self):
        """
        Updates the image in the Tkinter window to include recent changes to the image
        """
        self.tkimg = self._tkimage()
    def save(self, savepath):
        """
        Saves the image to the given filepath.

        | **option** | **description**
        | --- | --- 
        | filepath | the string path location to save the image. Extension must be given and can only be ".gif".
        
        """
        if savepath.endswith(".png"):
            imagerows = [list(itertools.chain.from_iterable(row)) for row in self.imagegrid]
            png.from_array(imagerows, mode="RGB").save(savepath)
        elif savepath.endswith(".gif"):
            tempwin = tk.Tk() #only so dont get "too early to create image" error
            tkimg = self._tkimage()
            tkimg.write(savepath, "gif")
            tempwin.destroy()
        
    #INTERNAL USE ONLY
    def _loadimage(self, filepath=None, data=None):
        if filepath:
            if filepath.endswith(".png"):
                #PNG
                reader = png.Reader(filename=filepath)
                width,height,pixels,metadata = reader.read()
                if metadata["alpha"]:
                    colorlength = 4
                else:
                    colorlength = 3
                data = []
                for pxlrow in pixels:
                    row = []
                    index = 0
                    while index < width*colorlength:
                        color = [pxlrow[index+spectrum] for spectrum in xrange(colorlength)]
                        color = color[:3] #this bc currently no support for alpha image values
                        row.append(color)
                        index += colorlength
                    data.append(row)
                self.width,self.height = width,height
                self.imagegrid = data
            elif filepath.endswith(".gif"):
                #GIF
                tempwin = tk.Tk()
                tempimg = tk.PhotoImage(file=filepath)
                data = [[tuple([int(spec) for spec in tempimg._get(x,y).split()])
                        for x in xrange(tempimg.width())]
                        for y in xrange(tempimg.height())]
                self.width = len(data[0])
                self.height = len(data)
                self.imagegrid = data
        elif data:
            self.width = len(data[0])
            self.height = len(data)
            self.imagegrid = data
    def _tkimage(self):
        """
        Converts the image pixel matrix to a Tkinter Photoimage to allow viewing/saving.
        For internal use only.
        """
        tkimg = tk.PhotoImage(width=self.width, height=self.height)
        imgstring = " ".join(["{"+" ".join(["#%02x%02x%02x" %tuple(rgb) for rgb in horizline])+"}" for horizline in self.imagegrid])
        tkimg.put(imgstring)
        return tkimg

if __name__ == "__main__":
    import pydraw.tester as tester
    tester.testall()
    
