# Pydraw submodule
# Coordinate system handler for pixel conversion

REDUCEVECTORS = False

class CoordinateSystem(object):
    def __init__(self, bbox):
        """
        A helper class that the user can use to define a coordinate system
        and convert coordinates to pixel space

        - bbox: the bounding box of the coordinate system as a four-tuple (xleft,ytop,xright,ybottom).
        """
        bbox = [float(each) for each in bbox]
        self.xleft,self.ytop,self.xright,self.ybottom = bbox
        x2x = (self.xleft,self.xright)
        y2y = (self.ybottom,self.ytop)
        self.xwidth = max(x2x)-min(x2x)
        self.yheight = max(y2y)-min(y2y)
        #offset coordinates so they are all positive values
        xmin = min(x2x)
        ymin = min(y2y)
        if xmin < 0: self.xoffset = -xmin
        else: self.xoffset = 0
        if ymin < 0: self.yoffset = -ymin
        else: self.yoffset = 0
    def getinfo(self):
        """
        Returns a dictionary with info about the current settings
        of the coordinate system.
        """
        try:
            outdims = (self.imgwidth,self.imgheight)
        except:
            outdims = ("no output image has been assigned")
        cssdict = dict([("output dimensions",outdims),
                        ("coord bbox",(self.xleft,self.ytop,self.xright,self.ybottom)),
                        ("coord dimensions",(self.xwidth,self.yheight)),
                        ("coord offset",(self.xoffset,self.yoffset)) ])
        return cssdict
    def bindimage(self, img):
        """
        - img: the image instance whose dimensions the coordinate system should use when converting to pixels.
        """
        self.imgwidth = float(img.width)
        self.imgheight = float(img.height)
        #set fracdiv value to speed up later calculations
        self._fracdivx = self.imgwidth
        self._fracdivy = self.imgheight
        #next consider the direction of each axis
        if self.xleft < self.xright:
            self._revx = 0
            self._fracdivx *= -1
        else:
            self._revx = self.imgwidth
        if self.ybottom < self.ytop:
            self._revy = self.imgheight
        else:
            self._revy = 0
            self._fracdivy *= -1

    def point2pixel(self, inx, iny):
        """
        Converts one xy tuple point to a pixel coordinate point
        according to the coordinate system and pixel image defined
        in the class
        """
        #(inx/xwidth)*imgwidth
        newx = self._revx-(self.xoffset+inx)/self.xwidth*self._fracdivx
        newy = self._revy-(self.yoffset+iny)/self.yheight*self._fracdivy
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
            newx = self._revx-(self.xoffset+inx)/self.xwidth*self._fracdivx
            newy = self._revy-(self.yoffset+iny)/self.yheight*self._fracdivy
            if REDUCEVECTORS:
                newpoint = (int(newx),int(newy))
                if newpoint != previous:
                    outcoords.extend(newpoint)
                    previous = newpoint
            else:
                newpoint = (newx,newy)
                outcoords.append(newpoint)
        return outcoords


        
