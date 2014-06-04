"""
PyDraw
v0.1

## Introduction
PyDraw is a pure-Python drawing library.
The reason for making this library was to experiment with new drawing features to
merge with the pure-Python "Pymaging" library. But since Pymaging still hasn't 
been released in a working-version aimed for end-users, I'm just releasing this as a separate 
package until it can hopefully be incorporated into the Pymaging library later on.
PyDraw might also be interesting in itself since it incredibly lightweight,
straightforward to use, and provides not only basic drawing but also some
advanced features. One of the joys of it being pure-Python is that it becomes
fairly easy and way more accessible for even novice Python programmers to
experiment with and extend its drawing functionality and routines. 
Main features include:

- uses similar drawing commands to those used in PIL and Aggdraw
- the user can draw on a new empty image, open an existing one, and save the image to file
- draws various graphical primitives:
  - lines
  - circles
  - multilines
  - polygons
  - bezier curves
- drawings uses antialising (smooth sub-pixel precision)
- offers exact and fuzzy floodfill coloring of large areas (however, fuzzy floodfill is currently way too slow to be used)
- can also transform images
  - perspective transform, ie 3d tilting of an image
  - sphere/stereographic transform, ie 3d globe effect (partially working, partially not)

The main backdraws currently are:

- only support for reading/writing gif images, and if you use too many colors the gif image won't save
- while transparent gif images can be read, transparency will not be saved (becomes black)
- not as fast as C-based libraries (on average 10x slower)
- not a stable version yet, so several lacking features and errors (see Status below)

## Basic Usage
A typical example of how to use it would be:

```
import pydraw
img = pydraw.Image().new(width=500,height=500)
img.drawbezier([(22,22),(88,88),(188,22),(333,88)], fillcolor=(222,0,0))
img.drawcircle(333,111,fillsize=55,outlinecolor=(222,222,0))
img.drawline(0,250,499,250, fillcolor=(222,222,222))
img.floodfill(444,444,fillcolor=(0,222,0))
img.floodfill(222,222,fillcolor=(0,0,222))
img.view()
```

## Requires:
No dependencies; everything is written with the standard builtin Python library.
This is mainly thanks to the basic read-write capabilities of the Tkinter PhotoImage class.
Also tested to work on both Python 2.x and 3.x. 

## Status:
Main features are working okay so should be able to be used by end-users.
However, still in its most basic alpha-version, which means there may be many bugs. 
But most importantly it is lacking a few crucial drawing features,
which will be added in the future, such as:

- None of the primitives are being filled correctly (so drawing is limited to outlines)
- Thick multilines and thick polygon outlines appear choppy, need to add smooth join rules
- Lines need to be capped at their ends, with option for rounded caps
- Need more basic image transforms, such as rotate and flip
- Support for saving transparency, and drawing partially transparent colors
- Support for various color formats besides RGB (such as hex or colornames)
- And most importantly, more image formats

## License:
This code is free to share, use, reuse, and modify according to the MIT license, see license.txt

## Credits:
Karim Bahgat (2014)
Several Stackoverflow posts have been helpful for adding certain features,
and in some cases the code has been taken directly from the posts.
In other cases help and code has been found on websites.
In all such cases, the appropriate credit is given in the code.

## Contributors
I welcome any efforts to contribute code, particularly for:

- optimizing for speed, particularly the floodfill algorithm and its fuzzy variant
- adding/improving/correcting any rendering algorithms
- improve the quality of antialiasing, is currently still somewhat choppy
- fixing why image transform results in weird ripples and holes in the images
- adding new features (see Status above)

"""

import core, coordinate_transformer
from core import *
from coordinate_transformer import *



