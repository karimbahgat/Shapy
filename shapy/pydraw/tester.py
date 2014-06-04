#Tester for the PyDraw module

if __name__ == "__main__":
    
    import pydraw

    crs = pydraw.CoordinateSystem([0,0,100,100])
    img = pydraw.Image(880,440, background=(222,0,0), crs=crs)
    #img = Image(filepath="C:/Users/BIGKIMO/Desktop/hmm.png")
    #print crs.getinfo()

    #SINGLE PIXEL TEST
    img.put(94.7,94.7,(0,0,222))
    #img.put(95.7,98,(0,0,222))
    #img.put(98,95.7,(0,0,222))

    #GREEN POLYGONS WITH OUTLINE
    #img.drawpolygon(coords=[(30,30),(90,10),(90,90),(10,90),(30,30)], fillcolor=(0,222,0), outlinecolor=(0,0,0), outlinewidth=12, outlinejoinstyle="round")
    #img.drawpolygon(coords=[(80,20),(50,15),(20,44),(90,50),(50,90),(10,50),(30,20),(50,10)], fillcolor=(0,222,0), outlinecolor=(0,0,0), outlinewidth=5, outlinejoinstyle="round")

    #POLYGON WITH HOLES
    img.drawpolygon(coords=[(30,30),(90,10),(90,90),(10,90),(30,30)], holes=[[(51,41),(77,51),(77,65),(51,77),(51,41)] , [(43,63),(49,63),(49,69),(43,69),(43,63)]], fillcolor=(222,222,0), outlinecolor=(0,0,0), outlinewidth=12, outlinejoinstyle="round")

    #MISC MULTILINE TEST
    #img.drawmultiline(coords=[(90,20),(80,20),(50,15),(20,44),(90,50),(50,90),(10,50),(30,20),(50,10)], fillcolor=(0,0,0), fillsize=8, outlinecolor=None, joinstyle="miter")
    #img.drawmultiline(coords=[(10,50),(50,50),(50,90)], fillcolor=(0,0,0), fillsize=8, outlinecolor=None, joinstyle="round")
    #img.drawmultiline(coords=[(10,50),(50,50),(60,90)], fillcolor=(0,111,0), fillsize=12, outlinecolor=None, joinstyle="round")

    #SINGLE LINE TEST
    #img.drawline(22,11,88,77,fillcolor=(222,0,0),fillsize=8, capstyle="round")
    #img.drawline(22,66,88,77,fillcolor=(222,0,0,166),fillsize=11, capstyle="round")
    ##img.drawline(44,33,55,80,fillcolor=(222,0,0),fillsize=0.5)

    #VARIOUS OTHER SHAPES
    #img.drawbezier([(11,11),(90,40),(90,90)])
    #img.drawpolygon([(90,50),(90-5,50-5),(90+5,50+5),(90-5,50+5),(90,50)], fillcolor=(222,0,0))
    #img.drawcircle(50,50,fillsize=8, fillcolor=(222,222,0), outlinecolor=(0,0,222), outlinewidth=1)
    img.drawarc(44,62,radius=30,opening=90,facing=360, outlinecolor=(0,0,222), outlinewidth=1)
    img.drawrectangle([42,42,88,55], fillcolor=(0,0,222), outlinecolor=(211,111,0), outlinewidth=4, outlinejoinstyle="round")
    img.drawsquare(80,80,fillsize=13, fillcolor=(111,0,222), outlinecolor=(211,0,0), outlinewidth=1, outlinejoinstyle="miter")

    #TEST DATA PASTE
    #img = Image().load("C:/Users/BIGKIMO/Desktop/puremap.png")
    #data = Image().load("C:/Users/BIGKIMO/Desktop/hmm.png").imagegrid
    #img.pastedata(444,222,data,transparency=0.5)
    
    img.view()
    img.save("C:/Users/BIGKIMO/Desktop/hmm.png")

    #TEST COORDINATE SYSTEM TO PIXELS
##    crs = pydraw.CoordinateSystem([-180,90,180,-90])
##    img = pydraw.Image(600,600, background=(222,0,0), crs=crs)
##    print crs.getinfo()
##    poly = [(-170,-80),(-170,80),(170,80),(170,-80)]
##    holes = [[(-100,-50),(-100,50),(100,10),(100,-50)]]
##    img.drawpolygon(poly, holes=holes)
##    img.view()
