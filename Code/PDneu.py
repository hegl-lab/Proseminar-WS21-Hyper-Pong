from color import Color, NoFill
from array import array
from math import pi, atan2
import numpy as np
import drawSvg as svg

def isNearZero(z, eps : float = 1.0e-8):
    return (abs(z) < eps)

def isApproxReal(z, eps : float = 1.0e-8):
    if type(z) is int or type(z) is float:
        return True
    if type(z) is complex:
        return (abs(z.imag) < eps)
    elif type(z) is PDPoint:
        return (abs(z.getImagPart()) < eps)
    else:
        raise TypeError("Cannot check if an object of type '{}' is approximatly a real number.".format(type(z)))

def arg(z):
    if type(z) is int or type(z) is float:
        return 0.0
    if type(z) is complex:
        return atan2(z.imag, z.real)
    elif type(z) is PDPoint:
        return z.getArgument()
    else:
        raise TypeError("Cannot calculate argument of an object of type '{}'.".format(type(z)))

# symmetric == True:  returns phi % 2pi in [-pi, pi)
# symmetric == False: returns phi % 2pi in [0, 2*pi)
def mod2pi(phi : float, symmetric : bool = True):

    while phi >= 2*pi:
        phi -= 2*pi
    while phi < 0:
        phi += 2*pi

    if symmetric:
        if phi >= pi:
            phi -= 2*pi

    return phi

class PDObject:

    # Unique ID to be able to identify the object
    # self._uid : int

    def __init__(self):
        self._uid = None

    # returns self._id
    def getID(self):
        if self._uid == None:
            raise TypeError("The ID of the point was not set yet.")
        else:
            return self._uid

    # sets self._uid to uid
    def setID(self, uid : int):
        self._uid

class PDPoint(PDObject):

    # Member variables

    # self._point : complex

    # self._radius : float
    # self._argument : float

    # self._color : Color
    # self._size : float

    def __init__(self, point : complex, color : Color = Color(), size : float = 0.01):

        self._point = point

        self._radius = abs(point)
        self._argument = arg(point)

        self._color = color
        self._size = size

    def __eq__(self, other):
        if type(other) is complex:
            return isNearZero(abs(self._point - other))
        elif type(other) is PDPoint:
            return isNearZero(abs(self._point - other.getComplex()))
        else:
            raise TypeError("Cannot compare an object of type '{}' with an object of type 'PDPoint'.".format(type(other)))

    def __add__(self, other):
        if type(other) is complex:
            return PDPoint(self._point + other)
        elif type(other) is PDPoint:
            return PDPoint(self._point + other.getComplex())
        else:
            raise TypeError("Cannot add an object of type '{}' to an object of type 'PDPoint'.".format(type(other)))

    def __sub__(self, other):
        if type(other) is complex:
            return PDPoint(self._point - other)
        elif type(other) is PDPoint:
            return PDPoint(self._point - other.getComplex())
        else:
            raise TypeError("Cannot subtract an object of type '{}' from an object of type 'PDPoint'.".format(type(other)))

    def __mul__(self, other):
        if type(other) is complex or type(other) is float or type(other) is int:
            return PDPoint(self._point * other)
        elif type(other) is PDPoint:
            return PDPoint(self._point * other.getComplex())
        else:
            raise TypeError("Cannot multiply an object of type '{}' with an object of type 'PDPoint'.".format(type(other)))

    def __truediv__(self, other):
        if type(other) is complex or type(other) is float or type(other) is int:
            return PDPoint(self._point / other)
        elif type(other) is PDPoint:
            return PDPoint(self._point / other.getComplex())
        else:
            raise TypeError("Cannot divide an object of type 'PDPoint' by an object of type '{}'.".format(type(other)))

    def __abs__(self):
        return abs(self._point)

    ###############################################
    # TODO

    # Calculates inverson at unit circle
    def getInversion(self):
        if self.isZero():
            raise ArithmeticError("Cannot invert point 0+0j.")
        else:
            return PDPoint(self._point/abs(self._point)**2)

    # Normalizes the point (returns point with same argument but radius = 1)
    def getNormalization(self):
        if self.isZero():
            raise ArithmeticError("Cannot normalize point 0+0j.")
        else:
            return PDPoint(self._point/abs(self._point))

    #
    ###############################################

    def getRealPart(self):
        return self._point.real

    def getImagPart(self):
        return self._point.imag

    def getCartesic(self):
        return self.getRealPart(), self.getImagPart()

    def getComplex(self):
        return self._point

    def getRadius(self):
        return self._radius

    def getArgument(self):
        return self._argument

    def getPolar(self):
        return self.getRadius(), self.getArgument()

    def isIdeal(self):
        return isNearZero(abs(1.0 - self._radius))

    def isZero(self):
        return isNearZero(self._radius)

    def isOnPD(self):
        return (self._radius <= 1.0 or self.isIdeal())

    def conjugate(self):
        return PDPoint(self._point.conjugate())

class PDGeodesic(PDObject):

     #Member variables

    #self._point1 : PDPoint
    #self._point2 : PDPoint

    #self._isArc : bool
    #self._center : PDPoint #[0+0j if diameter]
    #self._radius : float #[0 if diameter]

    #self._width : float #(0...inf)
    #self._edge_color : Color
    #self._fill_color : Color

    def __init__(self, point1 : PDPoint, point2 : PDPoint, edge_color : Color = Color(), fill_color : Color = NoFill, width : float = 0.0):

        if point1 == point2:
            raise ValueError("Points for defining a geodesic cannot be equal.")

        if width < 0:
            raise ValueError("Width of geodesic cannot be negative.")

        self._point1 = point1
        self._point2 = point2

        self._width = width
        self._edge_color = edge_color
        self._fill_color = fill_color

        self.__calculate()
        self.__isdiameter()

    ###############################################
    # TODO
    def __isdiameter(self):
        if self._point1.isZero()== True or isApproxReal(self._point2 / self._point1)==True: return True
        else: return False

    def __calculate(self):


        # When is the geodesic a diameter?
        # Tip: Use the value point2 / point1 and isApproxReal() for a criterion

            if self.__isdiameter():
                self._isArc = False
                self._center = PDPoint(0+0j)
                self._radius = 0.0
            else:

                self._isArc = True

            # see: https://en.wikipedia.org/wiki/Poincar%C3%A9_disk_model#Lines

                P = self._point1
                Q = self._point2

                Pinv = P.getInversion()
                Qinv = Q.getInversion()

                M = (P + Pinv) * 0.5
                N = (Q + Qinv) * 0.5

            # calculate normalized direction "vectors" of the perpendiculars
                m_dir = (Pinv - P).getNormalization() * 1j
                n_dir = (Qinv -Q).getNormalization() *1j

            # find intersection of m : M + m_dir * t and n : N + n_dir * s
            # Tip: isomorphism a+ib <--> (a,b)
            # (solve the linear equation system [2x2])

                X=N-M
                t=(-n_dir.getImagPart()*X.getRealPart()+n_dir.getRealPart()*X.getImagPart())/(-n_dir.getImagPart()*m_dir.getRealPart()+n_dir.getRealPart()*m_dir.getImagPart())

         #(1/(m_dir.getRealPart()*(-n_dir.getImagPart())-(-n_dir.getRealPart())*m_dir.getImagPart()))*array([(-n_dir.getImagPart())*X.getRealPart()+n_dir.getRealPart()*X.getImagPart()],[(-m_dir.getImagPart())*X.getRealPart()+m_dir.getRealPart()*X.getImagPart()])
            #FIX THIS: t =1.0/mdir.getImagePart()n_dir.getRealPart()

                self._center = M + m_dir * t
                self._radius = abs(P - self._center)
                #print(self._center)
                #print(self._radius)


    ###############################################

    def addToSVGDrawing(self, drawing : svg.Drawing):
        if isNearZero(self._width, 0.01):
            if self._isArc:
                c = self._center
                p1 = self._point1
                p2 = self._point2

                cx = c.getRealPart()
                cy = c.getImagPart()

                r = self._radius

                angle1 = mod2pi(arg((p1 - c)), symmetric = False) / (2.0*pi) * 360.0
                angle2 = mod2pi(arg((p2 - c)), symmetric = False) / (2.0*pi) * 360.0

                 #magic :)
                if ( (p2-c) * (p1-c).conjugate() ).getImagPart() < 0:
                    angle1, angle2 = angle2, angle1

                drawing.append(svg.ArcLine(cx, cy, r, -angle1, -angle2, stroke = self._edge_color.getColor(), stroke_width = 0.01, fill = self._fill_color.getColor()))

            else:
                sx = self._point1.getRealPart()
                sy = self._point1.getImagPart()

                ex = self._point2.getRealPart()
                ey = self._point2.getImagPart()

                drawing.append(svg.Line(sx, sy, ex, ey, stroke = self._edge_color.getColor(), stroke_width = 0.01, fill = self._fill_color.getColor()))
