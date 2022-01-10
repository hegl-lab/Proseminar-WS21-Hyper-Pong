import cmath
from sympy import *
import numpy as np
import scipy.optimize as opt
import pygame
import warnings
from PDneu import *

# initialising pygame
pygame.init()
#pygame.mixer.init()
#add sound
#sound = pygame.mixer.Sound('meow.mp3')

# colors used 
orange  = ( 200, 140, 0)
red     = ( 153, 0, 0)
green   = ( 0, 153, 0)
blue = ( 0, 0, 153)
black = ( 0, 0, 0)
white   = ( 255, 255, 255)

width = 801
height = 801

#keeps track of the scores
score_value_player1 = 0
score_value_player2 = 0
font = pygame.font.Font('freesansbold.ttf', 32)

# open window
screen = pygame.display.set_mode((width, height))

# title
pygame.display.set_caption("Ping Pong")

# solange die Variable True ist, soll das Spiel laufen
gameactive = True

# Bildschirm Aktualisierungen einstellen
clock = pygame.time.Clock()

ball_colour = white
movement = 0.5
direction = 1

#1 (see def ballgeodesic)
wallupcenter_x = 0
wallupcenter_y = 1.75

#2
wallplayer2center_x = 1.75
wallplayer2center_y= 0

#3
walldowncenter_x = 0
walldowncenter_y = -1.75

#4
wallplayer1center_x = -1.75
wallplayer1center_y = 0

wallradius = sqrt(1.7)

#Creating first geodesic
ballgeodesiccenter_x = 1
ballgeodesiccenter_y = 1
ballgeodesicradius = sqrt(1.5)

#needed to find next ballgeodesic
helppoint_x = 0
helppoint_y = 0

def distance(z0,z1):
    distance = cmath.acosh(1+2*(abs(z0-z1)**2)/((1-abs(z0)**2)*(1-abs(z1)**2)))
    return distance

def findcenter(variables):
    (x,y) = variables

    eq1 = (solution_x-x)**2+(solution_y-y)**2 - ballgeodesicradius**2
    eq2 = (helppoint_x-x)**2+(helppoint_y-y)**2 - ballgeodesicradius**2
    return [eq1, eq2]

#function to calculate pygame coordinates into normal coordinates
def topygamecoords(xcord, ycord):
    point = [round(401 + xcord*300), round(401 - ycord*300)]
    return point

def topygameradius(radius):
    return 300*radius

def xy_to_PD(x,y):
    z = PDPoint(complex(x,y))
    return(z)

def PD_to_xy(point):
    x = point.getReal()
    y = point.getImag()
    return((x,y))

def newballpos(center_x, center_y, radius, t):
    newballpos = [center_x + radius*cos(2*pi*t), center_y + radius*sin(2*pi*t)]
    return newballpos

def helptangent(variables):
    (x,y) = variables

    first_eq = (x - ballgeodesiccenter_x)**2 + (y-ballgeodesiccenter_y)**2 - ballgeodesicradius**2
    second_eq = m_tangent*x + b_tangent - y
    return [first_eq, second_eq]

#helppoint used to find next geodesic
def helppoint(solution_x, solution_y, center_x, center_y):
    global helppoint_x, helppoint_y, b_tangent, m_tangent
    if center_x - solution_x != 0 and center_y - solution_y != 0:
        n = (center_y - solution_y)/(center_x - solution_x) #orthogonal
        b_orthogonal = solution_y - n*solution_x
        m_tangent = 1/n #tangent
        if center_x == walldowncenter_x and center_y == walldowncenter_y :
            b_tangent = solution_y - m_tangent*solution_x + 0.1
            helpsolve = opt.fsolve(helptangent, (solution_x,solution_y))
            orthintersect_y = m_tangent*(b_orthogonal - b_tangent)/(m_tangent - n) + b_tangent
            orthintersect_x = (b_orthogonal - b_tangent)/(m_tangent - n)
            helppoint_y = 2*orthintersect_y - helpsolve[1]
            helppoint_x = 2*orthintersect_x - helpsolve[0]
        elif center_x == wallupcenter_x and center_y == wallupcenter_y :
            b_tangent = solution_y - m_tangent*solution_x - 0.1
            helpsolve = opt.fsolve(helptangent, (solution_x,solution_y))
            orthintersect_y = m_tangent*(b_orthogonal - b_tangent)/(m_tangent - n) + b_tangent
            orthintersect_x = (b_orthogonal - b_tangent)/(m_tangent - n)
            helppoint_y = 2*orthintersect_y - helpsolve[1]
            helppoint_x = 2*orthintersect_x - helpsolve[0]
        elif center_x == wallplayer1center_x and center_y == wallplayer1center_y :
            b_tangent = solution_y - m_tangent*solution_x - 0.1
            helpsolve = opt.fsolve(helptangent, (solution_x,solution_y))
            orthintersect_y = m_tangent*(b_orthogonal - b_tangent)/(m_tangent - n) + b_tangent
            orthintersect_x = (b_orthogonal - b_tangent)/(m_tangent - n)
            helppoint_y = 2*orthintersect_y - helpsolve[1]
            helppoint_x = 2*orthintersect_x - helpsolve[0]
        elif center_x == wallplayer2center_x and center_y == wallplayer2center_y :
            b_tangent = solution_y - m_tangent*solution_x + 0.1
            helpsolve = opt.fsolve(helptangent, (solution_x,solution_y))
            orthintersect_y = m_tangent*(b_orthogonal - b_tangent)/(m_tangent - n) + b_tangent
            orthintersect_x = (b_orthogonal - b_tangent)/(m_tangent - n)
            helppoint_y = 2*orthintersect_y - helpsolve[1]
            helppoint_x = 2*orthintersect_x - helpsolve[0]
    elif center_y - solution_y == 0:
            if center_x == wallplayer1center_x and center_y == wallplayer1center_y :
                helppoint_x = solution_x + 0.1
                helppoint_y = 2*(solution_y) - sqrt(ballgeodesicradius**2 - (solution_x + 0.1 - ballgeodesiccenter_x)**2) - ballgeodesiccenter_y
            elif center_x == wallplayer2center_x and center_y == wallplayer2center_y :
                helppoint_x = solution_x - 0.1
                helppoint_y = 2*(solution_y) - sqrt(ballgeodesicradius**2 - (solution_x - 0.1 - ballgeodesiccenter_x)**2) - ballgeodesiccenter_y
            else:
                print("Something went very wrong.")
    elif center_x - solution_x == 0:
                if center_x == walldowncenter_x and center_y == walldowncenter_y :
                    helppoint_y = solution_y + 0.1
                    helppoint_x = 2*(solution_x) - sqrt(ballgeodesicradius**2 - (solution_y + 0.1 - ballgeodesiccenter_y)**2) - ballgeodesiccenter_x
                elif center_x == wallupcenter_x and center_y == wallupcenter_y :
                    helppoint_y = solution_y - 0.1
                    helppoint_x = 2*(solution_x) - sqrt(ballgeodesicradius**2 - (solution_y + 0.1 - ballgeodesiccenter_y)**2) - ballgeodesiccenter_x
                else:
                    print("Something went very wrong.")

def wallupintersection(variables):
    (x,y) = variables

    first_eq = (x-wallupcenter_x)**2+(y-wallupcenter_y)**2 - wallradius**2
    second_eq = (x-ballgeodesiccenter_x)**2+(y-ballgeodesiccenter_y)**2 - ballgeodesicradius**2
    return [first_eq, second_eq]

def walldownintersection(variables):
    (x,y) = variables

    first_eq = (x-walldowncenter_x)**2+(y-walldowncenter_y)**2 - wallradius**2
    second_eq = (x-ballgeodesiccenter_x)**2+(y-ballgeodesiccenter_y)**2 - ballgeodesicradius**2
    return [first_eq, second_eq]

def wallplayer1intersection(variables):
    (x,y) = variables

    first_eq = (x-wallplayer1center_x)**2+(y-wallplayer1center_y)**2 - wallradius**2
    second_eq = (x-ballgeodesiccenter_x)**2+(y-ballgeodesiccenter_y)**2 - ballgeodesicradius**2
    return [first_eq, second_eq]

def wallplayer2intersection(variables):
    (x,y) = variables

    first_eq = (x-wallplayer2center_x)**2+(y-wallplayer2center_y)**2 - wallradius**2
    second_eq = (x-ballgeodesiccenter_x)**2+(y-ballgeodesiccenter_y)**2 - ballgeodesicradius**2
    return [first_eq, second_eq]

# represents the point of the current intersection point with one of the walls
solution = opt.fsolve(wallplayer2intersection, (0.1,1) )
oldsolution = solution
nextintersection = topygamecoords(solution[0], solution[1])
wall = 2 #variable to what wall the ball moves

#function to change current ballgeodesic
def ballgeodesic(wall):
    global ballgeodesiccenter_x, ballgeodesiccenter_y, ballgeodesicradius
    #see numeration of walls
    if wall == 1:
        helppoint(solution[0], solution[1], wallupcenter_x, wallupcenter_y)
        p1 = xy_to_PD(solution[0],solution[1])
        p2 = xy_to_PD(helppoint_x,helppoint_y)
        g = PDGeodesic(p1,p2)
        center = g._center.getComplex()
        ballgeodesiccenter_x = center.real
        ballgeodesiccenter_y = center.imag
        ballgeodesicradius = g._radius
        #wall = 2
    elif wall == 2:
        helppoint(solution[0], solution[1], wallplayer2center_x, wallplayer2center_y)
        p1 = xy_to_PD(solution[0],solution[1])
        p2 = xy_to_PD(helppoint_x,helppoint_y)
        g = PDGeodesic(p1,p2)
        center = g._center.getComplex()
        ballgeodesiccenter_x = center.real
        ballgeodesiccenter_y = center.imag
        print("Center:" , ballgeodesiccenter_x, " ", ballgeodesiccenter_y)
        ballgeodesicradius = g._radius
        print(g._radius)
        #wall = 3
    elif wall == 3:
        helppoint(solution[0], solution[1], walldowncenter_x, walldowncenter_y)
        p1 = xy_to_PD(solution[0],solution[1])
        p2 = xy_to_PD(helppoint_x,helppoint_y)
        g = PDGeodesic(p1,p2)
        center = g._center.getComplex()
        ballgeodesiccenter_x = center.real
        ballgeodesiccenter_y = center.imag
        ballgeodesicradius = g._radius
        #wall = 4
    elif wall == 4:
        helppoint(solution[0], solution[1], wallplayer1center_x, wallplayer1center_y)
        p1 = xy_to_PD(solution[0],solution[1])
        p2 = xy_to_PD(helppoint_x,helppoint_y)
        g = PDGeodesic(p1,p2)
        center = g._center.getComplex()
        ballgeodesiccenter_x = center.real
        ballgeodesiccenter_y = center.imag
        ballgeodesicradius = g._radius
        #wall = 1
    else:
        print("ERROR input must be in the set of {1,2,3,4}")

def ball_radius(x,y):
    if sqrt((x - 401)**2 + (y- 401)**2) >= 300:
        return 0
    else:
        return round(15-(15*sqrt((x - 401)**2 + (y- 401)**2))/300)

#we need to find the wall of the nextintersection
def findsolution():
    global wall, solution
    warnings.simplefilter('error', RuntimeWarning)
    lastwall = wall
    if lastwall == 1:
        try:
            wall = 2
            solution = opt.fsolve(wallplayer2intersection, (0.1,0.1))
            print("try")
        except RuntimeWarning:
            wall = 3
            soltion = opt.fsolve(walldownintersection, (0.1,0.1))
            print("except")
    elif lastwall == 2:
        try:
            wall = 3
            solution = opt.fsolve(walldownintersection, (0.1,0.1))
            print("try")
        except RuntimeWarning:
            wall = 4
            solution = opt.fsolve(wallplayer1intersection, (0.1,0.1))
            print("except")
    elif lastwall == 3:
        try:
            wall = 4
            solution = opt.fsolve(wallplayer1intersection, (0.1,0.1))
            print("try")
        except RuntimeWarning:
            wall = 1
            solution = opt.fsolve(wallupintersection, (0.1,0.1))
            print("except")
    elif lastwall == 4:
        try:
            wall = 1
            solution = opt.fsolve(wallupintersection, (0.1,0.1))
            print("try")
        except RuntimeWarning:
            wall = 2
            solution = opt.fsolve(wallplayer2intersection, (0.1,0.1))
            print("except")

def findnewmovement(variables):
    t = variables

    first_eq = oldsolution[0] - ballgeodesiccenter_x - ballgeodesicradius*cos(2*pi*t)
    second_eq = oldsolution[1] - ballgeodesiccenter_y - ballgeodesicradius*sin(2*pi*t)
    return [first_eq, second_eq]

def show_score(x, y):
    score = font.render(str(score_value_player1) + " : " + str(score_value_player2), True, (255, 255, 255))
    screen.blit(score, (x, y))

def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(over_text, (200, 250))

# loop of main programm
while gameactive:
    # check if an action has taken place
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameactive = False

    # integrate game logic here
    helpballpos = newballpos(ballgeodesiccenter_x, ballgeodesiccenter_y, ballgeodesicradius, movement)
    movement += 0.001
    ballpos = topygamecoords(helpballpos[0], helpballpos[1])
    ballradius = ball_radius(ballpos[0], ballpos[1])

    #Problem: movement needs to be switched so we need to find the fitting t of the new geodesic so they connect so findnewmovement needs to be fixed
    if wall == 1 and ballpos[1] - ballradius >= nextintersection[1]:
        ballgeodesic(wall)
        oldsolution = solution
        findsolution()
        #movement += opt.fsolve(findnewmovement, 0.1)
        nextintersection = topygamecoords(solution[0],solution[1])
        #sound.play()
    elif wall == 2 and ballpos[0] + ballradius >= nextintersection[0]:
        #sound.play()
        ballgeodesic(wall)
        oldsolution = solution
        findsolution()
        #movement += opt.fsolve(findnewmovement, 0.1)
        nextintersection = topygamecoords(solution[0],solution[1])
    elif wall == 3 and ballpos[1] - ballradius <= nextintersection[1]:
        ballgeodesic(wall)
        oldsolution = solution
        findsolution()
        #movement += opt.fsolve(findnewmovement, 0.1)
        nextintersection = topygamecoords(solution[0],solution[1])
    elif wall == 4 and ballpos[0] - ballradius <= nextintersection[0]:
        ballgeodesic(wall)
        oldsolution = solution
        findsolution()
        #movement += opt.fsolve(findnewmovement, 0.1)
        nextintersection = topygamecoords(solution[0],solution[1])

    # delete gamefield
    screen.fill(black)

    # draw gamefield and figures
    pygame.draw.circle(screen, orange, [401,401],300)
    pygame.draw.circle(screen, green,[topygamecoords(0,1.75)[0],topygamecoords(0,1.75)[1]],topygameradius(wallradius),5)
    pygame.draw.circle(screen, green,[topygamecoords(0,-1.75)[0],topygamecoords(0,-1.75)[1]],topygameradius(wallradius),5)
    pygame.draw.circle(screen, red,[topygamecoords(-1.75,0)[0],topygamecoords(-1.75,0)[1]],topygameradius(wallradius),5)
    pygame.draw.circle(screen, blue,[topygamecoords(1.75,0)[0],topygamecoords(1.75,0)[1]],topygameradius(wallradius),5)
    pygame.draw.circle(screen, ball_colour, [ballpos[0], ballpos[1]], ballradius)

    show_score(360, 10)
    # refresh Window
    pygame.display.update()

    # set refreshing time
    clock.tick(60)#normal 60

pygame.quit()
quit()
