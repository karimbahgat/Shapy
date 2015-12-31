# Buffy Polygon buffer algo idea

Depending on ring direction, buffer only the outer side of each polygon segment and allow various line and cap joins. 
Should work for line buffer as well. 

Then decompose the polygon into non self intersecting polygon parts by starting a new part at each self intersection.
The part may then return to its starting intersection at which point we close it. Or it may lead to other self 
intersections before it closes off. In any case we keep track of the vertexes along with the index position of the 
starting intersection. Whenever a vertex is encountered that is also the same as the last registered vertex of a 
previously unclosed part, we add the following vertexes to that part, possibly closing it off. Once all parts have 
been collected with a unique index position and vertex list, we create the parts collection by popping them out
of the original polygon at their index positions, which means the original polygon will be cleaned of self intersections, 
and we do this in reverse order to preserve index positions. 

Once we have the collection of parts, we can determine which to keep by getting one of their inside points and finding 
their winding numbers inside the original polygon. 

Alternatively, use the Greiner Horman algo to get the cumulative union of all the parts until all parts have been unioned. 
