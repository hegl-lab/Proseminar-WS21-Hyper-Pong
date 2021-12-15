import cmath
from sympy import *
import numpy as np
import scipy.optimize as opt
import pygame


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

# represents the point of the current intersection point with one of the walls
solution_x = 0
solution_y = 0

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

def newballpos(center_x, center_y, radius, t):
    newballpos = [center_x + radius*cos(2*pi*t), center_y + radius*sin(2*pi*t)]
    return newballpos

#helppoint not done because it doesnt keep in mind the orthogonal of the wall
def helppoint(solution_x, solution_y, center_x, center_y):
    global helppoint_x, helppoint_y

    n = (center_y - solution_y)/(center_x - solution_x)
    m = 1/n
    k = solution_y - m*solution_x
    if center_x == walldowncenter_x and center_y == walldowncenter_y :
        helppoint_y = -0.5
        helppoint_x = (-0.5-k)/m - 0.2
    elif center_x == wallupcenter_x and center_y == wallupcenter_y :
            helppoint_y = 0.5
            helppoint_x = (0.5-k)/m + 0.2
    elif center_x == wallplayer1center_x and center_y == wallplayer1center_y :
            helppoint_x = -0.5
            helppoint_y = (-0.5-k)/m + 0.2
    elif center_x == wallplayer2center_x and center_y == wallplayer2center_y :
            helppoint_x = 0.5
            helppoint_y = (0.5-k)/m - 0.2

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

#function to change current ballgeodesic
def ballgeodesic(wall):
    global ballgeodesiccenter_x, ballgeodesiccenter_y
    #see numeration of walls
    if wall == 1:
        helppoint(solution_x, solution_y, wallupcenter_x, wallupcenter_y)
        center = opt.fsolve(findcenter, (1,0.1))
        ballgeodesiccenter_x = center[0]
        ballgeodesiccenter_y = center[1]
        wall = 2
    elif wall == 2:
        helppoint(solution_x, solution_y, wallplayer2center_x, wallplayer2center_y)
        center = opt.fsolve(findcenter, (0.1,-1))
        ballgeodesiccenter_x = center[0]
        ballgeodesiccenter_y = center[1]
        #wall = 3
    elif wall == 3:
        helppoint(solution_x, solution_y, walldowncenter_x, walldowncenter_y)
        center = opt.fsolve(findcenter, (-1,0.1))
        ballgeodesiccenter_x = center[0]
        ballgeodesiccenter_y = center[1]
        wall = 4
    elif wall == 4:
        helppoint(solution_x, solution_y, wallplayer1center_x, wallplayer1center_y)
        center = opt.fsolve(findcenter, (0.1,1))
        ballgeodesiccenter_x = center[0]
        ballgeodesiccenter_y = center[1]
        wall = 1
    else:
        print("ERROR input must be in the set of {1,2,3,4}")

def ball_radius(x,y):
    if sqrt((x - 401)**2 + (y- 401)**2) >= 300:
        return 0
    else:
        return round(15-(15*sqrt((x - 401)**2 + (y- 401)**2))/300)

solution = opt.fsolve(wallplayer2intersection, (0.1,1) )
nextintersection = topygamecoords(solution[0], solution[1])
wall = 2 #variable to what wall the ball moves

# initialising pygame
pygame.init()
#pygame.mixer.init()
#add sound
#sound = pygame.mixer.Sound('meow.mp3')

# colours used
orange  = ( 200, 140, 0)
red     = ( 153, 0, 0)
green   = ( 0, 153, 0)
blue = ( 0, 0, 153)
black = ( 0, 0, 0)
white   = ( 255, 255, 255)

width = 801
height = 801

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
#ballradius = 10

# loop of main programm
while gameactive:
    # check if an action has taken place
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameactive = False

    # integrate game logic here
    helpballpos = newballpos(ballgeodesiccenter_x, ballgeodesiccenter_y, ballgeodesicradius, movement)
    movement += direction * 0.001
    ballpos = topygamecoords(helpballpos[0], helpballpos[1])
    ballradius = ball_radius(ballpos[0], ballpos[1])

    if wall == 1 and ballpos[1] - ballradius <= nextintersection[1]:
        #ballgeodesic(wall)
        #sound.play()
        solution = opt.fsolve(wallplayer2intersection, (0.1,1))
        nextintersection = topygamecoords(solution[0],solution[1])
        wall = 2
        direction = direction * -1
    elif wall ==2 and ballpos[0] + ballradius >= nextintersection[0]:
        #ballgeodesic(wall)
        #sound.play()
        solution = opt.fsolve(wallupintersection, (0.1,1))
        nextintersection = topygamecoords(solution[0],solution[1])
        wall = 1
        direction = direction * -1
    elif wall == 3 and ballpos[1] - ballradius >= nextintersection[1]:
        ballgeodesic(wall)
        nextintersection1 = opt.fsolve(wallplayer1intersection, (0.1,1))
        wall = 4
        direction = direction * -1
    elif wall == 4 and ballpos[0] - ballradius <= nextintersection1[0]:
        ballgeodesic(wall)
        nextintersection1 = opt.fsolve(walldownintersection, (0.1,1))
        wall = 1
        direction = direction * -1



    # delete gamefield
    screen.fill(black)

    # draw gamefield and figures
    pygame.draw.circle(screen, orange, [401,401],300)
    pygame.draw.circle(screen, green,[topygamecoords(0,1.75)[0],topygamecoords(0,1.75)[1]],topygameradius(wallradius),5)
    pygame.draw.circle(screen, green,[topygamecoords(0,-1.75)[0],topygamecoords(0,-1.75)[1]],topygameradius(wallradius),5)
    pygame.draw.circle(screen, red,[topygamecoords(-1.75,0)[0],topygamecoords(-1.75,0)[1]],topygameradius(wallradius),5)
    pygame.draw.circle(screen, blue,[topygamecoords(1.75,0)[0],topygamecoords(1.75,0)[1]],topygameradius(wallradius),5)
    pygame.draw.circle(screen, ball_colour, [ballpos[0], ballpos[1]], ballradius)


    # refresh Window
    pygame.display.flip()

    # set refreshing time
    clock.tick(60)#normal 60

pygame.quit()
quit()
