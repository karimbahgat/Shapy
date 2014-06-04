# Pydraw submodule
# Coordinate system handler for pixel conversion

REDUCEVECTORS = False

class CoordinateSystem(object):
    def __init__(self, bbox):
        """
        A helper class that the user can use to define a coordinate system
        and convert coordinates to pixel space.

        - bbox: the bounding box of the coordinate system as a four-tuple (xleft,ytop,xright,ybottom).
        """
        bbox = [float(each) for each in bbox]
        self.xleft,self.ytop,self.xright,self.ybottom = bbox
        x2x = (self.xleft,self.xright)
        y2y = (self.ybottom,self.ytop)
        self.xwidth = max(x2x)-min(x2x)
        self.yheight = max(y2y)-min(y2y)
    def getinfo(self):
        """
        Returns a dictionary with info about the current settings
        of the coordinate system.
        """
        try:
            outdims = (self.imgwidth,self.imgheight)
        except:
            outdims = ("no output image has been assigned")
        crsdict = dict([("output dimensions",outdims),
                        ("coord bbox",(self.xleft,self.ytop,self.xright,self.ybottom)),
                        ("coord dimensions",(self.xwidth,self.yheight)) ])
        return crsdict
    def bindimage(self, img):
        """
        - img: the image instance whose dimensions the coordinate system should use when converting to pixels.
        """
        self.imgwidth = float(img.width)
        self.imgheight = float(img.height)
        self.scalex = self.imgwidth / (self.xright - self.xleft)
        self.scaley = -self.imgheight / (self.ytop - self.ybottom)
    def point2pixel(self, inx, iny):
        """
        Converts one xy tuple point to a pixel coordinate point
        according to the coordinate system and pixel image defined
        in the class
        """
        newx = self.scalex * (inx - self.xleft)
        newy = self.imgheight + self.scaley * (iny - self.ybottom)
        newpoint = (newx,newy)
        return newpoint
    def coords2pixels(self, incoords):
        """
        Converts a single list of coordinate pairs to pixel coordinate pairs
        according to the coordinate system and pixel image defined in the class
        """
        outcoords = []
        previous = None
        for point in incoords:
            inx, iny = point
            newx = self.scalex * (inx - self.xleft)
            newy = self.imgheight + self.scaley * (iny - self.ybottom)
            if REDUCEVECTORS:
                newpoint = (int(newx),int(newy))
                if newpoint != previous:
                    outcoords.extend(newpoint)
                    previous = newpoint
            else:
                newpoint = (newx,newy)
                outcoords.append(newpoint)
        return outcoords


        
