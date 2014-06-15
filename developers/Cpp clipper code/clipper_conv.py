'''******************************************************************************
*                                                                              *
* Author    :  Angus Johnson                                                   *
* Version   :  6.1.5                                                           *
* Date      :  27 May 2014                                                     *
* Website   :  http:#www.angusj.com                                           *
* Copyright :  Angus Johnson 2010-2014                                         *
*                                                                              *
* License:                                                                     *
* Use, & distribution is subject to Boost Software License Ver 1. *
* http:#www.boost.org/LICENSE_1_0.txt                                         *
*                                                                              *
* Attributions:                                                                *
* The code in self library is an extension of Bala Vatti's clipping algorithm: *
* "A generic solution to polygon clipping"                                     *
* Communications of the ACM, 35, 7 (July 1992) pp 56-63.             *
* http:#portal.acm.org/citation.cfm?id=129906                                 *
*                                                                              *
* Computer graphics and geometric modeling: implementation and algorithms      *
* By Max K. Agoston                                                            *
* Springer; 1 edition (January 4, 2005)                                        *
* http:#books.google.com/books?q=vatti+clipping+agoston                       *
*                                                                              *
* See also:                                                                    *
* "Polygon Offsetting by Computing Winding Numbers"                            *
* Paper no. DETC2005-85513 pp. 565-575                                         *
* ASME 2005 International Design Engineering Technical Conferences             *
* and Computers and Information in Engineering Conference (IDETC/CIE2005)      *
* September 24-28, 2005 , Beach, California, *
* http:#www.me.berkeley.edu/~mcmains/pubs/DAC05OffsetPolygon.pdf              *
*                                                                              *
******************************************************************************'''

'''******************************************************************************
*                                                                              *
* This is a translation of the Delphi Clipper library and the naming style     *
* used has retained a Delphi flavour.                                          *
*                                                                              *
******************************************************************************'''

#include "clipper.hpp"
#include <cmath>
#include <vector>
#include <algorithm>
#include <stdexcept>
#include <cstring>
#include <cstdlib>
#include <ostream>
#include <functional>

namespace ClipperLib
static pi = 3.141592653589793238
static two_pi = pi *2
static def_arc_tolerance = 0.25

enum Direction { dRightToLeft, dLeftToRight

static Unassigned = -1;  #edge not currently 'owning' a solution
static Skip = -2;        #edge that would otherwise close a path

#define HORIZONTAL (-1.0E+40)
#define TOLERANCE (1.0e-20)
#define NEAR_ZERO(val) (((val) > -TOLERANCE) and ((val) < TOLERANCE))

struct TEdge  IntPoint Bot
  IntPoint Curr
  IntPoint Top
  IntPoint Delta
  double Dx
  PolyType PolyTyp
  EdgeSide Side
  int WindDelta; #1 or -1 depending on winding direction
  int WindCnt
  int WindCnt2; #winding count of the opposite polytype
  int OutIdx
  TEdge *Next
  TEdge *Prev
  TEdge *NextInLML
  TEdge *NextInAEL
  TEdge *PrevInAEL
  TEdge *NextInSEL
  TEdge *PrevInSEL


struct IntersectNode  TEdge          *Edge1
  TEdge          *Edge2
  IntPoint        Pt


struct LocalMinima  cInt          Y
  TEdge        *LeftBound
  TEdge        *RightBound
  LocalMinima  *Next


struct OutPt

struct OutRec  int       Idx
  bool      IsHole
  bool      IsOpen
  OutRec   *FirstLeft;  #see comments in clipper.pas
  PolyNode *PolyNd
  OutPt    *Pts
  OutPt    *BottomPt


struct OutPt  int       Idx
  IntPoint  Pt
  OutPt    *Next
  OutPt    *Prev


struct Join  OutPt    *OutPt1
  OutPt    *OutPt2
  IntPoint  OffPt


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

inline cInt Round(double val)
  if ((val < 0)) return static_cast<cInt>(val - 0.5); 
  else return static_cast<cInt>(val + 0.5)

#------------------------------------------------------------------------------

inline cInt Abs(cInt val)
  return val < 0 ? -val : val


#------------------------------------------------------------------------------
# PolyTree methods ...
#------------------------------------------------------------------------------

def Clear(self):
    for (i = 0; i < AllNodes.size(); ++i)
      delete AllNodes[i]
    AllNodes.resize(0); 
    Childs.resize(0)

#------------------------------------------------------------------------------

def GetFirst(self):
  if not Childs.empty():
      return Childs[0]
  else:
      return 0

#------------------------------------------------------------------------------

def Total(self):
  return (int)AllNodes.size()


#------------------------------------------------------------------------------
# PolyNode methods ...
#------------------------------------------------------------------------------

PolyNode.PolyNode(): Childs(), Parent(0), Index(0), m_IsOpen(False)

#------------------------------------------------------------------------------

def ChildCount(self):
  return (int)Childs.size()

#------------------------------------------------------------------------------

def AddChild(self, child):
  cnt = (unsigned)Childs.size()
  Childs.push_back(&child)
  child.Parent = self
  child.Index = cnt

#------------------------------------------------------------------------------

def GetNext(self):
{ 
  if (not Childs.empty()) 
      return Childs[0]; 
  else:
      return GetNextSiblingUp();    
}  
#------------------------------------------------------------------------------

def GetNextSiblingUp(self):
{ 
  if not Parent) #protects against PolyTree.GetNextSiblingUp(:
      return 0
  elif Index == Parent.Childs.size() - 1:
      return Parent.GetNextSiblingUp()
  else:
      return Parent.Childs[Index + 1]
}  
#------------------------------------------------------------------------------

def IsHole(self):
{ 
  result = True
  node = Parent
  while (node)
      result = not result
      node = node.Parent

  return result
}  
#------------------------------------------------------------------------------

def IsOpen(self):
{ 
  return m_IsOpen
}  
#------------------------------------------------------------------------------

#ifndef use_int32

#------------------------------------------------------------------------------
# Int128 class (enables safe math on signed 64bit integers)
# eg Int128 val1((long64)9223372036854775807); #ie 2^63 -1
#    Int128 val2((long64)9223372036854775807)
#    val3 = val1 * val2
#    val3.AsString => "85070591730234615847396907784232501249" (8.5e+37)
#------------------------------------------------------------------------------

class Int128
  public:
    ulong64 lo
    long64 hi

    Int128(_lo = 0)
      lo = (ulong64)_lo;   
      if (_lo < 0)  hi = -1; hi = 0; 



    Int128( Int128 &val): lo(val.lo), hi(val.hi){

    Int128( long64& _hi, _lo): lo(_lo), hi(_hi){
    
    operator = ( long64 &val)
      lo = (ulong64)val
      if (val < 0) hi = -1; hi = 0
      return *self


    bool operator == ( Int128 &val)
      {return (hi == val.hi and lo == val.lo);

    bool operator != ( Int128 &val)
      { return not (*self == val);

    bool operator > ( Int128 &val)
      if hi != val.hi:
        return hi > val.hi
      else:
        return lo > val.lo


    bool operator < ( Int128 &val)
      if hi != val.hi:
        return hi < val.hi
      else:
        return lo < val.lo


    bool operator >= ( Int128 &val)
      { return not (*self < val);

    bool operator <= ( Int128 &val)
      { return not (*self > val);

    Int128& operator += ( Int128 &rhs)
      hi += rhs.hi
      lo += rhs.lo
      if (lo < rhs.lo) hi++
      return *self


    Int128 operator + ( Int128 &rhs)
      Int128 result(*self)
      result+= rhs
      return result


    Int128& operator -= ( Int128 &rhs)
      *self += -rhs
      return *self


    Int128 operator - ( Int128 &rhs)
      Int128 result(*self)
      result -= rhs
      return result


    Int128 operator-()  #unary negation
      if lo == 0:
        return Int128(-hi,0)
      else:
        return Int128(~hi,~lo +1)



#------------------------------------------------------------------------------

Int128 Int128Mul (long64 lhs, rhs)
  negate = (lhs < 0) != (rhs < 0)

  if (lhs < 0) lhs = -lhs
  int1Hi = ulong64(lhs) >> 32
  int1Lo = ulong64(lhs & 0xFFFFFFFF)

  if (rhs < 0) rhs = -rhs
  int2Hi = ulong64(rhs) >> 32
  int2Lo = ulong64(rhs & 0xFFFFFFFF)

  #nb: see comments in clipper.pas
  a = int1Hi * int2Hi
  b = int1Lo * int2Lo
  c = int1Hi * int2Lo + int1Lo * int2Hi

  Int128 tmp
  tmp.hi = long64(a + (c >> 32))
  tmp.lo = long64(c << 32)
  tmp.lo += long64(b)
  if (tmp.lo < b) tmp.hi++
  if (negate) tmp = -tmp
  return tmp

#endif

#------------------------------------------------------------------------------
# Miscellaneous global functions
#------------------------------------------------------------------------------

def Swap(self, val1, val2):
  tmp = val1
  val1 = val2
  val2 = tmp

#------------------------------------------------------------------------------
def Orientation(self, &poly):
    return Area(poly) >= 0

#------------------------------------------------------------------------------

def Area(self, &poly):
  size = (int)poly.size()
  if (size < 3) return 0

  a = 0
  for (i = 0, j = size -1; i < size; ++i)
    a += ((double)poly[j].X + poly[i].X) * ((double)poly[j].Y - poly[i].Y)
    j = i

  return -a * 0.5

#------------------------------------------------------------------------------

def Area(self, &outRec):
  OutPt *op = outRec.Pts
  if (not op) return 0
  a = 0
  do    a +=  (double)(op.Prev.Pt.X + op.Pt.X) * (double)(op.Prev.Pt.Y - op.Pt.Y)
    op = op.Next
  } while (op != outRec.Pts)
  return a * 0.5

#------------------------------------------------------------------------------

def PointIsVertex(self, &Pt, *pp):
  OutPt *pp2 = pp
  do
    if (pp2.Pt == Pt) return True
    pp2 = pp2.Next

  while (pp2 != pp)
  return False

#------------------------------------------------------------------------------

int PointInPolygon ( IntPoint &pt, &path)
  #returns 0 if False, +1 if True, -1 if pt ON polygon boundary
  #See "The Point in Polygon Problem for Arbitrary Polygons" by Hormann & Agathos
  #http:#citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.88.5498&rep=rep1&type=pdf
  result = 0
  cnt = path.size()
  if (cnt < 3) return 0
  ip = path[0]
  for(i = 1; i <= cnt; ++i)
    ipNext = (i == cnt ? path[0] : path[i])
    if ipNext.Y == pt.Y:
        if ((ipNext.X == pt.X) or (ip.Y == pt.Y and 
          ((ipNext.X > pt.X) == (ip.X < pt.X)))) return -1

    if (ip.Y < pt.Y) != (ipNext.Y < pt.Y):
      if ip.X >= pt.X:
        if (ipNext.X > pt.X) result = 1 - result
        else:
          d = (double)(ip.X - pt.X) * (ipNext.Y - pt.Y) - 
            (double)(ipNext.X - pt.X) * (ip.Y - pt.Y)
          if (not d) return -1
          if ((d > 0) == (ipNext.Y > ip.Y)) result = 1 - result

      } else:
        if ipNext.X > pt.X:
          d = (double)(ip.X - pt.X) * (ipNext.Y - pt.Y) - 
            (double)(ipNext.X - pt.X) * (ip.Y - pt.Y)
          if (not d) return -1
          if ((d > 0) == (ipNext.Y > ip.Y)) result = 1 - result



    ip = ipNext
  } 
  return result

#------------------------------------------------------------------------------

int PointInPolygon ( IntPoint &pt, *op)
  #returns 0 if False, +1 if True, -1 if pt ON polygon boundary
  result = 0
  startOp = op
  for(;;)
    if op.Next.Pt.Y == pt.Y:
        if ((op.Next.Pt.X == pt.X) or (op.Pt.Y == pt.Y and 
          ((op.Next.Pt.X > pt.X) == (op.Pt.X < pt.X)))) return -1

    if (op.Pt.Y < pt.Y) != (op.Next.Pt.Y < pt.Y):
      if op.Pt.X >= pt.X:
        if (op.Next.Pt.X > pt.X) result = 1 - result
        else:
          d = (double)(op.Pt.X - pt.X) * (op.Next.Pt.Y - pt.Y) - 
            (double)(op.Next.Pt.X - pt.X) * (op.Pt.Y - pt.Y)
          if (not d) return -1
          if ((d > 0) == (op.Next.Pt.Y > op.Pt.Y)) result = 1 - result

      } else:
        if op.Next.Pt.X > pt.X:
          d = (double)(op.Pt.X - pt.X) * (op.Next.Pt.Y - pt.Y) - 
            (double)(op.Next.Pt.X - pt.X) * (op.Pt.Y - pt.Y)
          if (not d) return -1
          if ((d > 0) == (op.Next.Pt.Y > op.Pt.Y)) result = 1 - result


    } 
    op = op.Next
    if (startOp == op) break
  } 
  return result

#------------------------------------------------------------------------------

def Poly2ContainsPoly1(self, *OutPt1, *OutPt2):
  op = OutPt1
  do
    res = PointInPolygon(op.Pt, OutPt2)
    if (res >= 0) return res != 0
    op = op.Next; 

  while (op != OutPt1)
  return True; 

#----------------------------------------------------------------------

def SlopesEqual(self, &e1, &e2, UseFullInt64Range):
#ifndef use_int32
  if UseFullInt64Range:
    return Int128Mul(e1.Delta.Y, e2.Delta.X) == Int128Mul(e1.Delta.X, e2.Delta.Y)
  else:
#endif
    return e1.Delta.Y * e2.Delta.X == e1.Delta.X * e2.Delta.Y

#------------------------------------------------------------------------------

bool SlopesEqual( IntPoint pt1, pt2,
   IntPoint pt3, UseFullInt64Range)
#ifndef use_int32
  if UseFullInt64Range:
    return Int128Mul(pt1.Y-pt2.Y, pt2.X-pt3.X) == Int128Mul(pt1.X-pt2.X, pt2.Y-pt3.Y)
  else:
#endif
    return (pt1.Y-pt2.Y)*(pt2.X-pt3.X) == (pt1.X-pt2.X)*(pt2.Y-pt3.Y)

#------------------------------------------------------------------------------

bool SlopesEqual( IntPoint pt1, pt2,
   IntPoint pt3, pt4, UseFullInt64Range)
#ifndef use_int32
  if UseFullInt64Range:
    return Int128Mul(pt1.Y-pt2.Y, pt3.X-pt4.X) == Int128Mul(pt1.X-pt2.X, pt3.Y-pt4.Y)
  else:
#endif
    return (pt1.Y-pt2.Y)*(pt3.X-pt4.X) == (pt1.X-pt2.X)*(pt3.Y-pt4.Y)

#------------------------------------------------------------------------------

inline bool IsHorizontal(TEdge &e)
  return e.Delta.Y == 0

#------------------------------------------------------------------------------

inline double GetDx( IntPoint pt1, pt2)
  return (pt1.Y == pt2.Y) ?
    HORIZONTAL : (double)(pt2.X - pt1.X) / (pt2.Y - pt1.Y)

#---------------------------------------------------------------------------

inline void SetDx(TEdge &e)
  e.Delta.X = (e.Top.X - e.Bot.X)
  e.Delta.Y = (e.Top.Y - e.Bot.Y)

  if (e.Delta.Y == 0) e.Dx = HORIZONTAL
  else e.Dx = (double)(e.Delta.X) / e.Delta.Y

#---------------------------------------------------------------------------

inline void SwapSides(TEdge &Edge1, &Edge2)
  Side =  Edge1.Side
  Edge1.Side = Edge2.Side
  Edge2.Side = Side

#------------------------------------------------------------------------------

inline void SwapPolyIndexes(TEdge &Edge1, &Edge2)
  OutIdx =  Edge1.OutIdx
  Edge1.OutIdx = Edge2.OutIdx
  Edge2.OutIdx = OutIdx

#------------------------------------------------------------------------------

inline cInt TopX(TEdge &edge, currentY)
  return ( currentY == edge.Top.Y ) ?
    edge.Top.X : edge.Bot.X + Round(edge.Dx *(currentY - edge.Bot.Y))

#------------------------------------------------------------------------------

def IntersectPoint(self, &Edge1, &Edge2, &ip):
#ifdef use_xyz  
  ip.Z = 0
#endif

  double b1, b2
  if Edge1.Dx == Edge2.Dx:
    ip.Y = Edge1.Curr.Y
    ip.X = TopX(Edge1, ip.Y)
    return

  elif Edge1.Delta.X == 0:
    ip.X = Edge1.Bot.X
    if IsHorizontal(Edge2):
      ip.Y = Edge2.Bot.Y
    else:
      b2 = Edge2.Bot.Y - (Edge2.Bot.X / Edge2.Dx)
      ip.Y = Round(ip.X / Edge2.Dx + b2)


  elif Edge2.Delta.X == 0:
    ip.X = Edge2.Bot.X
    if IsHorizontal(Edge1):
      ip.Y = Edge1.Bot.Y
    else:
      b1 = Edge1.Bot.Y - (Edge1.Bot.X / Edge1.Dx)
      ip.Y = Round(ip.X / Edge1.Dx + b1)

  } 
  else:
    b1 = Edge1.Bot.X - Edge1.Bot.Y * Edge1.Dx
    b2 = Edge2.Bot.X - Edge2.Bot.Y * Edge2.Dx
    q = (b2-b1) / (Edge1.Dx - Edge2.Dx)
    ip.Y = Round(q)
    if std.fabs(Edge1.Dx) < std.fabs(Edge2.Dx):
      ip.X = Round(Edge1.Dx * q + b1)
    else:
      ip.X = Round(Edge2.Dx * q + b2)


  if (ip.Y < Edge1.Top.Y or ip.Y < Edge2.Top.Y) 
    if Edge1.Top.Y > Edge2.Top.Y:
      ip.Y = Edge1.Top.Y
    else:
      ip.Y = Edge2.Top.Y
    if std.fabs(Edge1.Dx) < std.fabs(Edge2.Dx):
      ip.X = TopX(Edge1, ip.Y)
    else:
      ip.X = TopX(Edge2, ip.Y)
  } 
  #finally, don't allow 'ip' to be BELOW curr.Y (ie bottom of scanbeam) ...
  if ip.Y > Edge1.Curr.Y:
    ip.Y = Edge1.Curr.Y
    #use the more vertical edge to derive X ...
    if std.fabs(Edge1.Dx) > std.fabs(Edge2.Dx):
      ip.X = TopX(Edge2, ip.Y); else:
      ip.X = TopX(Edge1, ip.Y)


#------------------------------------------------------------------------------

def ReversePolyPtLinks(self, *pp):
  if (not pp) return
  OutPt *pp1, *pp2
  pp1 = pp
  do  pp2 = pp1.Next
  pp1.Next = pp1.Prev
  pp1.Prev = pp2
  pp1 = pp2
  } while( pp1 != pp )

#------------------------------------------------------------------------------

def DisposeOutPts(self, pp):
  if (pp == 0) return
    pp.Prev.Next = 0
  while( pp )
    OutPt *tmpPp = pp
    pp = pp.Next
    delete tmpPp


#------------------------------------------------------------------------------

inline void InitEdge(TEdge* e, eNext, ePrev, Pt)
  std.memset(e, 0, sizeof(TEdge))
  e.Next = eNext
  e.Prev = ePrev
  e.Curr = Pt
  e.OutIdx = Unassigned

#------------------------------------------------------------------------------

def InitEdge2(self, e, Pt):
  if e.Curr.Y >= e.Next.Curr.Y:
    e.Bot = e.Curr
    e.Top = e.Next.Curr
  } else:
    e.Top = e.Curr
    e.Bot = e.Next.Curr

  SetDx(e)
  e.PolyTyp = Pt

#------------------------------------------------------------------------------

def RemoveEdge(self, e):
  #removes e from double_linked_list (but without removing from memory)
  e.Prev.Next = e.Next
  e.Next.Prev = e.Prev
  result = e.Next
  e.Prev = 0; #flag as removed (see ClipperBase.Clear)
  return result

#------------------------------------------------------------------------------

inline void ReverseHorizontal(TEdge &e)
  #swap horizontal edges' Top and Bottom x's so they follow the natural
  #progression of the bounds - ie so their xbots will align with the
  #adjoining lower edge. [Helpful in the ProcessHorizontal() method.]
  Swap(e.Top.X, e.Bot.X)
#ifdef use_xyz  
  Swap(e.Top.Z, e.Bot.Z)
#endif

#------------------------------------------------------------------------------

def SwapPoints(self, &pt1, &pt2):
  tmp = pt1
  pt1 = pt2
  pt2 = tmp

#------------------------------------------------------------------------------

bool GetOverlapSegment(IntPoint pt1a, pt1b, pt2a,
  IntPoint pt2b, &pt1, &pt2)
  #precondition: segments are Collinear.
  if Abs(pt1a.X - pt1b.X) > Abs(pt1a.Y - pt1b.Y):
    if pt1a.X > pt1b.X) SwapPoints(pt1a, pt1b:
    if pt2a.X > pt2b.X) SwapPoints(pt2a, pt2b:
    if (pt1a.X > pt2a.X) pt1 = pt1a; pt1 = pt2a
    if (pt1b.X < pt2b.X) pt2 = pt1b; pt2 = pt2b
    return pt1.X < pt2.X
  } else:
    if pt1a.Y < pt1b.Y) SwapPoints(pt1a, pt1b:
    if pt2a.Y < pt2b.Y) SwapPoints(pt2a, pt2b:
    if (pt1a.Y < pt2a.Y) pt1 = pt1a; pt1 = pt2a
    if (pt1b.Y > pt2b.Y) pt2 = pt1b; pt2 = pt2b
    return pt1.Y > pt2.Y


#------------------------------------------------------------------------------

def FirstIsBottomPt(self, btmPt1, btmPt2):
  OutPt *p = btmPt1.Prev
  while ((p.Pt == btmPt1.Pt) and (p != btmPt1)) p = p.Prev
  dx1p = std.fabs(GetDx(btmPt1.Pt, p.Pt))
  p = btmPt1.Next
  while ((p.Pt == btmPt1.Pt) and (p != btmPt1)) p = p.Next
  dx1n = std.fabs(GetDx(btmPt1.Pt, p.Pt))

  p = btmPt2.Prev
  while ((p.Pt == btmPt2.Pt) and (p != btmPt2)) p = p.Prev
  dx2p = std.fabs(GetDx(btmPt2.Pt, p.Pt))
  p = btmPt2.Next
  while ((p.Pt == btmPt2.Pt) and (p != btmPt2)) p = p.Next
  dx2n = std.fabs(GetDx(btmPt2.Pt, p.Pt))
  return (dx1p >= dx2p and dx1p >= dx2n) or (dx1n >= dx2p and dx1n >= dx2n)

#------------------------------------------------------------------------------

def GetBottomPt(self, *pp):
  dups = 0
  p = pp.Next
  while (p != pp)
    if p.Pt.Y > pp.Pt.Y:
      pp = p
      dups = 0

    elif p.Pt.Y == pp.Pt.Y and p.Pt.X <= pp.Pt.X:
      if p.Pt.X < pp.Pt.X:
        dups = 0
        pp = p
      } else:
        if (p.Next != pp and p.Prev != pp) dups = p


    p = p.Next

  if dups:
    #there appears to be at least 2 vertices at BottomPt so ...
    while (dups != p)
      if (not FirstIsBottomPt(p, dups)) pp = dups
      dups = dups.Next
      while (dups.Pt != pp.Pt) dups = dups.Next


  return pp

#------------------------------------------------------------------------------

bool Pt2IsBetweenPt1AndPt3( IntPoint pt1,
   IntPoint pt2, pt3)
  if (pt1 == pt3) or (pt1 == pt2) or (pt3 == pt2):
    return False
  elif pt1.X != pt3.X:
    return (pt2.X > pt1.X) == (pt2.X < pt3.X)
  else:
    return (pt2.Y > pt1.Y) == (pt2.Y < pt3.Y)

#------------------------------------------------------------------------------

def HorzSegmentsOverlap(self, seg1a, seg1b, seg2a, seg2b):
  if seg1a > seg1b) Swap(seg1a, seg1b:
  if seg2a > seg2b) Swap(seg2a, seg2b:
  return (seg1a < seg2b) and (seg2a < seg1b)


#------------------------------------------------------------------------------
# ClipperBase class methods ...
#------------------------------------------------------------------------------

ClipperBase.ClipperBase() #constructor
  m_MinimaList = 0
  m_CurrentLM = 0
  m_UseFullRange = False

#------------------------------------------------------------------------------

ClipperBase.~ClipperBase() #destructor
  Clear()

#------------------------------------------------------------------------------

def RangeTest(self, Pt, useFullRange):
  if useFullRange:
    if (Pt.X > hiRange or Pt.Y > hiRange or -Pt.X > hiRange or -Pt.Y > hiRange) 
      throw "Coordinate outside allowed range"

  elif (Pt.X > loRangeor Pt.Y > loRange or -Pt.X > loRange or -Pt.Y > loRange) 
    useFullRange = True
    RangeTest(Pt, useFullRange)


#------------------------------------------------------------------------------

def FindNextLocMin(self, E):
  for (;;)
    while (E.Bot != E.Prev.Bot or E.Curr == E.Top) E = E.Next
    if (not IsHorizontal(*E) and not IsHorizontal(*E.Prev)) break
    while (IsHorizontal(*E.Prev)) E = E.Prev
    E2 = E
    while (IsHorizontal(*E)) E = E.Next
    if (E.Top.Y == E.Prev.Bot.Y) continue; #ie just an intermediate horz.
    if (E2.Prev.Bot.X < E.Bot.X) E = E2
    break

  return E

#------------------------------------------------------------------------------

def ProcessBound(self, E, NextIsForward):
  TEdge *Result = E
  TEdge *Horz = 0

  if E.OutIdx == Skip:
    #if edges still remain in the current bound beyond the skip edge then
    #create another LocMin and call ProcessBound once more
    if NextIsForward:
      while (E.Top.Y == E.Next.Bot.Y) E = E.Next
      #don't include top horizontals when parsing a bound a second time,
      #they will be contained in the opposite bound ...
      while (E != Result and IsHorizontal(*E)) E = E.Prev

    else:
      while (E.Top.Y == E.Prev.Bot.Y) E = E.Prev
      while (E != Result and IsHorizontal(*E)) E = E.Next


    if E == Result:
      if (NextIsForward) Result = E.Next
      Result = E.Prev

    else:
      #there are more edges in the bound beyond result starting with E
      if NextIsForward:
        E = Result.Next
      else:
        E = Result.Prev
      locMin = LocalMinima
      locMin.Next = 0
      locMin.Y = E.Bot.Y
      locMin.LeftBound = 0
      locMin.RightBound = E
      E.WindDelta = 0
      Result = ProcessBound(E, NextIsForward)
      InsertLocalMinima(locMin)

    return Result


  TEdge *EStart

  if IsHorizontal(*E):
    #We need to be careful with open paths because self may not be a
    #True local minima (ie E may be following a skip edge).
    #Also, horz. edges may start heading left before going right.
    if (NextIsForward) 
      EStart = E.Prev
    else:
      EStart = E.Next
    if (IsHorizontal(*EStart)) #ie an adjoining horizontal skip edge
      if (EStart.Bot.X != E.Bot.X and EStart.Top.X != E.Bot.X) 
        ReverseHorizontal(*E)

    elif (EStart.Bot.X != E.Bot.X) 
      ReverseHorizontal(*E)

  
  EStart = E
  if NextIsForward:
    while (Result.Top.Y == Result.Next.Bot.Y and Result.Next.OutIdx != Skip)
      Result = Result.Next
    if IsHorizontal(*Result) and Result.Next.OutIdx != Skip:
      #nb: at the top of a bound, are added to the bound
      #only when the preceding edge attaches to the horizontal's left vertex
      #unless a Skip edge is encountered when that becomes the top divide
      Horz = Result
      while (IsHorizontal(*Horz.Prev)) Horz = Horz.Prev
      if (Horz.Prev.Top.X == Result.Next.Top.X) 
        if (not NextIsForward) Result = Horz.Prev

      elif (Horz.Prev.Top.X > Result.Next.Top.X) Result = Horz.Prev

    while (E != Result) 
      E.NextInLML = E.Next
      if (IsHorizontal(*E) and E != EStart and
        E.Bot.X != E.Prev.Top.X) ReverseHorizontal(*E)
      E = E.Next

    if (IsHorizontal(*E) and E != EStart and E.Bot.X != E.Prev.Top.X) 
      ReverseHorizontal(*E)
    Result = Result.Next; #move to the edge just beyond current bound
  } else:
    while (Result.Top.Y == Result.Prev.Bot.Y and Result.Prev.OutIdx != Skip) 
      Result = Result.Prev
    if IsHorizontal(*Result) and Result.Prev.OutIdx != Skip:
      Horz = Result
      while (IsHorizontal(*Horz.Next)) Horz = Horz.Next
      if (Horz.Next.Top.X == Result.Prev.Top.X) 
        if (not NextIsForward) Result = Horz.Next

      elif (Horz.Next.Top.X > Result.Prev.Top.X) Result = Horz.Next


    while (E != Result)
      E.NextInLML = E.Prev
      if (IsHorizontal(*E) and E != EStart and E.Bot.X != E.Next.Top.X) 
        ReverseHorizontal(*E)
      E = E.Prev

    if (IsHorizontal(*E) and E != EStart and E.Bot.X != E.Next.Top.X) 
      ReverseHorizontal(*E)
    Result = Result.Prev; #move to the edge just beyond current bound


  return Result

#------------------------------------------------------------------------------

def AddPath(self, &pg, PolyTyp, Closed):
#ifdef use_lines
  if not Closed and PolyTyp == ptClip:
    throw clipperException("AddPath: Open paths must be subject.")
#else:
  if not Closed:
    throw clipperException("AddPath: Open paths have been disabled.")
#endif

  highI = (int)pg.size() -1
  if (Closed) while (highI > 0 and (pg[highI] == pg[0])) --highI
  while (highI > 0 and (pg[highI] == pg[highI -1])) --highI
  if ((Closed and highI < 2) or (not Closed and highI < 1)) return False

  #create a edge array ...
  TEdge *edges = TEdge [highI +1]

  IsFlat = True
  #1. Basic (first) edge initialization ...
  try
    edges[1].Curr = pg[1]
    RangeTest(pg[0], m_UseFullRange)
    RangeTest(pg[highI], m_UseFullRange)
    InitEdge(&edges[0], &edges[1], &edges[highI], pg[0])
    InitEdge(&edges[highI], &edges[0], &edges[highI-1], pg[highI])
    for (i = highI - 1; i >= 1; --i)
      RangeTest(pg[i], m_UseFullRange)
      InitEdge(&edges[i], &edges[i+1], &edges[i-1], pg[i])


  catch(...)
    delete [] edges
    throw; #range test fails

  TEdge *eStart = &edges[0]

  #2. Remove duplicate vertices, and (when closed) collinear edges ...
  TEdge *E = eStart, *eLoopStop = eStart
  for (;;)
    #nb: allows matching start and end points when not Closed ...
    if E.Curr == E.Next.Curr and (Closed or E.Next != eStart):
      if (E == E.Next) break
      if (E == eStart) eStart = E.Next
      E = RemoveEdge(E)
      eLoopStop = E
      continue

    if (E.Prev == E.Next) 
      break; #only two vertices
    elif (Closed and
      SlopesEqual(E.Prev.Curr, E.Curr, E.Next.Curr, m_UseFullRange) and 
      (not m_PreserveCollinear or
      not Pt2IsBetweenPt1AndPt3(E.Prev.Curr, E.Curr, E.Next.Curr)))
      #Collinear edges are allowed for open paths but in closed paths
      #the default is to merge adjacent collinear edges into a single edge.
      #However, the PreserveCollinear property is enabled, overlapping
      #collinear edges (ie spikes) will be removed from closed paths.
      if (E == eStart) eStart = E.Next
      E = RemoveEdge(E)
      E = E.Prev
      eLoopStop = E
      continue

    E = E.Next
    if ((E == eLoopStop) or (not Closed and E.Next == eStart)) break


  if (not Closed and (E == E.Next)) or (Closed and (E.Prev == E.Next)):
    delete [] edges
    return False


  if not Closed:
  { 
    m_HasOpenPaths = True
    eStart.Prev.OutIdx = Skip


  #3. Do second stage of edge initialization ...
  E = eStart
  do
    InitEdge2(*E, PolyTyp)
    E = E.Next
    if (IsFlat and E.Curr.Y != eStart.Curr.Y) IsFlat = False

  while (E != eStart)

  #4. Finally, edge bounds to LocalMinima list ...

  #Totally flat paths must be handled differently when adding them
  #to LocalMinima list to avoid endless loops etc ...
  if (IsFlat) 
    if (Closed) 
      delete [] edges
      return False

    E.Prev.OutIdx = Skip
    if E.Prev.Bot.X < E.Prev.Top.X) ReverseHorizontal(*E.Prev:
    locMin = LocalMinima()
    locMin.Next = 0
    locMin.Y = E.Bot.Y
    locMin.LeftBound = 0
    locMin.RightBound = E
    locMin.RightBound.Side = esRight
    locMin.RightBound.WindDelta = 0
    while (E.Next.OutIdx != Skip)
      E.NextInLML = E.Next
      if E.Bot.X != E.Prev.Top.X) ReverseHorizontal(*E:
      E = E.Next

    InsertLocalMinima(locMin)
    m_edges.push_back(edges)
	  return True


  m_edges.push_back(edges)
  bool leftBoundIsForward
  EMin = 0

  #workaround to avoid an endless loop in the while loop below when
  #open paths have matching start and end points ...
  if (E.Prev.Bot == E.Prev.Top) E = E.Next

  for (;;)
    E = FindNextLocMin(E)
    if (E == EMin) break
    elif (not EMin) EMin = E

    #E and E.Prev now share a local minima (left aligned if horizontal).
    #Compare their slopes to find which starts which bound ...
    locMin = LocalMinima
    locMin.Next = 0
    locMin.Y = E.Bot.Y
    if (E.Dx < E.Prev.Dx) 
      locMin.LeftBound = E.Prev
      locMin.RightBound = E
      leftBoundIsForward = False; #Q.nextInLML = Q.prev
    } else:
      locMin.LeftBound = E
      locMin.RightBound = E.Prev
      leftBoundIsForward = True; #Q.nextInLML = Q.next

    locMin.LeftBound.Side = esLeft
    locMin.RightBound.Side = esRight

    if (not Closed) locMin.LeftBound.WindDelta = 0
    elif locMin.LeftBound.Next == locMin.RightBound:
      locMin.LeftBound.WindDelta = -1
    else locMin.LeftBound.WindDelta = 1
    locMin.RightBound.WindDelta = -locMin.LeftBound.WindDelta

    E = ProcessBound(locMin.LeftBound, leftBoundIsForward)
    if E.OutIdx == Skip) E = ProcessBound(E, leftBoundIsForward:

    E2 = ProcessBound(locMin.RightBound, leftBoundIsForward)
    if E2.OutIdx == Skip) E2 = ProcessBound(E2, leftBoundIsForward:

    if locMin.LeftBound.OutIdx == Skip:
      locMin.LeftBound = 0
    elif locMin.RightBound.OutIdx == Skip:
      locMin.RightBound = 0
    InsertLocalMinima(locMin)
    if (not leftBoundIsForward) E = E2

  return True

#------------------------------------------------------------------------------

def AddPaths(self, &ppg, PolyTyp, Closed):
  result = False
  for (i = 0; i < ppg.size(); ++i)
    if (AddPath(ppg[i], PolyTyp, Closed)) result = True
  return result

#------------------------------------------------------------------------------

def InsertLocalMinima(self, *newLm):
  if  not  m_MinimaList :
    m_MinimaList = newLm

  elif  newLm.Y >= m_MinimaList.Y :
    newLm.Next = m_MinimaList
    m_MinimaList = newLm
  } else:
    tmpLm = m_MinimaList
    while( tmpLm.Next  and ( newLm.Y < tmpLm.Next.Y ) )
      tmpLm = tmpLm.Next
    newLm.Next = tmpLm.Next
    tmpLm.Next = newLm


#------------------------------------------------------------------------------

def Clear(self):
  DisposeLocalMinimaList()
  for (i = 0; i < m_edges.size(); ++i)
    #for each edge array in turn, the first used edge and 
    #check for and remove any hiddenPts in each edge in the array.
    edges = m_edges[i]
    delete [] edges

  m_edges.clear()
  m_UseFullRange = False
  m_HasOpenPaths = False

#------------------------------------------------------------------------------

def Reset(self):
  m_CurrentLM = m_MinimaList
  if( not m_CurrentLM ) return; #ie nothing to process

  #reset all edges ...
  lm = m_MinimaList
  while( lm )
    e = lm.LeftBound
    if e:
      e.Curr = e.Bot
      e.Side = esLeft
      e.OutIdx = Unassigned


    e = lm.RightBound
    if e:
      e.Curr = e.Bot
      e.Side = esRight
      e.OutIdx = Unassigned

    lm = lm.Next


#------------------------------------------------------------------------------

def DisposeLocalMinimaList(self):
  while( m_MinimaList )
    tmpLm = m_MinimaList.Next
    delete m_MinimaList
    m_MinimaList = tmpLm

  m_CurrentLM = 0

#------------------------------------------------------------------------------

def PopLocalMinima(self):
  if( not  m_CurrentLM ) return
  m_CurrentLM = m_CurrentLM.Next

#------------------------------------------------------------------------------

def GetBounds(self):
  IntRect result
  lm = m_MinimaList
  if not lm:
    result.left = result.top = result.right = result.bottom = 0
    return result

  result.left = lm.LeftBound.Bot.X
  result.top = lm.LeftBound.Bot.Y
  result.right = lm.LeftBound.Bot.X
  result.bottom = lm.LeftBound.Bot.Y
  while (lm)
    if lm.LeftBound.Bot.Y > result.bottom:
      result.bottom = lm.LeftBound.Bot.Y
    e = lm.LeftBound
    for (;;)      bottomE = e
      while (e.NextInLML)
        if (e.Bot.X < result.left) result.left = e.Bot.X
        if (e.Bot.X > result.right) result.right = e.Bot.X
        e = e.NextInLML

      if (e.Bot.X < result.left) result.left = e.Bot.X
      if (e.Bot.X > result.right) result.right = e.Bot.X
      if (e.Top.X < result.left) result.left = e.Top.X
      if (e.Top.X > result.right) result.right = e.Top.X
      if (e.Top.Y < result.top) result.top = e.Top.Y

      if (bottomE == lm.LeftBound) e = lm.RightBound
      else break

    lm = lm.Next

  return result


#------------------------------------------------------------------------------
# TClipper methods ...
#------------------------------------------------------------------------------

Clipper.Clipper(int initOptions) : ClipperBase() #constructor
  m_ActiveEdges = 0
  m_SortedEdges = 0
  m_ExecuteLocked = False
  m_UseFullRange = False
  m_ReverseOutput = ((initOptions & ioReverseSolution) != 0)
  m_StrictSimple = ((initOptions & ioStrictlySimple) != 0)
  m_PreserveCollinear = ((initOptions & ioPreserveCollinear) != 0)
  m_HasOpenPaths = False
#ifdef use_xyz  
  m_ZFill = 0
#endif

#------------------------------------------------------------------------------

Clipper.~Clipper() #destructor
  Clear()
  m_Scanbeam.clear()

#------------------------------------------------------------------------------

#ifdef use_xyz  
def ZFillFunction(self, zFillFunc):
{  
  m_ZFill = zFillFunc

#------------------------------------------------------------------------------
#endif

def Reset(self):
  ClipperBase.Reset()
  m_Scanbeam.clear()
  m_ActiveEdges = 0
  m_SortedEdges = 0
  lm = m_MinimaList
  while (lm)
    InsertScanbeam(lm.Y)
    lm = lm.Next


#------------------------------------------------------------------------------

bool Clipper.Execute(ClipType clipType, &solution,
    PolyFillType subjFillType, clipFillType)
  if( m_ExecuteLocked ) return False
  if m_HasOpenPaths:
    throw clipperException("Error: PolyTree struct is need for open path clipping.")
  m_ExecuteLocked = True
  solution.resize(0)
  m_SubjFillType = subjFillType
  m_ClipFillType = clipFillType
  m_ClipType = clipType
  m_UsingPolyTree = False
  succeeded = ExecuteInternal()
  if succeeded) BuildResult(solution:
  DisposeAllOutRecs()
  m_ExecuteLocked = False
  return succeeded

#------------------------------------------------------------------------------

bool Clipper.Execute(ClipType clipType, polytree,
    PolyFillType subjFillType, clipFillType)
  if( m_ExecuteLocked ) return False
  m_ExecuteLocked = True
  m_SubjFillType = subjFillType
  m_ClipFillType = clipFillType
  m_ClipType = clipType
  m_UsingPolyTree = True
  succeeded = ExecuteInternal()
  if succeeded) BuildResult2(polytree:
  DisposeAllOutRecs()
  m_ExecuteLocked = False
  return succeeded

#------------------------------------------------------------------------------

def FixHoleLinkage(self, &outrec):
  #skip OutRecs that (a) contain outermost polygons or
  #(b) already have the correct owner/child linkage ...
  if (not outrec.FirstLeft or                
      (outrec.IsHole != outrec.FirstLeft.IsHole and
      outrec.FirstLeft.Pts)) return

  orfl = outrec.FirstLeft
  while (orfl and ((orfl.IsHole == outrec.IsHole) or not orfl.Pts))
      orfl = orfl.FirstLeft
  outrec.FirstLeft = orfl

#------------------------------------------------------------------------------

def ExecuteInternal(self):
  succeeded = True
  try    Reset()
    if (not m_CurrentLM) return False
    botY = PopScanbeam()
    do      InsertLocalMinimaIntoAEL(botY)
      ClearGhostJoins()
      ProcessHorizontals(False)
      if (m_Scanbeam.empty()) break
      topY = PopScanbeam()
      succeeded = ProcessIntersections(botY, topY)
      if (not succeeded) break
      ProcessEdgesAtTopOfScanbeam(topY)
      botY = topY
    } while (not m_Scanbeam.empty() or m_CurrentLM)

  catch(...) 
    succeeded = False


  if succeeded:
    #fix orientations ...
    for (i = 0; i < m_PolyOuts.size(); ++i)
      OutRec *outRec = m_PolyOuts[i]
      if (not outRec.Pts or outRec.IsOpen) continue
      if (outRec.IsHole ^ m_ReverseOutput) == (Area(*outRec) > 0):
        ReversePolyPtLinks(outRec.Pts)


    if not m_Joins.empty()) JoinCommonEdges(:

    #unfortunately FixupOutPolygon() must be done after JoinCommonEdges()
    for (i = 0; i < m_PolyOuts.size(); ++i)
      OutRec *outRec = m_PolyOuts[i]
      if outRec.Pts and not outRec.IsOpen:
        FixupOutPolygon(*outRec)


    if m_StrictSimple) DoSimplePolygons(:


  ClearJoins()
  ClearGhostJoins()
  return succeeded

#------------------------------------------------------------------------------

def InsertScanbeam(self, Y):
  m_Scanbeam.insert(Y)

#------------------------------------------------------------------------------

def PopScanbeam(self):
  Y = *m_Scanbeam.begin()
  m_Scanbeam.erase(m_Scanbeam.begin())
  return Y

#------------------------------------------------------------------------------

def DisposeAllOutRecs(self):  for (i = 0; i < m_PolyOuts.size(); ++i)
    DisposeOutRec(i)
  m_PolyOuts.clear()

#------------------------------------------------------------------------------

def DisposeOutRec(self, index):
  OutRec *outRec = m_PolyOuts[index]
  if outRec.Pts) DisposeOutPts(outRec.Pts:
  delete outRec
  m_PolyOuts[index] = 0

#------------------------------------------------------------------------------

def SetWindingCount(self, &edge):
  TEdge *e = edge.PrevInAEL
  #find the edge of the same polytype that immediately preceeds 'edge' in AEL
  while (e  and ((e.PolyTyp != edge.PolyTyp) or (e.WindDelta == 0))) e = e.PrevInAEL
  if not e:
    edge.WindCnt = (edge.WindDelta == 0 ? 1 : edge.WindDelta)
    edge.WindCnt2 = 0
    e = m_ActiveEdges; #ie get ready to calc WindCnt2
  }   
  elif edge.WindDelta == 0 and m_ClipType != ctUnion:
    edge.WindCnt = 1
    edge.WindCnt2 = e.WindCnt2
    e = e.NextInAEL; #ie get ready to calc WindCnt2

  elif IsEvenOddFillType(edge):
    #EvenOdd filling ...
    if edge.WindDelta == 0:
      #are we inside a subj polygon ...
      Inside = True
      TEdge *e2 = e.PrevInAEL
      while (e2)
        if (e2.PolyTyp == e.PolyTyp and e2.WindDelta != 0) 
          Inside = not Inside
        e2 = e2.PrevInAEL

      edge.WindCnt = (Inside ? 0 : 1)

    else:
      edge.WindCnt = edge.WindDelta

    edge.WindCnt2 = e.WindCnt2
    e = e.NextInAEL; #ie get ready to calc WindCnt2
  } 
  else:
    #nonZero, or Negative filling ...
    if e.WindCnt * e.WindDelta < 0:
      #prev edge is 'decreasing' WindCount (WC) toward zero
      #so we're outside the previous polygon ...
      if Abs(e.WindCnt) > 1:
        #outside prev poly but still inside another.
        #when reversing direction of prev poly use the same WC 
        if (e.WindDelta * edge.WindDelta < 0) edge.WindCnt = e.WindCnt
        #otherwise continue to 'decrease' WC ...
        else edge.WindCnt = e.WindCnt + edge.WindDelta
      } 
      else:
        #now outside all polys of same polytype so set own WC ...
        edge.WindCnt = (edge.WindDelta == 0 ? 1 : edge.WindDelta)
    } else:
      #prev edge is 'increasing' WindCount (WC) away from zero
      #so we're inside the previous polygon ...
      if (edge.WindDelta == 0) 
        edge.WindCnt = (e.WindCnt < 0 ? e.WindCnt - 1 : e.WindCnt + 1)
      #if wind direction is reversing prev then use same WC
      elif (e.WindDelta * edge.WindDelta < 0) edge.WindCnt = e.WindCnt
      #otherwise add to WC ...
      else edge.WindCnt = e.WindCnt + edge.WindDelta

    edge.WindCnt2 = e.WindCnt2
    e = e.NextInAEL; #ie get ready to calc WindCnt2


  #update WindCnt2 ...
  if IsEvenOddAltFillType(edge):
    #EvenOdd filling ...
    while (e != &edge)
      if e.WindDelta != 0:
        edge.WindCnt2 = (edge.WindCnt2 == 0 ? 1 : 0)
      e = e.NextInAEL

  } else:
    #nonZero, or Negative filling ...
    while ( e != &edge )
      edge.WindCnt2 += e.WindDelta
      e = e.NextInAEL



#------------------------------------------------------------------------------

def IsEvenOddFillType(self, edge):
  if edge.PolyTyp == ptSubject:
    return m_SubjFillType == pftEvenOdd; else:
    return m_ClipFillType == pftEvenOdd

#------------------------------------------------------------------------------

def IsEvenOddAltFillType(self, edge):
  if edge.PolyTyp == ptSubject:
    return m_ClipFillType == pftEvenOdd; else:
    return m_SubjFillType == pftEvenOdd

#------------------------------------------------------------------------------

def IsContributing(self, edge):
  PolyFillType pft, pft2
  if edge.PolyTyp == ptSubject:
    pft = m_SubjFillType
    pft2 = m_ClipFillType
  } else:
    pft = m_ClipFillType
    pft2 = m_SubjFillType


  switch(pft)
    case pftEvenOdd: 
      #return False if a subj line has been flagged as inside a subj polygon
      if (edge.WindDelta == 0 and edge.WindCnt != 1) return False
      break
    case pftNonZero:
      if (Abs(edge.WindCnt) != 1) return False
      break
    case pftPositive: 
      if (edge.WindCnt != 1) return False
      break
    default: #pftNegative
      if (edge.WindCnt != -1) return False


  switch(m_ClipType)
    case ctIntersection:
      switch(pft2)
        case pftEvenOdd: 
        case pftNonZero: 
          return (edge.WindCnt2 != 0)
        case pftPositive: 
          return (edge.WindCnt2 > 0)
        default: 
          return (edge.WindCnt2 < 0)

      break
    case ctUnion:
      switch(pft2)
        case pftEvenOdd: 
        case pftNonZero: 
          return (edge.WindCnt2 == 0)
        case pftPositive: 
          return (edge.WindCnt2 <= 0)
        default: 
          return (edge.WindCnt2 >= 0)

      break
    case ctDifference:
      if edge.PolyTyp == ptSubject:
        switch(pft2)
          case pftEvenOdd: 
          case pftNonZero: 
            return (edge.WindCnt2 == 0)
          case pftPositive: 
            return (edge.WindCnt2 <= 0)
          default: 
            return (edge.WindCnt2 >= 0)

      else:
        switch(pft2)
          case pftEvenOdd: 
          case pftNonZero: 
            return (edge.WindCnt2 != 0)
          case pftPositive: 
            return (edge.WindCnt2 > 0)
          default: 
            return (edge.WindCnt2 < 0)

      break
    case ctXor:
      if (edge.WindDelta == 0) #XOr always contributing unless open
        switch(pft2)
          case pftEvenOdd: 
          case pftNonZero: 
            return (edge.WindCnt2 == 0)
          case pftPositive: 
            return (edge.WindCnt2 <= 0)
          default: 
            return (edge.WindCnt2 >= 0)

      else:
        return True
      break
    default:
      return True


#------------------------------------------------------------------------------

def AddLocalMinPoly(self, *e1, *e2, &Pt):
  OutPt* result
  TEdge *e, *prevE
  if IsHorizontal(*e2) or ( e1.Dx > e2.Dx ):
    result = AddOutPt(e1, Pt)
    e2.OutIdx = e1.OutIdx
    e1.Side = esLeft
    e2.Side = esRight
    e = e1
    if e.PrevInAEL == e2:
      prevE = e2.PrevInAEL; 
    else:
      prevE = e.PrevInAEL
  } else:
    result = AddOutPt(e2, Pt)
    e1.OutIdx = e2.OutIdx
    e1.Side = esRight
    e2.Side = esLeft
    e = e2
    if e.PrevInAEL == e1:
        prevE = e1.PrevInAEL
    else:
        prevE = e.PrevInAEL


  if (prevE and prevE.OutIdx >= 0 and
      (TopX(*prevE, Pt.Y) == TopX(*e, Pt.Y)) and
      SlopesEqual(*e, *prevE, m_UseFullRange) and
      (e.WindDelta != 0) and (prevE.WindDelta != 0))
    outPt = AddOutPt(prevE, Pt)
    AddJoin(result, outPt, e.Top)

  return result

#------------------------------------------------------------------------------

def AddLocalMaxPoly(self, *e1, *e2, &Pt):
  AddOutPt( e1, Pt )
  if e2.WindDelta == 0) AddOutPt(e2, Pt:
  if  e1.OutIdx == e2.OutIdx :
    e1.OutIdx = Unassigned
    e2.OutIdx = Unassigned

  elif (e1.OutIdx < e2.OutIdx) 
    AppendPolygon(e1, e2); 
  else:
    AppendPolygon(e2, e1)

#------------------------------------------------------------------------------

def AddEdgeToSEL(self, *edge):
  #SEL pointers in PEdge are reused to build a list of horizontal edges.
  #However, don't need to worry about order with horizontal edge processing.
  if  not m_SortedEdges :
    m_SortedEdges = edge
    edge.PrevInSEL = 0
    edge.NextInSEL = 0

  else:
    edge.NextInSEL = m_SortedEdges
    edge.PrevInSEL = 0
    m_SortedEdges.PrevInSEL = edge
    m_SortedEdges = edge


#------------------------------------------------------------------------------

def CopyAELToSEL(self):
  e = m_ActiveEdges
  m_SortedEdges = e
  while ( e )
    e.PrevInSEL = e.PrevInAEL
    e.NextInSEL = e.NextInAEL
    e = e.NextInAEL


#------------------------------------------------------------------------------

def AddJoin(self, *op1, *op2, OffPt):
  j = Join
  j.OutPt1 = op1
  j.OutPt2 = op2
  j.OffPt = OffPt
  m_Joins.push_back(j)

#------------------------------------------------------------------------------

def ClearJoins(self):
  for (i = 0; i < m_Joins.size(); i++)
    delete m_Joins[i]
  m_Joins.resize(0)

#------------------------------------------------------------------------------

def ClearGhostJoins(self):
  for (i = 0; i < m_GhostJoins.size(); i++)
    delete m_GhostJoins[i]
  m_GhostJoins.resize(0)

#------------------------------------------------------------------------------

def AddGhostJoin(self, *op, OffPt):
  j = Join
  j.OutPt1 = op
  j.OutPt2 = 0
  j.OffPt = OffPt
  m_GhostJoins.push_back(j)

#------------------------------------------------------------------------------

def InsertLocalMinimaIntoAEL(self, botY):
  while(  m_CurrentLM  and ( m_CurrentLM.Y == botY ) )
    lb = m_CurrentLM.LeftBound
    rb = m_CurrentLM.RightBound
    PopLocalMinima()
    OutPt *Op1 = 0
    if not lb:
      #nb: don't insert LB into either AEL or SEL
      InsertEdgeIntoAEL(rb, 0)
      SetWindingCount(*rb)
      if IsContributing(*rb):
        Op1 = AddOutPt(rb, rb.Bot); 
    } 
    elif not rb:
      InsertEdgeIntoAEL(lb, 0)
      SetWindingCount(*lb)
      if IsContributing(*lb):
        Op1 = AddOutPt(lb, lb.Bot)
      InsertScanbeam(lb.Top.Y)

    else:
      InsertEdgeIntoAEL(lb, 0)
      InsertEdgeIntoAEL(rb, lb)
      SetWindingCount( *lb )
      rb.WindCnt = lb.WindCnt
      rb.WindCnt2 = lb.WindCnt2
      if IsContributing(*lb):
        Op1 = AddLocalMinPoly(lb, rb, lb.Bot);      
      InsertScanbeam(lb.Top.Y)


     if rb:
       if IsHorizontal(*rb)) AddEdgeToSEL(rb:
       else InsertScanbeam( rb.Top.Y )


    if (not lb or not rb) continue

    #if any output polygons share an edge, they'll need joining later ...
    if (Op1 and IsHorizontal(*rb) and 
      m_GhostJoins.size() > 0 and (rb.WindDelta != 0))
      for (i = 0; i < m_GhostJoins.size(); ++i)
        jr = m_GhostJoins[i]
        #if the horizontal Rb and a 'ghost' horizontal overlap, convert
        #the 'ghost' join to a real join ready for later ...
        if HorzSegmentsOverlap(jr.OutPt1.Pt.X, jr.OffPt.X, rb.Bot.X, rb.Top.X):
          AddJoin(jr.OutPt1, Op1, jr.OffPt)



    if (lb.OutIdx >= 0 and lb.PrevInAEL and 
      lb.PrevInAEL.Curr.X == lb.Bot.X and
      lb.PrevInAEL.OutIdx >= 0 and
      SlopesEqual(*lb.PrevInAEL, *lb, m_UseFullRange) and
      (lb.WindDelta != 0) and (lb.PrevInAEL.WindDelta != 0))
        OutPt *Op2 = AddOutPt(lb.PrevInAEL, lb.Bot)
        AddJoin(Op1, Op2, lb.Top)


    if lb.NextInAEL != rb:

      if (rb.OutIdx >= 0 and rb.PrevInAEL.OutIdx >= 0 and
        SlopesEqual(*rb.PrevInAEL, *rb, m_UseFullRange) and
        (rb.WindDelta != 0) and (rb.PrevInAEL.WindDelta != 0))
          OutPt *Op2 = AddOutPt(rb.PrevInAEL, rb.Bot)
          AddJoin(Op1, Op2, rb.Top)


      e = lb.NextInAEL
      if e:
        while( e != rb )
          #nb: For calculating winding counts etc, IntersectEdges() assumes
          #that param1 will be to the Right of param2 ABOVE the intersection ...
          IntersectEdges(rb , e , lb.Curr); #order important here
          e = e.NextInAEL



    


#------------------------------------------------------------------------------

def DeleteFromAEL(self, *e):
  AelPrev = e.PrevInAEL
  AelNext = e.NextInAEL
  if(  not AelPrev and  not AelNext and (e != m_ActiveEdges) ) return; #already deleted
  if( AelPrev ) AelPrev.NextInAEL = AelNext
  m_ActiveEdges = AelNext
  if( AelNext ) AelNext.PrevInAEL = AelPrev
  e.NextInAEL = 0
  e.PrevInAEL = 0

#------------------------------------------------------------------------------

def DeleteFromSEL(self, *e):
  SelPrev = e.PrevInSEL
  SelNext = e.NextInSEL
  if( not SelPrev and  not SelNext and (e != m_SortedEdges) ) return; #already deleted
  if( SelPrev ) SelPrev.NextInSEL = SelNext
  m_SortedEdges = SelNext
  if( SelNext ) SelNext.PrevInSEL = SelPrev
  e.NextInSEL = 0
  e.PrevInSEL = 0

#------------------------------------------------------------------------------

#ifdef use_xyz
def SetZ(self, pt, e1, e2):
  if (pt.Z != 0 or not m_ZFill) return
  elif (pt == e1.Bot) pt.Z = e1.Bot.Z
  elif (pt == e1.Top) pt.Z = e1.Top.Z
  elif (pt == e2.Bot) pt.Z = e2.Bot.Z
  elif (pt == e2.Top) pt.Z = e2.Top.Z
  else (*m_ZFill)(e1.Bot, e1.Top, e2.Bot, e2.Top, pt); 

#------------------------------------------------------------------------------
#endif

def IntersectEdges(self, *e1, *e2, &Pt):
  e1Contributing = ( e1.OutIdx >= 0 )
  e2Contributing = ( e2.OutIdx >= 0 )

#ifdef use_xyz
        SetZ(Pt, *e1, *e2)
#endif

#ifdef use_lines
  #if either edge is on an OPEN path ...
  if e1.WindDelta == 0 or e2.WindDelta == 0:
    #ignore subject-subject open path intersections UNLESS they
    #are both open paths, they are both 'contributing maximas' ...
	if (e1.WindDelta == 0 and e2.WindDelta == 0) return

    #if intersecting a subj line with a subj poly ...
    elif (e1.PolyTyp == e2.PolyTyp and 
      e1.WindDelta != e2.WindDelta and m_ClipType == ctUnion)
      if e1.WindDelta == 0:
        if e2Contributing:
          AddOutPt(e1, Pt)
          if (e1Contributing) e1.OutIdx = Unassigned


      else:
        if e1Contributing:
          AddOutPt(e2, Pt)
          if (e2Contributing) e2.OutIdx = Unassigned



    elif e1.PolyTyp != e2.PolyTyp:
      #toggle subj open path OutIdx on/off when Abs(clip.WndCnt) == 1 ...
      if ((e1.WindDelta == 0) and abs(e2.WindCnt) == 1 and 
        (m_ClipType != ctUnion or e2.WindCnt2 == 0))
        AddOutPt(e1, Pt)
        if (e1Contributing) e1.OutIdx = Unassigned

      elif ((e2.WindDelta == 0) and (abs(e1.WindCnt) == 1) and 
        (m_ClipType != ctUnion or e1.WindCnt2 == 0))
        AddOutPt(e2, Pt)
        if (e2Contributing) e2.OutIdx = Unassigned


    return

#endif

  #update winding counts...
  #assumes that e1 will be to the Right of e2 ABOVE the intersection
  if  e1.PolyTyp == e2.PolyTyp :
    if  IsEvenOddFillType( *e1) :
      oldE1WindCnt = e1.WindCnt
      e1.WindCnt = e2.WindCnt
      e2.WindCnt = oldE1WindCnt
    } else:
      if (e1.WindCnt + e2.WindDelta == 0 ) e1.WindCnt = -e1.WindCnt
      else e1.WindCnt += e2.WindDelta
      if ( e2.WindCnt - e1.WindDelta == 0 ) e2.WindCnt = -e2.WindCnt
      else e2.WindCnt -= e1.WindDelta

  } else:
    if (not IsEvenOddFillType(*e2)) e1.WindCnt2 += e2.WindDelta
    else e1.WindCnt2 = ( e1.WindCnt2 == 0 ) ? 1 : 0
    if (not IsEvenOddFillType(*e1)) e2.WindCnt2 -= e1.WindDelta
    else e2.WindCnt2 = ( e2.WindCnt2 == 0 ) ? 1 : 0


  PolyFillType e1FillType, e2FillType, e1FillType2, e2FillType2
  if e1.PolyTyp == ptSubject:
    e1FillType = m_SubjFillType
    e1FillType2 = m_ClipFillType
  } else:
    e1FillType = m_ClipFillType
    e1FillType2 = m_SubjFillType

  if e2.PolyTyp == ptSubject:
    e2FillType = m_SubjFillType
    e2FillType2 = m_ClipFillType
  } else:
    e2FillType = m_ClipFillType
    e2FillType2 = m_SubjFillType


  cInt e1Wc, e2Wc
  switch (e1FillType)
    case e1Wc = e1.WindCnt; break
    case e1Wc = -e1.WindCnt; break
    e1Wc = Abs(e1.WindCnt)

  switch(e2FillType)
    case e2Wc = e2.WindCnt; break
    case e2Wc = -e2.WindCnt; break
    e2Wc = Abs(e2.WindCnt)


  if  e1Contributing and e2Contributing :
    if ((e1Wc != 0 and e1Wc != 1) or (e2Wc != 0 and e2Wc != 1) or
      (e1.PolyTyp != e2.PolyTyp and m_ClipType != ctXor) )
      AddLocalMaxPoly(e1, e2, Pt); 

    else:
      AddOutPt(e1, Pt)
      AddOutPt(e2, Pt)
      SwapSides( *e1 , *e2 )
      SwapPolyIndexes( *e1 , *e2 )


  elif  e1Contributing :
    if (e2Wc == 0 or e2Wc == 1) 
      AddOutPt(e1, Pt)
      SwapSides(*e1, *e2)
      SwapPolyIndexes(*e1, *e2)


  elif  e2Contributing :
    if (e1Wc == 0 or e1Wc == 1) 
      AddOutPt(e2, Pt)
      SwapSides(*e1, *e2)
      SwapPolyIndexes(*e1, *e2)

  } 
  elif  (e1Wc == 0 or e1Wc == 1) and (e2Wc == 0 or e2Wc == 1):
    #neither edge is currently contributing ...

    cInt e1Wc2, e2Wc2
    switch (e1FillType2)
      case e1Wc2 = e1.WindCnt2; break
      case pftNegative e1Wc2 = -e1.WindCnt2; break
      e1Wc2 = Abs(e1.WindCnt2)

    switch (e2FillType2)
      case e2Wc2 = e2.WindCnt2; break
      case e2Wc2 = -e2.WindCnt2; break
      e2Wc2 = Abs(e2.WindCnt2)


    if e1.PolyTyp != e2.PolyTyp:
      AddLocalMinPoly(e1, e2, Pt)

    elif e1Wc == 1 and e2Wc == 1:
      switch( m_ClipType )        case ctIntersection:
          if e1Wc2 > 0 and e2Wc2 > 0:
            AddLocalMinPoly(e1, e2, Pt)
          break
        case ctUnion:
          if  e1Wc2 <= 0 and e2Wc2 <= 0 :
            AddLocalMinPoly(e1, e2, Pt)
          break
        case ctDifference:
          if (((e1.PolyTyp == ptClip) and (e1Wc2 > 0) and (e2Wc2 > 0)) or
              ((e1.PolyTyp == ptSubject) and (e1Wc2 <= 0) and (e2Wc2 <= 0)))
                AddLocalMinPoly(e1, e2, Pt)
          break
        case ctXor:
          AddLocalMinPoly(e1, e2, Pt)

    else:
      SwapSides( *e1, *e2 )


#------------------------------------------------------------------------------

def SetHoleState(self, *e, *outrec):
  IsHole = False
  TEdge *e2 = e.PrevInAEL
  while (e2)
    if e2.OutIdx >= 0 and e2.WindDelta != 0:
      IsHole = not IsHole
      if not  outrec.FirstLeft:
        outrec.FirstLeft = m_PolyOuts[e2.OutIdx]

    e2 = e2.PrevInAEL

  if (IsHole) outrec.IsHole = True

#------------------------------------------------------------------------------

def GetLowermostRec(self, *outRec1, *outRec2):
  #work out which polygon fragment has the correct hole state ...
  if (not outRec1.BottomPt) 
    outRec1.BottomPt = GetBottomPt(outRec1.Pts)
  if (not outRec2.BottomPt) 
    outRec2.BottomPt = GetBottomPt(outRec2.Pts)
  OutPt *OutPt1 = outRec1.BottomPt
  OutPt *OutPt2 = outRec2.BottomPt
  if (OutPt1.Pt.Y > OutPt2.Pt.Y) return outRec1
  elif (OutPt1.Pt.Y < OutPt2.Pt.Y) return outRec2
  elif (OutPt1.Pt.X < OutPt2.Pt.X) return outRec1
  elif (OutPt1.Pt.X > OutPt2.Pt.X) return outRec2
  elif (OutPt1.Next == OutPt1) return outRec2
  elif (OutPt2.Next == OutPt2) return outRec1
  elif (FirstIsBottomPt(OutPt1, OutPt2)) return outRec1
  else return outRec2

#------------------------------------------------------------------------------

def Param1RightOfParam2(self, outRec1, outRec2):
  do
    outRec1 = outRec1.FirstLeft
    if (outRec1 == outRec2) return True
  } while (outRec1)
  return False

#------------------------------------------------------------------------------

def GetOutRec(self, Idx):
  outrec = m_PolyOuts[Idx]
  while (outrec != m_PolyOuts[outrec.Idx])
    outrec = m_PolyOuts[outrec.Idx]
  return outrec

#------------------------------------------------------------------------------

def AppendPolygon(self, *e1, *e2):
  #get the start and ends of both output polygons ...
  OutRec *outRec1 = m_PolyOuts[e1.OutIdx]
  OutRec *outRec2 = m_PolyOuts[e2.OutIdx]

  OutRec *holeStateRec
  if (Param1RightOfParam2(outRec1, outRec2)) 
    holeStateRec = outRec2
  elif (Param1RightOfParam2(outRec2, outRec1)) 
    holeStateRec = outRec1
  else:
    holeStateRec = GetLowermostRec(outRec1, outRec2)

  #get the start and ends of both output polygons and
  #join e2 poly onto e1 poly and delete pointers to e2 ...

  p1_lft = outRec1.Pts
  p1_rt = p1_lft.Prev
  p2_lft = outRec2.Pts
  p2_rt = p2_lft.Prev

  EdgeSide Side
  #join e2 poly onto e1 poly and delete pointers to e2 ...
  if   e1.Side == esLeft :
    if   e2.Side == esLeft :
      #z y x a b c
      ReversePolyPtLinks(p2_lft)
      p2_lft.Next = p1_lft
      p1_lft.Prev = p2_lft
      p1_rt.Next = p2_rt
      p2_rt.Prev = p1_rt
      outRec1.Pts = p2_rt
    } else:
      #x y z a b c
      p2_rt.Next = p1_lft
      p1_lft.Prev = p2_rt
      p2_lft.Prev = p1_rt
      p1_rt.Next = p2_lft
      outRec1.Pts = p2_lft

    Side = esLeft
  } else:
    if   e2.Side == esRight :
      #a b c z y x
      ReversePolyPtLinks(p2_lft)
      p1_rt.Next = p2_rt
      p2_rt.Prev = p1_rt
      p2_lft.Next = p1_lft
      p1_lft.Prev = p2_lft
    } else:
      #a b c x y z
      p1_rt.Next = p2_lft
      p2_lft.Prev = p1_rt
      p1_lft.Prev = p2_rt
      p2_rt.Next = p1_lft

    Side = esRight


  outRec1.BottomPt = 0
  if holeStateRec == outRec2:
    if outRec2.FirstLeft != outRec1:
      outRec1.FirstLeft = outRec2.FirstLeft
    outRec1.IsHole = outRec2.IsHole

  outRec2.Pts = 0
  outRec2.BottomPt = 0
  outRec2.FirstLeft = outRec1

  OKIdx = e1.OutIdx
  ObsoleteIdx = e2.OutIdx

  e1.OutIdx = Unassigned; #nb: safe because we only get here via AddLocalMaxPoly
  e2.OutIdx = Unassigned

  e = m_ActiveEdges
  while( e )
    if  e.OutIdx == ObsoleteIdx :
      e.OutIdx = OKIdx
      e.Side = Side
      break

    e = e.NextInAEL


  outRec2.Idx = outRec1.Idx

#------------------------------------------------------------------------------

def CreateOutRec(self):
  result = OutRec
  result.IsHole = False
  result.IsOpen = False
  result.FirstLeft = 0
  result.Pts = 0
  result.BottomPt = 0
  result.PolyNd = 0
  m_PolyOuts.push_back(result)
  result.Idx = (int)m_PolyOuts.size()-1
  return result

#------------------------------------------------------------------------------

def AddOutPt(self, *e, &pt):
  ToFront = (e.Side == esLeft)
  if   e.OutIdx < 0 :
    OutRec *outRec = CreateOutRec()
    outRec.IsOpen = (e.WindDelta == 0)
    newOp = OutPt
    outRec.Pts = newOp
    newOp.Idx = outRec.Idx
    newOp.Pt = pt
    newOp.Next = newOp
    newOp.Prev = newOp
    if not outRec.IsOpen:
      SetHoleState(e, outRec)
    e.OutIdx = outRec.Idx
    return newOp
  } else:
    OutRec *outRec = m_PolyOuts[e.OutIdx]
    #OutRec.Pts is the 'Left-most' point & OutRec.Pts.Prev is the 'Right-most'
    op = outRec.Pts

    if (ToFront and (pt == op.Pt)) return op
    elif (not ToFront and (pt == op.Prev.Pt)) return op.Prev

    newOp = OutPt
    newOp.Idx = outRec.Idx
    newOp.Pt = pt
    newOp.Next = op
    newOp.Prev = op.Prev
    newOp.Prev.Next = newOp
    op.Prev = newOp
    if (ToFront) outRec.Pts = newOp
    return newOp


#------------------------------------------------------------------------------

def ProcessHorizontals(self, IsTopOfScanbeam):
  horzEdge = m_SortedEdges
  while(horzEdge)
    DeleteFromSEL(horzEdge)
    ProcessHorizontal(horzEdge, IsTopOfScanbeam)
    horzEdge = m_SortedEdges


#------------------------------------------------------------------------------

inline bool IsMinima(TEdge *e)
  return e  and (e.Prev.NextInLML != e) and (e.Next.NextInLML != e)

#------------------------------------------------------------------------------

inline bool IsMaxima(TEdge *e, Y)
  return e and e.Top.Y == Y and not e.NextInLML

#------------------------------------------------------------------------------

inline bool IsIntermediate(TEdge *e, Y)
  return e.Top.Y == Y and e.NextInLML

#------------------------------------------------------------------------------

TEdge *GetMaximaPair(TEdge *e)
  result = 0
  if (e.Next.Top == e.Top) and not e.Next.NextInLML:
    result = e.Next
  elif (e.Prev.Top == e.Top) and not e.Prev.NextInLML:
    result = e.Prev

  if (result and (result.OutIdx == Skip or
    #result is False if both NextInAEL & PrevInAEL are nil & not horizontal ...
    (result.NextInAEL == result.PrevInAEL and not IsHorizontal(*result))))
      return 0
  return result

#------------------------------------------------------------------------------

def SwapPositionsInAEL(self, *Edge1, *Edge2):
  #check that one or other edge hasn't already been removed from AEL ...
  if (Edge1.NextInAEL == Edge1.PrevInAEL or 
    Edge2.NextInAEL == Edge2.PrevInAEL) return

  if   Edge1.NextInAEL == Edge2 :
    Next = Edge2.NextInAEL
    if( Next ) Next.PrevInAEL = Edge1
    Prev = Edge1.PrevInAEL
    if( Prev ) Prev.NextInAEL = Edge2
    Edge2.PrevInAEL = Prev
    Edge2.NextInAEL = Edge1
    Edge1.PrevInAEL = Edge2
    Edge1.NextInAEL = Next

  elif   Edge2.NextInAEL == Edge1 :
    Next = Edge1.NextInAEL
    if( Next ) Next.PrevInAEL = Edge2
    Prev = Edge2.PrevInAEL
    if( Prev ) Prev.NextInAEL = Edge1
    Edge1.PrevInAEL = Prev
    Edge1.NextInAEL = Edge2
    Edge2.PrevInAEL = Edge1
    Edge2.NextInAEL = Next

  else:
    Next = Edge1.NextInAEL
    Prev = Edge1.PrevInAEL
    Edge1.NextInAEL = Edge2.NextInAEL
    if( Edge1.NextInAEL ) Edge1.NextInAEL.PrevInAEL = Edge1
    Edge1.PrevInAEL = Edge2.PrevInAEL
    if( Edge1.PrevInAEL ) Edge1.PrevInAEL.NextInAEL = Edge1
    Edge2.NextInAEL = Next
    if( Edge2.NextInAEL ) Edge2.NextInAEL.PrevInAEL = Edge2
    Edge2.PrevInAEL = Prev
    if( Edge2.PrevInAEL ) Edge2.PrevInAEL.NextInAEL = Edge2


  if( not Edge1.PrevInAEL ) m_ActiveEdges = Edge1
  elif( not Edge2.PrevInAEL ) m_ActiveEdges = Edge2

#------------------------------------------------------------------------------

def SwapPositionsInSEL(self, *Edge1, *Edge2):
  if(  not ( Edge1.NextInSEL ) and  not ( Edge1.PrevInSEL ) ) return
  if(  not ( Edge2.NextInSEL ) and  not ( Edge2.PrevInSEL ) ) return

  if   Edge1.NextInSEL == Edge2 :
    Next = Edge2.NextInSEL
    if( Next ) Next.PrevInSEL = Edge1
    Prev = Edge1.PrevInSEL
    if( Prev ) Prev.NextInSEL = Edge2
    Edge2.PrevInSEL = Prev
    Edge2.NextInSEL = Edge1
    Edge1.PrevInSEL = Edge2
    Edge1.NextInSEL = Next

  elif   Edge2.NextInSEL == Edge1 :
    Next = Edge1.NextInSEL
    if( Next ) Next.PrevInSEL = Edge2
    Prev = Edge2.PrevInSEL
    if( Prev ) Prev.NextInSEL = Edge1
    Edge1.PrevInSEL = Prev
    Edge1.NextInSEL = Edge2
    Edge2.PrevInSEL = Edge1
    Edge2.NextInSEL = Next

  else:
    Next = Edge1.NextInSEL
    Prev = Edge1.PrevInSEL
    Edge1.NextInSEL = Edge2.NextInSEL
    if( Edge1.NextInSEL ) Edge1.NextInSEL.PrevInSEL = Edge1
    Edge1.PrevInSEL = Edge2.PrevInSEL
    if( Edge1.PrevInSEL ) Edge1.PrevInSEL.NextInSEL = Edge1
    Edge2.NextInSEL = Next
    if( Edge2.NextInSEL ) Edge2.NextInSEL.PrevInSEL = Edge2
    Edge2.PrevInSEL = Prev
    if( Edge2.PrevInSEL ) Edge2.PrevInSEL.NextInSEL = Edge2


  if( not Edge1.PrevInSEL ) m_SortedEdges = Edge1
  elif( not Edge2.PrevInSEL ) m_SortedEdges = Edge2

#------------------------------------------------------------------------------

def GetNextInAEL(self, *e, dir):
  return dir == dLeftToRight ? e.NextInAEL : e.PrevInAEL

#------------------------------------------------------------------------------

def GetHorzDirection(self, HorzEdge, Dir, Left, Right):
  if HorzEdge.Bot.X < HorzEdge.Top.X:
    Left = HorzEdge.Bot.X
    Right = HorzEdge.Top.X
    Dir = dLeftToRight
  } else:
    Left = HorzEdge.Top.X
    Right = HorzEdge.Bot.X
    Dir = dRightToLeft


#------------------------------------------------------------------------

'''******************************************************************************
* Notes: Horizontal edges (HEs) at scanline intersections (ie at the Top or    *
* Bottom of a scanbeam) are processed as if layered. The order in which HEs    *
* are processed doesn't matter. HEs intersect with other HE Bot.Xs only [#]    *
* (or they could intersect with Top.Xs only, EITHER Bot.Xs OR Top.Xs),      *
* and with other non-horizontal edges [*]. Once these intersections are        *
* processed, HEs then 'promote' the Edge above (NextInLML) into   *
* the AEL. These 'promoted' edges may in turn intersect [%] with other HEs.    *
******************************************************************************'''

def ProcessHorizontal(self, *horzEdge, isTopOfScanbeam):
  Direction dir
  cInt horzLeft, horzRight

  GetHorzDirection(*horzEdge, dir, horzLeft, horzRight)

  eLastHorz = horzEdge, *eMaxPair = 0
  while (eLastHorz.NextInLML and IsHorizontal(*eLastHorz.NextInLML)) 
    eLastHorz = eLastHorz.NextInLML
  if not eLastHorz.NextInLML:
    eMaxPair = GetMaximaPair(eLastHorz)

  for (;;)
    IsLastHorz = (horzEdge == eLastHorz)
    e = GetNextInAEL(horzEdge, dir)
    while(e)
      #Break if we've got to the end of an intermediate horizontal edge ...
      #nb: Smaller Dx's are to the right of larger Dx's ABOVE the horizontal.
      if (e.Curr.X == horzEdge.Top.X and horzEdge.NextInLML and 
        e.Dx < horzEdge.NextInLML.Dx) break

      eNext = GetNextInAEL(e, dir); #saves eNext for later

      if ((dir == dLeftToRight and e.Curr.X <= horzRight) or
        (dir == dRightToLeft and e.Curr.X >= horzLeft))
        #so far we're still in range of the horizontal Edge  but make sure
        #we're at the last of consec. horizontals when matching with eMaxPair
        if e == eMaxPair and IsLastHorz:

          if horzEdge.OutIdx >= 0:
            op1 = AddOutPt(horzEdge, horzEdge.Top)
            eNextHorz = m_SortedEdges
            while (eNextHorz)
              if (eNextHorz.OutIdx >= 0 and
                HorzSegmentsOverlap(horzEdge.Bot.X,
                horzEdge.Top.X, eNextHorz.Bot.X, eNextHorz.Top.X))
                op2 = AddOutPt(eNextHorz, eNextHorz.Bot)
                AddJoin(op2, op1, eNextHorz.Top)

              eNextHorz = eNextHorz.NextInSEL

            AddGhostJoin(op1, horzEdge.Bot)
            AddLocalMaxPoly(horzEdge, eMaxPair, horzEdge.Top)

          DeleteFromAEL(horzEdge)
          DeleteFromAEL(eMaxPair)
          return

        elif dir == dLeftToRight:
          Pt = IntPoint(e.Curr.X, horzEdge.Curr.Y)
          IntersectEdges(horzEdge, e, Pt)

        else:
          Pt = IntPoint(e.Curr.X, horzEdge.Curr.Y)
          IntersectEdges( e, horzEdge, Pt)

        SwapPositionsInAEL( horzEdge, e )

      elif( (dir == dLeftToRight and e.Curr.X >= horzRight) or
       (dir == dRightToLeft and e.Curr.X <= horzLeft) ) break
      e = eNext
    } #end while

    if horzEdge.NextInLML and IsHorizontal(*horzEdge.NextInLML):
      UpdateEdgeIntoAEL(horzEdge)
      if horzEdge.OutIdx >= 0) AddOutPt(horzEdge, horzEdge.Bot:
      GetHorzDirection(*horzEdge, dir, horzLeft, horzRight)
    } else:
      break
  } #end for (;;)

  if horzEdge.NextInLML:
    if horzEdge.OutIdx >= 0:
      op1 = AddOutPt( horzEdge, horzEdge.Top)
      if isTopOfScanbeam) AddGhostJoin(op1, horzEdge.Bot:
      UpdateEdgeIntoAEL(horzEdge)
      if (horzEdge.WindDelta == 0) return
      #nb: HorzEdge is no longer horizontal here
      ePrev = horzEdge.PrevInAEL
      eNext = horzEdge.NextInAEL
      if (ePrev and ePrev.Curr.X == horzEdge.Bot.X and
        ePrev.Curr.Y == horzEdge.Bot.Y and ePrev.WindDelta != 0 and
        (ePrev.OutIdx >= 0 and ePrev.Curr.Y > ePrev.Top.Y and
        SlopesEqual(*horzEdge, *ePrev, m_UseFullRange)))
        op2 = AddOutPt(ePrev, horzEdge.Bot)
        AddJoin(op1, op2, horzEdge.Top)

      elif (eNext and eNext.Curr.X == horzEdge.Bot.X and
        eNext.Curr.Y == horzEdge.Bot.Y and eNext.WindDelta != 0 and
        eNext.OutIdx >= 0 and eNext.Curr.Y > eNext.Top.Y and
        SlopesEqual(*horzEdge, *eNext, m_UseFullRange))
        op2 = AddOutPt(eNext, horzEdge.Bot)
        AddJoin(op1, op2, horzEdge.Top)


    else:
      UpdateEdgeIntoAEL(horzEdge); 

  else:
    if horzEdge.OutIdx >= 0) AddOutPt(horzEdge, horzEdge.Top:
    DeleteFromAEL(horzEdge)


#------------------------------------------------------------------------------

def UpdateEdgeIntoAEL(self, *&e):
  if( not e.NextInLML ) throw
    clipperException("UpdateEdgeIntoAEL: invalid call")

  e.NextInLML.OutIdx = e.OutIdx
  AelPrev = e.PrevInAEL
  AelNext = e.NextInAEL
  if (AelPrev) AelPrev.NextInAEL = e.NextInLML
  m_ActiveEdges = e.NextInLML
  if (AelNext) AelNext.PrevInAEL = e.NextInLML
  e.NextInLML.Side = e.Side
  e.NextInLML.WindDelta = e.WindDelta
  e.NextInLML.WindCnt = e.WindCnt
  e.NextInLML.WindCnt2 = e.WindCnt2
  e = e.NextInLML
  e.Curr = e.Bot
  e.PrevInAEL = AelPrev
  e.NextInAEL = AelNext
  if not IsHorizontal(*e)) InsertScanbeam(e.Top.Y:

#------------------------------------------------------------------------------

def ProcessIntersections(self, botY, topY):
  if( not m_ActiveEdges ) return True
  try    BuildIntersectList(botY, topY)
    IlSize = m_IntersectList.size()
    if (IlSize == 0) return True
    if IlSize == 1 or FixupIntersectionOrder()) ProcessIntersectList(:
    else return False

  catch(...) 
    m_SortedEdges = 0
    DisposeIntersectNodes()
    throw clipperException("ProcessIntersections error")

  m_SortedEdges = 0
  return True

#------------------------------------------------------------------------------

def DisposeIntersectNodes(self):
  for (i = 0; i < m_IntersectList.size(); ++i )
    delete m_IntersectList[i]
  m_IntersectList.clear()

#------------------------------------------------------------------------------

def BuildIntersectList(self, botY, topY):
  if ( not m_ActiveEdges ) return

  #prepare for sorting ...
  e = m_ActiveEdges
  m_SortedEdges = e
  while( e )
    e.PrevInSEL = e.PrevInAEL
    e.NextInSEL = e.NextInAEL
    e.Curr.X = TopX( *e, topY )
    e = e.NextInAEL


  #bubblesort ...
  bool isModified
  do
    isModified = False
    e = m_SortedEdges
    while( e.NextInSEL )
      TEdge *eNext = e.NextInSEL
      IntPoint Pt
      if e.Curr.X > eNext.Curr.X:
        IntersectPoint(*e, *eNext, Pt)
        IntersectNode newNode = IntersectNode
        newNode.Edge1 = e
        newNode.Edge2 = eNext
        newNode.Pt = Pt
        m_IntersectList.push_back(newNode)

        SwapPositionsInSEL(e, eNext)
        isModified = True

      else:
        e = eNext

    if( e.PrevInSEL ) e.PrevInSEL.NextInSEL = 0
    else break

  while ( isModified )
  m_SortedEdges = 0; #important

#------------------------------------------------------------------------------


def ProcessIntersectList(self):
  for (i = 0; i < m_IntersectList.size(); ++i)
    iNode = m_IntersectList[i]
      IntersectEdges( iNode.Edge1, iNode.Edge2, iNode.Pt)
      SwapPositionsInAEL( iNode.Edge1 , iNode.Edge2 )

    delete iNode

  m_IntersectList.clear()

#------------------------------------------------------------------------------

def IntersectListSort(self, node1, node2):
  return node2.Pt.Y < node1.Pt.Y

#------------------------------------------------------------------------------

inline bool EdgesAdjacent( IntersectNode &inode)
  return (inode.Edge1.NextInSEL == inode.Edge2) or
    (inode.Edge1.PrevInSEL == inode.Edge2)

#------------------------------------------------------------------------------

def FixupIntersectionOrder(self):
  #pre-condition: intersections are sorted Bottom-most first.
  #Now it's crucial that intersections are made only between adjacent edges,
  #so to ensure self the order of intersections may need adjusting ...
  CopyAELToSEL()
  std.sort(m_IntersectList.begin(), m_IntersectList.end(), IntersectListSort)
  cnt = m_IntersectList.size()
  for (i = 0; i < cnt; ++i) 
    if not EdgesAdjacent(*m_IntersectList[i]):
      j = i + 1
      while (j < cnt and not EdgesAdjacent(*m_IntersectList[j])) j++
      if (j == cnt)  return False
      std.swap(m_IntersectList[i], m_IntersectList[j])

    SwapPositionsInSEL(m_IntersectList[i].Edge1, m_IntersectList[i].Edge2)

  return True

#------------------------------------------------------------------------------

def DoMaxima(self, *e):
  eMaxPair = GetMaximaPair(e)
  if not eMaxPair:
    if e.OutIdx >= 0:
      AddOutPt(e, e.Top)
    DeleteFromAEL(e)
    return


  eNext = e.NextInAEL
  while(eNext and eNext != eMaxPair)
    IntersectEdges(e, eNext, e.Top)
    SwapPositionsInAEL(e, eNext)
    eNext = e.NextInAEL


  if e.OutIdx == Unassigned and eMaxPair.OutIdx == Unassigned:
    DeleteFromAEL(e)
    DeleteFromAEL(eMaxPair)

  elif  e.OutIdx >= 0 and eMaxPair.OutIdx >= 0 :
    if e.OutIdx >= 0) AddLocalMaxPoly(e, eMaxPair, e.Top:
    DeleteFromAEL(e)
    DeleteFromAEL(eMaxPair)

#ifdef use_lines
  elif e.WindDelta == 0:
    if (e.OutIdx >= 0) 
      AddOutPt(e, e.Top)
      e.OutIdx = Unassigned

    DeleteFromAEL(e)

    if eMaxPair.OutIdx >= 0:
      AddOutPt(eMaxPair, e.Top)
      eMaxPair.OutIdx = Unassigned

    DeleteFromAEL(eMaxPair)
  } 
#endif
  else throw clipperException("DoMaxima error")

#------------------------------------------------------------------------------

def ProcessEdgesAtTopOfScanbeam(self, topY):
  e = m_ActiveEdges
  while( e )
    #1. process maxima, them as if they're 'bent' horizontal edges,
    #   but exclude maxima with horizontal edges. nb: e can't be a horizontal.
    IsMaximaEdge = IsMaxima(e, topY)

    if IsMaximaEdge:
      eMaxPair = GetMaximaPair(e)
      IsMaximaEdge = (not eMaxPair or not IsHorizontal(*eMaxPair))


    if IsMaximaEdge:
      ePrev = e.PrevInAEL
      DoMaxima(e)
      if( not ePrev ) e = m_ActiveEdges
      e = ePrev.NextInAEL

    else:
      #2. promote horizontal edges, update Curr.X and Curr.Y ...
      if IsIntermediate(e, topY) and IsHorizontal(*e.NextInLML):
        UpdateEdgeIntoAEL(e)
        if e.OutIdx >= 0:
          AddOutPt(e, e.Bot)
        AddEdgeToSEL(e)
      } 
      else:
        e.Curr.X = TopX( *e, topY )
        e.Curr.Y = topY


      if m_StrictSimple:
      {  
        ePrev = e.PrevInAEL
        if ((e.OutIdx >= 0) and (e.WindDelta != 0) and ePrev and (ePrev.OutIdx >= 0) and
          (ePrev.Curr.X == e.Curr.X) and (ePrev.WindDelta != 0))
          pt = e.Curr
#ifdef use_xyz
          SetZ(pt, *ePrev, *e)
#endif
          op = AddOutPt(ePrev, pt)
          op2 = AddOutPt(e, pt)
          AddJoin(op, op2, pt); #StrictlySimple (type-3) join



      e = e.NextInAEL



  #3. Process horizontals at the Top of the scanbeam ...
  ProcessHorizontals(True)

  #4. Promote intermediate vertices ...
  e = m_ActiveEdges
  while(e)
    if IsIntermediate(e, topY):
      op = 0
      if( e.OutIdx >= 0 ) 
        op = AddOutPt(e, e.Top)
      UpdateEdgeIntoAEL(e)

      #if output polygons share an edge, they'll need joining later ...
      ePrev = e.PrevInAEL
      eNext = e.NextInAEL
      if (ePrev and ePrev.Curr.X == e.Bot.X and
        ePrev.Curr.Y == e.Bot.Y and op and
        ePrev.OutIdx >= 0 and ePrev.Curr.Y > ePrev.Top.Y and
        SlopesEqual(*e, *ePrev, m_UseFullRange) and
        (e.WindDelta != 0) and (ePrev.WindDelta != 0))
        op2 = AddOutPt(ePrev, e.Bot)
        AddJoin(op, op2, e.Top)

      elif (eNext and eNext.Curr.X == e.Bot.X and
        eNext.Curr.Y == e.Bot.Y and op and
        eNext.OutIdx >= 0 and eNext.Curr.Y > eNext.Top.Y and
        SlopesEqual(*e, *eNext, m_UseFullRange) and
        (e.WindDelta != 0) and (eNext.WindDelta != 0))
        op2 = AddOutPt(eNext, e.Bot)
        AddJoin(op, op2, e.Top)


    e = e.NextInAEL


#------------------------------------------------------------------------------

def FixupOutPolygon(self, &outrec):
  #FixupOutPolygon() - removes duplicate points and simplifies consecutive
  #parallel edges by removing the middle vertex.
  OutPt *lastOK = 0
  outrec.BottomPt = 0
  OutPt *pp = outrec.Pts

  for (;;)
    if pp.Prev == pp or pp.Prev == pp.Next :
      DisposeOutPts(pp)
      outrec.Pts = 0
      return


    #test for duplicate points and collinear edges ...
    if ((pp.Pt == pp.Next.Pt) or (pp.Pt == pp.Prev.Pt) or 
      (SlopesEqual(pp.Prev.Pt, pp.Pt, pp.Next.Pt, m_UseFullRange) and
      (not m_PreserveCollinear or 
      not Pt2IsBetweenPt1AndPt3(pp.Prev.Pt, pp.Pt, pp.Next.Pt))))
      lastOK = 0
      OutPt *tmp = pp
      pp.Prev.Next = pp.Next
      pp.Next.Prev = pp.Prev
      pp = pp.Prev
      delete tmp

    elif (pp == lastOK) break
    else:
      if (not lastOK) lastOK = pp
      pp = pp.Next


  outrec.Pts = pp

#------------------------------------------------------------------------------

def PointCount(self, *Pts):
    if (not Pts) return 0
    result = 0
    p = Pts
    do
        result++
        p = p.Next

    while (p != Pts)
    return result

#------------------------------------------------------------------------------

def BuildResult(self, &polys):
  polys.reserve(m_PolyOuts.size())
  for (i = 0; i < m_PolyOuts.size(); ++i)
    if (not m_PolyOuts[i].Pts) continue
    Path pg
    p = m_PolyOuts[i].Pts.Prev
    cnt = PointCount(p)
    if (cnt < 2) continue
    pg.reserve(cnt)
    for (i = 0; i < cnt; ++i)
      pg.push_back(p.Pt)
      p = p.Prev

    polys.push_back(pg)


#------------------------------------------------------------------------------

def BuildResult2(self, polytree):
    polytree.Clear()
    polytree.AllNodes.reserve(m_PolyOuts.size())
    #add each output polygon/contour to polytree ...
    for (i = 0; i < m_PolyOuts.size(); i++)
        outRec = m_PolyOuts[i]
        cnt = PointCount(outRec.Pts)
        if ((outRec.IsOpen and cnt < 2) or (not outRec.IsOpen and cnt < 3)) continue
        FixHoleLinkage(*outRec)
        pn = PolyNode()
        #nb: polytree takes ownership of all the PolyNodes
        polytree.AllNodes.push_back(pn)
        outRec.PolyNd = pn
        pn.Parent = 0
        pn.Index = 0
        pn.Contour.reserve(cnt)
        OutPt *op = outRec.Pts.Prev
        for (j = 0; j < cnt; j++)
            pn.Contour.push_back(op.Pt)
            op = op.Prev



    #fixup PolyNode links etc ...
    polytree.Childs.reserve(m_PolyOuts.size())
    for (i = 0; i < m_PolyOuts.size(); i++)
        outRec = m_PolyOuts[i]
        if (not outRec.PolyNd) continue
        if (outRec.IsOpen) 
          outRec.PolyNd.m_IsOpen = True
          polytree.AddChild(*outRec.PolyNd)

        elif (outRec.FirstLeft and outRec.FirstLeft.PolyNd) 
          outRec.FirstLeft.PolyNd.AddChild(*outRec.PolyNd)
        else:
          polytree.AddChild(*outRec.PolyNd)


#------------------------------------------------------------------------------

def SwapIntersectNodes(self, &int1, &int2):
  #just swap the contents (because fIntersectNodes is a single-linked-list)
  inode = int1; #gets a copy of Int1
  int1.Edge1 = int2.Edge1
  int1.Edge2 = int2.Edge2
  int1.Pt = int2.Pt
  int2.Edge1 = inode.Edge1
  int2.Edge2 = inode.Edge2
  int2.Pt = inode.Pt

#------------------------------------------------------------------------------

inline bool E2InsertsBeforeE1(TEdge &e1, &e2)
  if (e2.Curr.X == e1.Curr.X) 
    if e2.Top.Y > e1.Top.Y:
      return e2.Top.X < TopX(e1, e2.Top.Y); 
      else return e1.Top.X > TopX(e2, e1.Top.Y)
  } 
  else return e2.Curr.X < e1.Curr.X

#------------------------------------------------------------------------------

bool GetOverlap( cInt a1, a2, b1, b2, 
    cInt& Left, Right)
  if a1 < a2:
    if (b1 < b2) {Left = std.max(a1,b1); Right = std.min(a2,b2);
    else {Left = std.max(a1,b2); Right = std.min(a2,b1);
  } 
  else:
    if (b1 < b2) {Left = std.max(a2,b1); Right = std.min(a1,b2);
    else {Left = std.max(a2,b2); Right = std.min(a1,b1);

  return Left < Right

#------------------------------------------------------------------------------

inline void UpdateOutPtIdxs(OutRec& outrec)
{  
  op = outrec.Pts
  do
    op.Idx = outrec.Idx
    op = op.Prev

  while(op != outrec.Pts)

#------------------------------------------------------------------------------

def InsertEdgeIntoAEL(self, *edge, startEdge):
  if not m_ActiveEdges:
    edge.PrevInAEL = 0
    edge.NextInAEL = 0
    m_ActiveEdges = edge

  elif not startEdge and E2InsertsBeforeE1(*m_ActiveEdges, *edge):
      edge.PrevInAEL = 0
      edge.NextInAEL = m_ActiveEdges
      m_ActiveEdges.PrevInAEL = edge
      m_ActiveEdges = edge
  } 
  else:
    if(not startEdge) startEdge = m_ActiveEdges
    while(startEdge.NextInAEL  and 
      not E2InsertsBeforeE1(*startEdge.NextInAEL , *edge))
        startEdge = startEdge.NextInAEL
    edge.NextInAEL = startEdge.NextInAEL
    if(startEdge.NextInAEL) startEdge.NextInAEL.PrevInAEL = edge
    edge.PrevInAEL = startEdge
    startEdge.NextInAEL = edge


#----------------------------------------------------------------------

def DupOutPt(self, outPt, InsertAfter):
  result = OutPt
  result.Pt = outPt.Pt
  result.Idx = outPt.Idx
  if InsertAfter:
    result.Next = outPt.Next
    result.Prev = outPt
    outPt.Next.Prev = result
    outPt.Next = result
  } 
  else:
    result.Prev = outPt.Prev
    result.Next = outPt
    outPt.Prev.Next = result
    outPt.Prev = result

  return result

#------------------------------------------------------------------------------

bool JoinHorz(OutPt* op1, op1b, op2, op2b,
   IntPoint Pt, DiscardLeft)
  Dir1 = (op1.Pt.X > op1b.Pt.X ? dRightToLeft : dLeftToRight)
  Dir2 = (op2.Pt.X > op2b.Pt.X ? dRightToLeft : dLeftToRight)
  if (Dir1 == Dir2) return False

  #When DiscardLeft, want Op1b to be on the Left of Op1, we
  #want Op1b to be on the Right. (And likewise with Op2 and Op2b.)
  #So, facilitate self while inserting Op1b and Op2b ...
  #when DiscardLeft, sure we're AT or RIGHT of Pt before adding Op1b,
  #otherwise make sure we're AT or LEFT of Pt. (Likewise with Op2b.)
  if (Dir1 == dLeftToRight) 
    while (op1.Next.Pt.X <= Pt.X and 
      op1.Next.Pt.X >= op1.Pt.X and op1.Next.Pt.Y == Pt.Y)  
        op1 = op1.Next
    if (DiscardLeft and (op1.Pt.X != Pt.X)) op1 = op1.Next
    op1b = DupOutPt(op1, DiscardLeft)
    if (op1b.Pt != Pt) 
      op1 = op1b
      op1.Pt = Pt
      op1b = DupOutPt(op1, DiscardLeft)

  } 
  else:
    while (op1.Next.Pt.X >= Pt.X and 
      op1.Next.Pt.X <= op1.Pt.X and op1.Next.Pt.Y == Pt.Y) 
        op1 = op1.Next
    if (not DiscardLeft and (op1.Pt.X != Pt.X)) op1 = op1.Next
    op1b = DupOutPt(op1, DiscardLeft)
    if op1b.Pt != Pt:
      op1 = op1b
      op1.Pt = Pt
      op1b = DupOutPt(op1, DiscardLeft)



  if Dir2 == dLeftToRight:
    while (op2.Next.Pt.X <= Pt.X and 
      op2.Next.Pt.X >= op2.Pt.X and op2.Next.Pt.Y == Pt.Y)
        op2 = op2.Next
    if (DiscardLeft and (op2.Pt.X != Pt.X)) op2 = op2.Next
    op2b = DupOutPt(op2, DiscardLeft)
    if op2b.Pt != Pt:
      op2 = op2b
      op2.Pt = Pt
      op2b = DupOutPt(op2, DiscardLeft)

  } else:
    while (op2.Next.Pt.X >= Pt.X and 
      op2.Next.Pt.X <= op2.Pt.X and op2.Next.Pt.Y == Pt.Y) 
        op2 = op2.Next
    if (not DiscardLeft and (op2.Pt.X != Pt.X)) op2 = op2.Next
    op2b = DupOutPt(op2, DiscardLeft)
    if op2b.Pt != Pt:
      op2 = op2b
      op2.Pt = Pt
      op2b = DupOutPt(op2, DiscardLeft)



  if (Dir1 == dLeftToRight) == DiscardLeft:
    op1.Prev = op2
    op2.Next = op1
    op1b.Next = op2b
    op2b.Prev = op1b

  else:
    op1.Next = op2
    op2.Prev = op1
    op1b.Prev = op2b
    op2b.Next = op1b

  return True

#------------------------------------------------------------------------------

def JoinPoints(self, *j, outRec1, outRec2):
  OutPt *op1 = j.OutPt1, *op1b
  OutPt *op2 = j.OutPt2, *op2b

  #There are 3 kinds of joins for output polygons ...
  #1. Horizontal joins where Join.OutPt1 & Join.OutPt2 are a vertices anywhere
  #along (horizontal) collinear edges (& Join.OffPt is on the same horizontal).
  #2. Non-horizontal joins where Join.OutPt1 & Join.OutPt2 are at the same
  #location at the Bottom of the overlapping segment (& Join.OffPt is above).
  #3. StrictSimple joins where edges touch but are not collinear and where
  #Join.OutPt1, Join.OutPt2 & Join.OffPt all share the same point.
  isHorizontal = (j.OutPt1.Pt.Y == j.OffPt.Y)

  if (isHorizontal  and (j.OffPt == j.OutPt1.Pt) and
  (j.OffPt == j.OutPt2.Pt))
    #Strictly Simple join ...
    if (outRec1 != outRec2) return False
    op1b = j.OutPt1.Next
    while (op1b != op1 and (op1b.Pt == j.OffPt)) 
      op1b = op1b.Next
    reverse1 = (op1b.Pt.Y > j.OffPt.Y)
    op2b = j.OutPt2.Next
    while (op2b != op2 and (op2b.Pt == j.OffPt)) 
      op2b = op2b.Next
    reverse2 = (op2b.Pt.Y > j.OffPt.Y)
    if (reverse1 == reverse2) return False
    if reverse1:
      op1b = DupOutPt(op1, False)
      op2b = DupOutPt(op2, True)
      op1.Prev = op2
      op2.Next = op1
      op1b.Next = op2b
      op2b.Prev = op1b
      j.OutPt1 = op1
      j.OutPt2 = op1b
      return True
    } else:
      op1b = DupOutPt(op1, True)
      op2b = DupOutPt(op2, False)
      op1.Next = op2
      op2.Prev = op1
      op1b.Prev = op2b
      op2b.Next = op1b
      j.OutPt1 = op1
      j.OutPt2 = op1b
      return True

  } 
  elif isHorizontal:
    #treat horizontal joins differently to non-horizontal joins since with
    #them we're not yet sure where the overlapping is. OutPt1.Pt & OutPt2.Pt
    #may be anywhere along the horizontal edge.
    op1b = op1
    while (op1.Prev.Pt.Y == op1.Pt.Y and op1.Prev != op1b and op1.Prev != op2)
      op1 = op1.Prev
    while (op1b.Next.Pt.Y == op1b.Pt.Y and op1b.Next != op1 and op1b.Next != op2)
      op1b = op1b.Next
    if (op1b.Next == op1 or op1b.Next == op2) return False; #a flat 'polygon'

    op2b = op2
    while (op2.Prev.Pt.Y == op2.Pt.Y and op2.Prev != op2b and op2.Prev != op1b)
      op2 = op2.Prev
    while (op2b.Next.Pt.Y == op2b.Pt.Y and op2b.Next != op2 and op2b.Next != op1)
      op2b = op2b.Next
    if (op2b.Next == op2 or op2b.Next == op1) return False; #a flat 'polygon'

    cInt Left, Right
    #Op1 -. Op1b & Op2 -. Op2b are the extremites of the horizontal edges
    if not GetOverlap(op1.Pt.X, op1b.Pt.X, op2.Pt.X, op2b.Pt.X, Left, Right):
      return False

    #DiscardLeftSide: when overlapping edges are joined, spike will created
    #which needs to be cleaned up. However, don't want Op1 or Op2 caught up
    #on the discard Side as either may still be needed for other joins ...
    IntPoint Pt
    bool DiscardLeftSide
    if (op1.Pt.X >= Left and op1.Pt.X <= Right) 
      Pt = op1.Pt; DiscardLeftSide = (op1.Pt.X > op1b.Pt.X)
    } 
    elif (op2.Pt.X >= Leftand op2.Pt.X <= Right) 
      Pt = op2.Pt; DiscardLeftSide = (op2.Pt.X > op2b.Pt.X)
    } 
    elif op1b.Pt.X >= Left and op1b.Pt.X <= Right:
      Pt = op1b.Pt; DiscardLeftSide = op1b.Pt.X > op1.Pt.X
    } 
    else:
      Pt = op2b.Pt; DiscardLeftSide = (op2b.Pt.X > op2.Pt.X)

    j.OutPt1 = op1; j.OutPt2 = op2
    return JoinHorz(op1, op1b, op2, op2b, Pt, DiscardLeftSide)
  } else:
    #nb: For non-horizontal joins ...
    #    1. Jr.OutPt1.Pt.Y == Jr.OutPt2.Pt.Y
    #    2. Jr.OutPt1.Pt > Jr.OffPt.Y

    #make sure the polygons are correctly oriented ...
    op1b = op1.Next
    while ((op1b.Pt == op1.Pt) and (op1b != op1)) op1b = op1b.Next
    Reverse1 = ((op1b.Pt.Y > op1.Pt.Y) or
      not SlopesEqual(op1.Pt, op1b.Pt, j.OffPt, m_UseFullRange))
    if Reverse1:
      op1b = op1.Prev
      while ((op1b.Pt == op1.Pt) and (op1b != op1)) op1b = op1b.Prev
      if ((op1b.Pt.Y > op1.Pt.Y) or
        not SlopesEqual(op1.Pt, op1b.Pt, j.OffPt, m_UseFullRange)) return False

    op2b = op2.Next
    while ((op2b.Pt == op2.Pt) and (op2b != op2))op2b = op2b.Next
    Reverse2 = ((op2b.Pt.Y > op2.Pt.Y) or
      not SlopesEqual(op2.Pt, op2b.Pt, j.OffPt, m_UseFullRange))
    if Reverse2:
      op2b = op2.Prev
      while ((op2b.Pt == op2.Pt) and (op2b != op2)) op2b = op2b.Prev
      if ((op2b.Pt.Y > op2.Pt.Y) or
        not SlopesEqual(op2.Pt, op2b.Pt, j.OffPt, m_UseFullRange)) return False


    if ((op1b == op1) or (op2b == op2) or (op1b == op2b) or
      ((outRec1 == outRec2) and (Reverse1 == Reverse2))) return False

    if Reverse1:
      op1b = DupOutPt(op1, False)
      op2b = DupOutPt(op2, True)
      op1.Prev = op2
      op2.Next = op1
      op1b.Next = op2b
      op2b.Prev = op1b
      j.OutPt1 = op1
      j.OutPt2 = op1b
      return True
    } else:
      op1b = DupOutPt(op1, True)
      op2b = DupOutPt(op2, False)
      op1.Next = op2
      op2.Prev = op1
      op1b.Prev = op2b
      op2b.Next = op1b
      j.OutPt1 = op1
      j.OutPt2 = op1b
      return True



#----------------------------------------------------------------------

def FixupFirstLefts1(self, OldOutRec, NewOutRec):
{ 
  
  for (i = 0; i < m_PolyOuts.size(); ++i)
    outRec = m_PolyOuts[i]
    if (outRec.Pts and outRec.FirstLeft == OldOutRec) 
      if Poly2ContainsPoly1(outRec.Pts, NewOutRec.Pts):
        outRec.FirstLeft = NewOutRec



#----------------------------------------------------------------------

def FixupFirstLefts2(self, OldOutRec, NewOutRec):
{ 
  for (i = 0; i < m_PolyOuts.size(); ++i)
    outRec = m_PolyOuts[i]
    if (outRec.FirstLeft == OldOutRec) outRec.FirstLeft = NewOutRec


#----------------------------------------------------------------------

static OutRec* ParseFirstLeft(OutRec* FirstLeft)
  while (FirstLeft and not FirstLeft.Pts) 
    FirstLeft = FirstLeft.FirstLeft
  return FirstLeft

#------------------------------------------------------------------------------

def JoinCommonEdges(self):
  for (i = 0; i < m_Joins.size(); i++)
    join = m_Joins[i]

    OutRec *outRec1 = GetOutRec(join.OutPt1.Idx)
    OutRec *outRec2 = GetOutRec(join.OutPt2.Idx)

    if (not outRec1.Pts or not outRec2.Pts) continue

    #get the polygon fragment with the correct hole state (FirstLeft)
    #before calling JoinPoints() ...
    OutRec *holeStateRec
    if (outRec1 == outRec2) holeStateRec = outRec1
    elif (Param1RightOfParam2(outRec1, outRec2)) holeStateRec = outRec2
    elif (Param1RightOfParam2(outRec2, outRec1)) holeStateRec = outRec1
    holeStateRec = GetLowermostRec(outRec1, outRec2)

    if (not JoinPoints(join, outRec1, outRec2)) continue

    if outRec1 == outRec2:
      #instead of joining two polygons, we've just created a one by
      #splitting one polygon into two.
      outRec1.Pts = join.OutPt1
      outRec1.BottomPt = 0
      outRec2 = CreateOutRec()
      outRec2.Pts = join.OutPt2

      #update all OutRec2.Pts Idx's ...
      UpdateOutPtIdxs(*outRec2)

      #We now need to check every OutRec.FirstLeft pointer. If it points
      #to OutRec1 it may need to point to OutRec2 instead ...
      if m_UsingPolyTree:
        for (j = 0; j < m_PolyOuts.size() - 1; j++)
          oRec = m_PolyOuts[j]
          if (not oRec.Pts or ParseFirstLeft(oRec.FirstLeft) != outRec1 or
            oRec.IsHole == outRec1.IsHole) continue
          if Poly2ContainsPoly1(oRec.Pts, join.OutPt2):
            oRec.FirstLeft = outRec2


      if Poly2ContainsPoly1(outRec2.Pts, outRec1.Pts):
        #outRec2 is contained by outRec1 ...
        outRec2.IsHole = not outRec1.IsHole
        outRec2.FirstLeft = outRec1

        #fixup FirstLeft pointers that may need reassigning to OutRec1
        if m_UsingPolyTree) FixupFirstLefts2(outRec2, outRec1:

        if (outRec2.IsHole ^ m_ReverseOutput) == (Area(*outRec2) > 0):
          ReversePolyPtLinks(outRec2.Pts)
            
      } elif Poly2ContainsPoly1(outRec1.Pts, outRec2.Pts):
        #outRec1 is contained by outRec2 ...
        outRec2.IsHole = outRec1.IsHole
        outRec1.IsHole = not outRec2.IsHole
        outRec2.FirstLeft = outRec1.FirstLeft
        outRec1.FirstLeft = outRec2

        #fixup FirstLeft pointers that may need reassigning to OutRec1
        if m_UsingPolyTree) FixupFirstLefts2(outRec1, outRec2:

        if (outRec1.IsHole ^ m_ReverseOutput) == (Area(*outRec1) > 0):
          ReversePolyPtLinks(outRec1.Pts)
      } 
      else:
        #the 2 polygons are completely separate ...
        outRec2.IsHole = outRec1.IsHole
        outRec2.FirstLeft = outRec1.FirstLeft

        #fixup FirstLeft pointers that may need reassigning to OutRec2
        if m_UsingPolyTree) FixupFirstLefts1(outRec1, outRec2:

     
    } else:
      #joined 2 polygons together ...

      outRec2.Pts = 0
      outRec2.BottomPt = 0
      outRec2.Idx = outRec1.Idx

      outRec1.IsHole = holeStateRec.IsHole
      if (holeStateRec == outRec2) 
        outRec1.FirstLeft = outRec2.FirstLeft
      outRec2.FirstLeft = outRec1

      #fixup FirstLeft pointers that may need reassigning to OutRec1
      if m_UsingPolyTree) FixupFirstLefts2(outRec2, outRec1:




#------------------------------------------------------------------------------
# ClipperOffset support functions ...
#------------------------------------------------------------------------------

def GetUnitNormal(self, &pt1, &pt2):
  if(pt2.X == pt1.X and pt2.Y == pt1.Y) 
    return DoublePoint(0, 0)

  Dx = (double)(pt2.X - pt1.X)
  dy = (double)(pt2.Y - pt1.Y)
  f = 1 *1.0/ std.sqrt( Dx*Dx + dy*dy )
  Dx *= f
  dy *= f
  return DoublePoint(dy, -Dx)


#------------------------------------------------------------------------------
# ClipperOffset class
#------------------------------------------------------------------------------

ClipperOffset.ClipperOffset(double miterLimit, arcTolerance)
  self.MiterLimit = miterLimit
  self.ArcTolerance = arcTolerance
  m_lowest.X = -1

#------------------------------------------------------------------------------

ClipperOffset.~ClipperOffset()
  Clear()

#------------------------------------------------------------------------------

def Clear(self):
  for (i = 0; i < m_polyNodes.ChildCount(); ++i)
    delete m_polyNodes.Childs[i]
  m_polyNodes.Childs.clear()
  m_lowest.X = -1

#------------------------------------------------------------------------------

def AddPath(self, path, joinType, endType):
  highI = (int)path.size() - 1
  if (highI < 0) return
  newNode = PolyNode()
  newNode.m_jointype = joinType
  newNode.m_endtype = endType

  #strip duplicate points from path and also get index to the lowest point ...
  if endType == etClosedLine or endType == etClosedPolygon:
    while (highI > 0 and path[0] == path[highI]) highI--
  newNode.Contour.reserve(highI + 1)
  newNode.Contour.push_back(path[0])
  j = 0, k = 0
  for (i = 1; i <= highI; i++)
    if newNode.Contour[j] != path[i]:
      j++
      newNode.Contour.push_back(path[i])
      if (path[i].Y > newNode.Contour[k].Y or
        (path[i].Y == newNode.Contour[k].Y and
        path[i].X < newNode.Contour[k].X)) k = j

  if endType == etClosedPolygon and j < 2:
    delete newNode
    return

  m_polyNodes.AddChild(*newNode)

  #if self path's lowest pt is lower than all the others then update m_lowest
  if (endType != etClosedPolygon) return
  if m_lowest.X < 0:
    m_lowest = IntPoint(m_polyNodes.ChildCount() - 1, k)
  else:
    ip = m_polyNodes.Childs[(int)m_lowest.X].Contour[(int)m_lowest.Y]
    if (newNode.Contour[k].Y > ip.Y or
      (newNode.Contour[k].Y == ip.Y and
      newNode.Contour[k].X < ip.X))
      m_lowest = IntPoint(m_polyNodes.ChildCount() - 1, k)


#------------------------------------------------------------------------------

def AddPaths(self, paths, joinType, endType):
  for (i = 0; i < paths.size(); ++i)
    AddPath(paths[i], joinType, endType)

#------------------------------------------------------------------------------

def FixOrientations(self):
  #fixup orientations of all closed paths if the orientation of the
  #closed path with the lowermost vertex is wrong ...
  if (m_lowest.X >= 0 and 
    not Orientation(m_polyNodes.Childs[(int)m_lowest.X].Contour))
    for (i = 0; i < m_polyNodes.ChildCount(); ++i)
      node = *m_polyNodes.Childs[i]
      if (node.m_endtype == etClosedPolygon or
        (node.m_endtype == etClosedLine and Orientation(node.Contour)))
          ReversePath(node.Contour)

  } else:
    for (i = 0; i < m_polyNodes.ChildCount(); ++i)
      node = *m_polyNodes.Childs[i]
      if node.m_endtype == etClosedLine and not Orientation(node.Contour):
        ReversePath(node.Contour)



#------------------------------------------------------------------------------

def Execute(self, solution, delta):
  solution.clear()
  FixOrientations()
  DoOffset(delta)
  
  #now clean up 'corners' ...
  Clipper clpr
  clpr.AddPaths(m_destPolys, ptSubject, True)
  if delta > 0:
    clpr.Execute(ctUnion, solution, pftPositive, pftPositive)

  else:
    r = clpr.GetBounds()
    Path outer(4)
    outer[0] = IntPoint(r.left - 10, r.bottom + 10)
    outer[1] = IntPoint(r.right + 10, r.bottom + 10)
    outer[2] = IntPoint(r.right + 10, r.top - 10)
    outer[3] = IntPoint(r.left - 10, r.top - 10)

    clpr.AddPath(outer, ptSubject, True)
    clpr.ReverseSolution(True)
    clpr.Execute(ctUnion, solution, pftNegative, pftNegative)
    if solution.size() > 0) solution.erase(solution.begin():


#------------------------------------------------------------------------------

def Execute(self, solution, delta):
  solution.Clear()
  FixOrientations()
  DoOffset(delta)

  #now clean up 'corners' ...
  Clipper clpr
  clpr.AddPaths(m_destPolys, ptSubject, True)
  if delta > 0:
    clpr.Execute(ctUnion, solution, pftPositive, pftPositive)

  else:
    r = clpr.GetBounds()
    Path outer(4)
    outer[0] = IntPoint(r.left - 10, r.bottom + 10)
    outer[1] = IntPoint(r.right + 10, r.bottom + 10)
    outer[2] = IntPoint(r.right + 10, r.top - 10)
    outer[3] = IntPoint(r.left - 10, r.top - 10)

    clpr.AddPath(outer, ptSubject, True)
    clpr.ReverseSolution(True)
    clpr.Execute(ctUnion, solution, pftNegative, pftNegative)
    #remove the outer PolyNode rectangle ...
    if solution.ChildCount() == 1 and solution.Childs[0].ChildCount() > 0:
      outerNode = solution.Childs[0]
      solution.Childs.reserve(outerNode.ChildCount())
      solution.Childs[0] = outerNode.Childs[0]
      for (i = 1; i < outerNode.ChildCount(); ++i)
        solution.AddChild(*outerNode.Childs[i])

    else:
      solution.Clear()


#------------------------------------------------------------------------------

def DoOffset(self, delta):
  m_destPolys.clear()
  m_delta = delta

  #if Zero offset, copy any CLOSED polygons to m_p and return ...
  if (NEAR_ZERO(delta)) 
    m_destPolys.reserve(m_polyNodes.ChildCount())
    for (i = 0; i < m_polyNodes.ChildCount(); i++)
      node = *m_polyNodes.Childs[i]
      if node.m_endtype == etClosedPolygon:
        m_destPolys.push_back(node.Contour)

    return


  #see offset_triginometry3.svg in the documentation folder ...
  if MiterLimit > 2) m_miterLim = 2/(MiterLimit * MiterLimit:
  m_miterLim = 0.5

  double y
  if (ArcTolerance <= 0.0) y = def_arc_tolerance
  elif (ArcTolerance > std.fabs(delta) * def_arc_tolerance) 
    y = std.fabs(delta) * def_arc_tolerance
  y = ArcTolerance
  #see offset_triginometry2.svg in the documentation folder ...
  steps = pi / std.acos(1 - y / std.fabs(delta))
  if (steps > std.fabs(delta) * pi) 
    steps = std.fabs(delta) * pi;  #ie excessive precision check
  m_sin = std.sin(two_pi / steps)
  m_cos = std.cos(two_pi / steps)
  m_StepsPerRad = steps / two_pi
  if (delta < 0.0) m_sin = -m_sin

  m_destPolys.reserve(m_polyNodes.ChildCount() * 2)
  for (i = 0; i < m_polyNodes.ChildCount(); i++)
    node = *m_polyNodes.Childs[i]
    m_srcPoly = node.Contour

    len = (int)m_srcPoly.size()
    if len == 0 or (delta <= 0 and (len < 3 or node.m_endtype != etClosedPolygon)):
        continue

    m_destPoly.clear()
    if len == 1:
      if node.m_jointype == jtRound:
        X = 1.0, Y = 0.0
        for (j = 1; j <= steps; j++)
          m_destPoly.push_back(IntPoint(
            Round(m_srcPoly[0].X + X * delta),
            Round(m_srcPoly[0].Y + Y * delta)))
          X2 = X
          X = X * m_cos - m_sin * Y
          Y = X2 * m_sin + Y * m_cos


      else:
        X = -1.0, Y = -1.0
        for (j = 0; j < 4; ++j)
          m_destPoly.push_back(IntPoint(
            Round(m_srcPoly[0].X + X * delta),
            Round(m_srcPoly[0].Y + Y * delta)))
          if (X < 0) X = 1
          elif (Y < 0) Y = 1
          X = -1


      m_destPolys.push_back(m_destPoly)
      continue

    #build m_normals ...
    m_normals.clear()
    m_normals.reserve(len)
    for (j = 0; j < len - 1; ++j)
      m_normals.push_back(GetUnitNormal(m_srcPoly[j], m_srcPoly[j + 1]))
    if node.m_endtype == etClosedLine or node.m_endtype == etClosedPolygon:
      m_normals.push_back(GetUnitNormal(m_srcPoly[len - 1], m_srcPoly[0]))
    else:
      m_normals.push_back(DoublePoint(m_normals[len - 2]))

    if node.m_endtype == etClosedPolygon:
      k = len - 1
      for (j = 0; j < len; ++j)
        OffsetPoint(j, k, node.m_jointype)
      m_destPolys.push_back(m_destPoly)

    elif node.m_endtype == etClosedLine:
      k = len - 1
      for (j = 0; j < len; ++j)
        OffsetPoint(j, k, node.m_jointype)
      m_destPolys.push_back(m_destPoly)
      m_destPoly.clear()
      #re-build m_normals ...
      n = m_normals[len -1]
      for (j = len - 1; j > 0; j--)
        m_normals[j] = DoublePoint(-m_normals[j - 1].X, -m_normals[j - 1].Y)
      m_normals[0] = DoublePoint(-n.X, -n.Y)
      k = 0
      for (j = len - 1; j >= 0; j--)
        OffsetPoint(j, k, node.m_jointype)
      m_destPolys.push_back(m_destPoly)

    else:
      k = 0
      for (j = 1; j < len - 1; ++j)
        OffsetPoint(j, k, node.m_jointype)

      IntPoint pt1
      if node.m_endtype == etOpenButt:
        j = len - 1
        pt1 = IntPoint((cInt)Round(m_srcPoly[j].X + m_normals[j].X *
          delta), (cInt)Round(m_srcPoly[j].Y + m_normals[j].Y * delta))
        m_destPoly.push_back(pt1)
        pt1 = IntPoint((cInt)Round(m_srcPoly[j].X - m_normals[j].X *
          delta), (cInt)Round(m_srcPoly[j].Y - m_normals[j].Y * delta))
        m_destPoly.push_back(pt1)

      else:
        j = len - 1
        k = len - 2
        m_sinA = 0
        m_normals[j] = DoublePoint(-m_normals[j].X, -m_normals[j].Y)
        if node.m_endtype == etOpenSquare:
          DoSquare(j, k)
        else:
          DoRound(j, k)


      #re-build m_normals ...
      for (j = len - 1; j > 0; j--)
        m_normals[j] = DoublePoint(-m_normals[j - 1].X, -m_normals[j - 1].Y)
      m_normals[0] = DoublePoint(-m_normals[1].X, -m_normals[1].Y)

      k = len - 1
      for (j = k - 1; j > 0; --j) OffsetPoint(j, k, node.m_jointype)

      if node.m_endtype == etOpenButt:
        pt1 = IntPoint((cInt)Round(m_srcPoly[0].X - m_normals[0].X * delta),
          (cInt)Round(m_srcPoly[0].Y - m_normals[0].Y * delta))
        m_destPoly.push_back(pt1)
        pt1 = IntPoint((cInt)Round(m_srcPoly[0].X + m_normals[0].X * delta),
          (cInt)Round(m_srcPoly[0].Y + m_normals[0].Y * delta))
        m_destPoly.push_back(pt1)

      else:
        k = 1
        m_sinA = 0
        if node.m_endtype == etOpenSquare:
          DoSquare(0, 1)
        else:
          DoRound(0, 1)

      m_destPolys.push_back(m_destPoly)



#------------------------------------------------------------------------------

def OffsetPoint(self, j, k, jointype):
  #cross product ...
  m_sinA = (m_normals[k].X * m_normals[j].Y - m_normals[j].X * m_normals[k].Y)
  if (std.fabs(m_sinA * m_delta) < 1.0) 
    #dot product ...
    cosA = (m_normals[k].X * m_normals[j].X + m_normals[j].Y * m_normals[k].Y ); 
    if (cosA > 0) # angle => 0 degrees
      m_destPoly.push_back(IntPoint(Round(m_srcPoly[j].X + m_normals[k].X * m_delta),
        Round(m_srcPoly[j].Y + m_normals[k].Y * m_delta)))
      return; 

    #else angle => 180 degrees   

  elif (m_sinA > 1.0) m_sinA = 1.0
  elif (m_sinA < -1.0) m_sinA = -1.0

  if m_sinA * m_delta < 0:
    m_destPoly.push_back(IntPoint(Round(m_srcPoly[j].X + m_normals[k].X * m_delta),
      Round(m_srcPoly[j].Y + m_normals[k].Y * m_delta)))
    m_destPoly.push_back(m_srcPoly[j])
    m_destPoly.push_back(IntPoint(Round(m_srcPoly[j].X + m_normals[j].X * m_delta),
      Round(m_srcPoly[j].Y + m_normals[j].Y * m_delta)))

  else:
    switch (jointype)
      case jtMiter:
          r = 1 + (m_normals[j].X * m_normals[k].X +
            m_normals[j].Y * m_normals[k].Y)
          if r >= m_miterLim) DoMiter(j, k, r); else DoSquare(j, k:
          break

      case jtSquare: DoSquare(j, k); break
      case jtRound: DoRound(j, k); break

  k = j

#------------------------------------------------------------------------------

def DoSquare(self, j, k):
  dx = std.tan(std.atan2(m_sinA,
      m_normals[k].X * m_normals[j].X + m_normals[k].Y * m_normals[j].Y) / 4)
  m_destPoly.push_back(IntPoint(
      Round(m_srcPoly[j].X + m_delta * (m_normals[k].X - m_normals[k].Y * dx)),
      Round(m_srcPoly[j].Y + m_delta * (m_normals[k].Y + m_normals[k].X * dx))))
  m_destPoly.push_back(IntPoint(
      Round(m_srcPoly[j].X + m_delta * (m_normals[j].X + m_normals[j].Y * dx)),
      Round(m_srcPoly[j].Y + m_delta * (m_normals[j].Y - m_normals[j].X * dx))))

#------------------------------------------------------------------------------

def DoMiter(self, j, k, r):
  q = m_delta / r
  m_destPoly.push_back(IntPoint(Round(m_srcPoly[j].X + (m_normals[k].X + m_normals[j].X) * q),
      Round(m_srcPoly[j].Y + (m_normals[k].Y + m_normals[j].Y) * q)))

#------------------------------------------------------------------------------

def DoRound(self, j, k):
  a = std.atan2(m_sinA,
  m_normals[k].X * m_normals[j].X + m_normals[k].Y * m_normals[j].Y)
  steps = (int)Round(m_StepsPerRad * std.fabs(a))

  X = m_normals[k].X, Y = m_normals[k].Y, X2
  for (i = 0; i < steps; ++i)
    m_destPoly.push_back(IntPoint(
        Round(m_srcPoly[j].X + X * m_delta),
        Round(m_srcPoly[j].Y + Y * m_delta)))
    X2 = X
    X = X * m_cos - m_sin * Y
    Y = X2 * m_sin + Y * m_cos

  m_destPoly.push_back(IntPoint(
  Round(m_srcPoly[j].X + m_normals[j].X * m_delta),
  Round(m_srcPoly[j].Y + m_normals[j].Y * m_delta)))


#------------------------------------------------------------------------------
# Miscellaneous public functions
#------------------------------------------------------------------------------

def DoSimplePolygons(self):
  i = 0
  while (i < m_PolyOuts.size()) 
    outrec = m_PolyOuts[i++]
    op = outrec.Pts
    if (not op) continue
    do #for each Pt in Polygon until duplicate found do ...
      op2 = op.Next
      while (op2 != outrec.Pts) 
        if ((op.Pt == op2.Pt) and op2.Next != op and op2.Prev != op) 
          #split the polygon into two ...
          op3 = op.Prev
          op4 = op2.Prev
          op.Prev = op4
          op4.Next = op
          op2.Prev = op3
          op3.Next = op2

          outrec.Pts = op
          outrec2 = CreateOutRec()
          outrec2.Pts = op2
          UpdateOutPtIdxs(*outrec2)
          if Poly2ContainsPoly1(outrec2.Pts, outrec.Pts):
            #OutRec2 is contained by OutRec1 ...
            outrec2.IsHole = not outrec.IsHole
            outrec2.FirstLeft = outrec

          else:
            if Poly2ContainsPoly1(outrec.Pts, outrec2.Pts):
            #OutRec1 is contained by OutRec2 ...
            outrec2.IsHole = outrec.IsHole
            outrec.IsHole = not outrec2.IsHole
            outrec2.FirstLeft = outrec.FirstLeft
            outrec.FirstLeft = outrec2
          } else:
            #the 2 polygons are separate ...
            outrec2.IsHole = outrec.IsHole
            outrec2.FirstLeft = outrec.FirstLeft

          op2 = op; #ie get ready for the Next iteration

        op2 = op2.Next

      op = op.Next

    while (op != outrec.Pts)


#------------------------------------------------------------------------------

def ReversePath(self, p):
  std.reverse(p.begin(), p.end())

#------------------------------------------------------------------------------

def ReversePaths(self, p):
  for (i = 0; i < p.size(); ++i)
    ReversePath(p[i])

#------------------------------------------------------------------------------

def SimplifyPolygon(self, &in_poly, &out_polys, fillType):
  Clipper c
  c.StrictlySimple(True)
  c.AddPath(in_poly, ptSubject, True)
  c.Execute(ctUnion, out_polys, fillType, fillType)

#------------------------------------------------------------------------------

def SimplifyPolygons(self, &in_polys, &out_polys, fillType):
  Clipper c
  c.StrictlySimple(True)
  c.AddPaths(in_polys, ptSubject, True)
  c.Execute(ctUnion, out_polys, fillType, fillType)

#------------------------------------------------------------------------------

def SimplifyPolygons(self, &polys, fillType):
  SimplifyPolygons(polys, polys, fillType)

#------------------------------------------------------------------------------

inline double DistanceSqrd( IntPoint& pt1, pt2)
  Dx = ((double)pt1.X - pt2.X)
  dy = ((double)pt1.Y - pt2.Y)
  return (Dx*Dx + dy*dy)

#------------------------------------------------------------------------------

double DistanceFromLineSqrd(
   IntPoint& pt, ln1, ln2)
  #The equation of a line in general form (Ax + By + C = 0)
  #given 2 points (x¹,y¹) & (x²,y²) is ...
  #(y¹ - y²)x + (x² - x¹)y + (y² - y¹)x¹ - (x² - x¹)y¹ = 0
  #A = (y¹ - y²); B = (x² - x¹); C = (y² - y¹)x¹ - (x² - x¹)y¹
  #perpendicular distance of point (x³,y³) = (Ax³ + By³ + C)/Sqrt(A² + B²)
  #see http:#en.wikipedia.org/wiki/Perpendicular_distance
  A = double(ln1.Y - ln2.Y)
  B = double(ln2.X - ln1.X)
  C = A * ln1.X  + B * ln1.Y
  C = A * pt.X + B * pt.Y - C
  return (C * C) / (A * A + B * B)

#---------------------------------------------------------------------------

bool SlopesNearCollinear( IntPoint& pt1, 
     IntPoint& pt2, pt3, distSqrd)
  #self function is more accurate when the point that's geometrically
  #between the other 2 points is the one that's tested for distance.
  #ie makes it more likely to pick up 'spikes' ...
	if Abs(pt1.X - pt2.X) > Abs(pt1.Y - pt2.Y):
    if (pt1.X > pt2.X) == (pt1.X < pt3.X):
      return DistanceFromLineSqrd(pt1, pt2, pt3) < distSqrd
    elif (pt2.X > pt1.X) == (pt2.X < pt3.X):
      return DistanceFromLineSqrd(pt2, pt1, pt3) < distSqrd
		else:
	    return DistanceFromLineSqrd(pt3, pt1, pt2) < distSqrd

	else:
    if (pt1.Y > pt2.Y) == (pt1.Y < pt3.Y):
      return DistanceFromLineSqrd(pt1, pt2, pt3) < distSqrd
    elif (pt2.Y > pt1.Y) == (pt2.Y < pt3.Y):
      return DistanceFromLineSqrd(pt2, pt1, pt3) < distSqrd
		else:
      return DistanceFromLineSqrd(pt3, pt1, pt2) < distSqrd


#------------------------------------------------------------------------------

def PointsAreClose(self, pt1, pt2, distSqrd):
    Dx = (double)pt1.X - pt2.X
    dy = (double)pt1.Y - pt2.Y
    return ((Dx * Dx) + (dy * dy) <= distSqrd)

#------------------------------------------------------------------------------

def ExcludeOp(self, op):
  result = op.Prev
  result.Next = op.Next
  op.Next.Prev = result
  result.Idx = 0
  return result

#------------------------------------------------------------------------------

def CleanPolygon(self, in_poly, out_poly, distance):
  #distance = proximity in units/pixels below which vertices
  #will be stripped. Default ~= sqrt(2).
  
  size = in_poly.size()
  
  if (size == 0) 
    out_poly.clear()
    return


  outPts = OutPt[size]
  for (i = 0; i < size; ++i)
    outPts[i].Pt = in_poly[i]
    outPts[i].Next = &outPts[(i + 1) % size]
    outPts[i].Next.Prev = &outPts[i]
    outPts[i].Idx = 0


  distSqrd = distance * distance
  op = &outPts[0]
  while (op.Idx == 0 and op.Next != op.Prev) 
    if PointsAreClose(op.Pt, op.Prev.Pt, distSqrd):
      op = ExcludeOp(op)
      size--
    } 
    elif PointsAreClose(op.Prev.Pt, op.Next.Pt, distSqrd):
      ExcludeOp(op.Next)
      op = ExcludeOp(op)
      size -= 2

    elif SlopesNearCollinear(op.Prev.Pt, op.Pt, op.Next.Pt, distSqrd):
      op = ExcludeOp(op)
      size--

    else:
      op.Idx = 1
      op = op.Next



  if (size < 3) size = 0
  out_poly.resize(size)
  for (i = 0; i < size; ++i)
    out_poly[i] = op.Pt
    op = op.Next

  delete [] outPts

#------------------------------------------------------------------------------

def CleanPolygon(self, poly, distance):
  CleanPolygon(poly, poly, distance)

#------------------------------------------------------------------------------

def CleanPolygons(self, in_polys, out_polys, distance):
  for (i = 0; i < in_polys.size(); ++i)
    CleanPolygon(in_polys[i], out_polys[i], distance)

#------------------------------------------------------------------------------

def CleanPolygons(self, polys, distance):
  CleanPolygons(polys, polys, distance)

#------------------------------------------------------------------------------

void Minkowski( Path& poly, path, 
  Paths& solution, isSum, isClosed)
  delta = (isClosed ? 1 : 0)
  polyCnt = poly.size()
  pathCnt = path.size()
  Paths pp
  pp.reserve(pathCnt)
  if isSum:
    for (i = 0; i < pathCnt; ++i)
      Path p
      p.reserve(polyCnt)
      for (j = 0; j < poly.size(); ++j)
        p.push_back(IntPoint(path[i].X + poly[j].X, path[i].Y + poly[j].Y))
      pp.push_back(p)

  else:
    for (i = 0; i < pathCnt; ++i)
      Path p
      p.reserve(polyCnt)
      for (j = 0; j < poly.size(); ++j)
        p.push_back(IntPoint(path[i].X - poly[j].X, path[i].Y - poly[j].Y))
      pp.push_back(p)


  solution.clear()
  solution.reserve((pathCnt + delta) * (polyCnt + 1))
  for (i = 0; i < pathCnt - 1 + delta; ++i)
    for (j = 0; j < polyCnt; ++j)
      Path quad
      quad.reserve(4)
      quad.push_back(pp[i % pathCnt][j % polyCnt])
      quad.push_back(pp[(i + 1) % pathCnt][j % polyCnt])
      quad.push_back(pp[(i + 1) % pathCnt][(j + 1) % polyCnt])
      quad.push_back(pp[i % pathCnt][(j + 1) % polyCnt])
      if not Orientation(quad)) ReversePath(quad:
      solution.push_back(quad)


#------------------------------------------------------------------------------

def MinkowskiSum(self, pattern, path, solution, pathIsClosed):
  Minkowski(pattern, path, solution, True, pathIsClosed)
  Clipper c
  c.AddPaths(solution, ptSubject, True)
  c.Execute(ctUnion, solution, pftNonZero, pftNonZero)

#------------------------------------------------------------------------------

void TranslatePath( Path& input, output, delta) 
  #precondition: input != output
  output.resize(input.size())
  for (i = 0; i < input.size(); ++i)
    output[i] = IntPoint(input[i].X + delta.X, input[i].Y + delta.Y)

#------------------------------------------------------------------------------

def MinkowskiSum(self, pattern, paths, solution, pathIsClosed):
  Clipper c
  for (i = 0; i < paths.size(); ++i)
    Paths tmp
    Minkowski(pattern, paths[i], tmp, True, pathIsClosed)
    c.AddPaths(tmp, ptSubject, True)
    if pathIsClosed:
      Path tmp2
      TranslatePath(paths[i], tmp2, pattern[0])
      c.AddPath(tmp2, ptClip, True)


    c.Execute(ctUnion, solution, pftNonZero, pftNonZero)

#------------------------------------------------------------------------------

def MinkowskiDiff(self, poly1, poly2, solution):
  Minkowski(poly1, poly2, solution, False, True)
  Clipper c
  c.AddPaths(solution, ptSubject, True)
  c.Execute(ctUnion, solution, pftNonZero, pftNonZero)

#------------------------------------------------------------------------------

enum NodeType {ntAny, ntOpen, ntClosed

def AddPolyNodeToPolygons(self, polynode, nodetype, paths):
  match = True
  if nodetype == ntClosed) match = not polynode.IsOpen(:
  elif (nodetype == ntOpen) return

  if not polynode.Contour.empty() and match:
    paths.push_back(polynode.Contour)
  for (i = 0; i < polynode.ChildCount(); ++i)
    AddPolyNodeToPolygons(*polynode.Childs[i], nodetype, paths)

#------------------------------------------------------------------------------

def PolyTreeToPaths(self, polytree, paths):
  paths.resize(0); 
  paths.reserve(polytree.Total())
  AddPolyNodeToPolygons(polytree, ntAny, paths)

#------------------------------------------------------------------------------

def ClosedPathsFromPolyTree(self, polytree, paths):
  paths.resize(0); 
  paths.reserve(polytree.Total())
  AddPolyNodeToPolygons(polytree, ntClosed, paths)

#------------------------------------------------------------------------------

def OpenPathsFromPolyTree(self, polytree, paths):
  paths.resize(0); 
  paths.reserve(polytree.Total())
  #Open paths are top level only, so ...
  for (i = 0; i < polytree.ChildCount(); ++i)
    if polytree.Childs[i].IsOpen():
      paths.push_back(polytree.Childs[i].Contour)

#------------------------------------------------------------------------------

std.ostream& operator <<(std.ostream &s, &p)
  s << "(" << p.X << "," << p.Y << ")"
  return s

#------------------------------------------------------------------------------

std.ostream& operator <<(std.ostream &s, &p)
  if (p.empty()) return s
  last = p.size() -1
  for (i = 0; i < last; i++)
    s << "(" << p[i].X << "," << p[i].Y << "), "
  s << "(" << p[last].X << "," << p[last].Y << ")\n"
  return s

#------------------------------------------------------------------------------

std.ostream& operator <<(std.ostream &s, &p)
  for (i = 0; i < p.size(); i++)
    s << p[i]
  s << "\n"
  return s

#------------------------------------------------------------------------------

#ifdef use_deprecated

void OffsetPaths( Paths &in_polys, &out_polys,
  double delta, jointype, endtype, limit)
  ClipperOffset co(limit, limit)
  co.AddPaths(in_polys, jointype, (EndType)endtype); 
  co.Execute(out_polys, delta)

#------------------------------------------------------------------------------

#endif


} #ClipperLib namespace
