import cmath
from sympy import *
import numpy as np
import scipy.optimize as opt
import pygame
import warnings
from PDneu import *

# initialising pygame
pygame.init()
pygame.mixer.init()
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
ballgeodesiccenter_x = 0
ballgeodesiccenter_y = 0
ballgeodesicradius = 0

#needed to find next ballgeodesic
helppoint_x = 0
helppoint_y = 0

# shows wether the ball will be reset or not
start = True

def distance(z0,z1):
    distance = cmath.acosh(1+2*(abs(z0-z1)**2)/((1-abs(z0)**2)*(1-abs(z1)**2)))
    return abs(distance)

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
    return (x,y)

def newballpos(center_x, center_y, radius, t):
    newballpos = [center_x + radius*cos(2*pi*t), center_y + radius*sin(2*pi*t)]
    return newballpos

def helptangent(variables):
    (x,y) = variables

    first_eq = (x - ballgeodesiccenter_x)**2 + (y-ballgeodesiccenter_y)**2 - ballgeodesicradius**2
    second_eq = m_tangent*x + b_tangent - y
    return [first_eq, second_eq]

#helppoint used to find next geodesic: Build perpendicular line to tangent of the circle trough intersection
#point of wall geodesic with old ball geodesic, move this tangent along the perpendicular and find helppoint as
#reflection of the intersection of tangent and old geodesic along the perpendicular.
def helppoint(solution_x, solution_y, center_x, center_y):
    global helppoint_x, helppoint_y, b_tangent, m_tangent
    if center_x - solution_x != 0 and center_y - solution_y != 0:
        n = (center_y - solution_y)/(center_x - solution_x) #orthogonal
        b_orthogonal = solution_y - n*solution_x
        m_tangent = 1/n #tangent

        if center_x == walldowncenter_x and center_y == walldowncenter_y :
            b_tangent = solution_y - m_tangent*solution_x + 0.001
        elif center_x == wallupcenter_x and center_y == wallupcenter_y :
            b_tangent = solution_y - m_tangent*solution_x - 0.001
        elif center_x == wallplayer1center_x and center_y == wallplayer1center_y :
            b_tangent = solution_y - m_tangent*solution_x - 0.001
        elif center_x == wallplayer2center_x and center_y == wallplayer2center_y :
            b_tangent = solution_y - m_tangent*solution_x + 0.001

        helpsolve = opt.fsolve(helptangent, (solution_x,solution_y))
        orthintersect_y = m_tangent*(b_orthogonal - b_tangent)/(m_tangent - n) + b_tangent
        orthintersect_x = (b_orthogonal - b_tangent)/(m_tangent - n)
        helppoint_y = 2*orthintersect_y - helpsolve[1]
        helppoint_x = 2*orthintersect_x - helpsolve[0]

    elif center_y - solution_y == 0:
            if center_x == wallplayer1center_x and center_y == wallplayer1center_y :
                helppoint_x = solution_x + 0.001
                helppoint_y = 2*(solution_y) - sqrt(ballgeodesicradius**2 - (solution_x + 0.001 - ballgeodesiccenter_x)**2) - ballgeodesiccenter_y
            elif center_x == wallplayer2center_x and center_y == wallplayer2center_y :
                helppoint_x = solution_x - 0.001
                helppoint_y = 2*(solution_y) - sqrt(ballgeodesicradius**2 - (solution_x - 0.001 - ballgeodesiccenter_x)**2) - ballgeodesiccenter_y
            else:
                print("Something went very wrong.")
    elif center_x - solution_x == 0:
            if center_x == walldowncenter_x and center_y == walldowncenter_y :
                helppoint_y = solution_y + 0.001
                helppoint_x = 2*(solution_x) - sqrt(ballgeodesicradius**2 - (solution_y + 0.001 - ballgeodesiccenter_y)**2) - ballgeodesiccenter_x
            elif center_x == wallupcenter_x and center_y == wallupcenter_y :
                helppoint_y = solution_y - 0.001
                helppoint_x = 2*(solution_x) - sqrt(ballgeodesicradius**2 - (solution_y + 0.001 - ballgeodesiccenter_y)**2) - ballgeodesiccenter_x
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

def newgeodesic():
    global ballgeodesiccenter_x, ballgeodesiccenter_y, ballgeodesicradius
    p1 = xy_to_PD(0.3, 0.4)
    p2 = xy_to_PD(0.45, 0.2)
    g = PDGeodesic(p1,p2)
    center = g._center.getComplex()
    ballgeodesiccenter_x = center.real
    ballgeodesiccenter_y = center.imag
    ballgeodesicradius = g._radius

#function to change current ballgeodesic
def ballgeodesic(wall):
    global ballgeodesiccenter_x, ballgeodesiccenter_y, ballgeodesicradius
    #see numeration of walls
    if wall == 1:
        helppoint(solution[0], solution[1], wallupcenter_x, wallupcenter_y)
        #wall = 2
    elif wall == 2:
        helppoint(solution[0], solution[1], wallplayer2center_x, wallplayer2center_y)
        #wall = 3
    elif wall == 3:
        helppoint(solution[0], solution[1], walldowncenter_x, walldowncenter_y)
        #wall = 4
    elif wall == 4:
        helppoint(solution[0], solution[1], wallplayer1center_x, wallplayer1center_y)
        #wall = 1
    else:
        print("ERROR input must be in the set of {1,2,3,4}")
    print("Solution: ( ", solution[0],", ", solution[1], " )" )
    print("helppoint: (" , helppoint_x, ", ", helppoint_y, ")")
    p1 = xy_to_PD(solution[0],solution[1])
    p2 = xy_to_PD(helppoint_x,helppoint_y)
    g = PDGeodesic(p1,p2)
    center = g._center.getComplex()
    ballgeodesiccenter_x = center.real
    ballgeodesiccenter_y = center.imag
    ballgeodesicradius = g._radius

def ball_radius(x,y):
    if sqrt((x - 401)**2 + (y- 401)**2) >= 300:
        return 0
    else:
        return round(15-(15*sqrt((x - 401)**2 + (y- 401)**2))/300)

#we need to find the wall of the nextintersection
def findsolution2():
    global wall, solution
    warnings.simplefilter('error', RuntimeWarning)
    solutions = [None, None, None, None]
    try:
        solutions[0]= opt.fsolve(wallupintersection, (0.1,0.1))
    except RuntimeWarning:
        solutions[0]= None
    try:
        solutions[1]= opt.fsolve(wallplayer2intersection, (0.1,0.1))
    except RuntimeWarning:
        solutions[1]= None
    try:
        solutions[2]= opt.fsolve(walldownintersection, (0.1,0.1))
    except RuntimeWarning:
        solutions[2]= None
    try:
        solutions[3]= opt.fsolve(wallplayer1intersection, (0.1,0.1))
    except RuntimeWarning:
        solutions[3]= None
    print ("Solutions: " , solutions)
    if solutions[0] is None and solutions[1] is None and solutions[2] is None and solutions[3] is None:
        print("Error")
        raise RuntimeError()

    min = None
    j = 0
    for i in range(4):
        if solutions[i] is None:
            continue
        else:
            dist = distance(oldsolution[0]+ oldsolution[1]*1j, solutions[i][0] + solutions[i][1]*1j)
            if min == None:
                if dist > 1.0e-15:
                    min = dist
                    j = i
            else:
                if dist < min and dist > 1.0e-15:
                    min = dist
                    j = i
        wall = j+1
        solution = solutions[j]

def findnewmovement(variables):
    t = variables

    first_eq = oldsolution[0] - ballgeodesiccenter_x - ballgeodesicradius*cos(2*pi*t)
    second_eq = oldsolution[1] - ballgeodesiccenter_y - ballgeodesicradius*sin(2*pi*t)
    return [first_eq, second_eq]

def blitRotate(surf, image, pos, originPos, angle):
    # offset from pivot to center
    image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

    # roatated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # rotated image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

    # rotate and blit the image
    surf.blit(rotated_image, rotated_image_rect)

def show_score(x, y):
    score = font.render(str(score_value_player1) + " : " + str(score_value_player2), True, (255, 255, 255))
    screen.blit(score, (x, y))

def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 255, 255)) #over_font not defined yet
    screen.blit(over_text, (200, 250))

#create a start geodesic
#newgeodesic()

# represents the point of the current intersection point with one of the walls
#solution = opt.fsolve(wallplayer2intersection, (0.1,1) )
#oldsolution = solution
#nextintersection = topygamecoords(solution[0], solution[1])
#wall = 2 #variable to what wall the ball moves
direction = 1
pseudopos = (0,0)


angle1 = 0
angle_rot1 = 0

angle2 = 0
angle_rot2 = 0

image = pygame.image.load('paddle.jpg')
image = pygame.transform.scale(image, (8,50))
paddle1 = image
#otherwise we'll get a background for the image
image.set_colorkey((0,0,0))

image = pygame.image.load('paddle.jpg')
image = pygame.transform.scale(image, (8,50))
paddle2 = image
image.set_colorkey((0,0,0))

w1, h1 = paddle1.get_size()
w2, h2 = paddle2.get_size()

#screen.blit(image,(200,401))
print("Helloooo:",topygamecoords(-0.585, -0.585))

# loop of main programm
while gameactive:
    # check if an action has taken place
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameactive = False

    # integrate game logic here
    if start == True:
        newgeodesic()
        solution = opt.fsolve(wallplayer2intersection, (0.1,1) )
        oldsolution = solution
        nextintersection = topygamecoords(solution[0], solution[1])
        wall = 2 #variable to what wall the ball moves
        start = False

    helpballpos = newballpos(ballgeodesiccenter_x, ballgeodesiccenter_y, ballgeodesicradius, movement)
    movement +=  direction * 0.001/ballgeodesicradius
    ballpos = topygamecoords(helpballpos[0], helpballpos[1])
    ballradius = ball_radius(ballpos[0], ballpos[1])

    #makes the ball switch geodesics when hitting a wall
    if (ballpos[0] - nextintersection[0])**2 + (ballpos[1] - nextintersection[1])**2 <= ballradius**2:
        if wall == 2:
            score_value_player1 += 1
            start = True
        if wall == 4:
            score_value_player2 += 1
            start = True
        #sound.play()
        oldbgc_x = ballgeodesiccenter_x
        oldbgc_y = ballgeodesiccenter_y
        oldbgrad = ballgeodesicradius
        ballgeodesic(wall)
        movement = atan2(solution[1]- ballgeodesiccenter_y, solution[0] - ballgeodesiccenter_x)/(2*pi)
        pseudopos = newballpos(ballgeodesiccenter_x, ballgeodesiccenter_y, ballgeodesicradius, movement + direction * 0.003/ballgeodesicradius)
        if (pseudopos[0] - oldbgc_x)**2 + (pseudopos[1] - oldbgc_y)**2 < oldbgrad**2:
            direction *= -1
        oldsolution = solution
        findsolution2()
        nextintersection = topygamecoords(solution[0],solution[1])
        #Karina said to write a comment here :)

    # delete gamefield
    screen.fill(black)

    # draw gamefield and figures
    pygame.draw.circle(screen, orange, [401,401],300)

    #paddles

    #move paddle of player 1
    c1=newballpos(wallplayer1center_x,wallplayer1center_y,sqrt(1.8),angle1)
    c1_py = topygamecoords(c1[0], c1[1])
    blitRotate(screen, paddle1, (c1_py[0],c1_py[1]), (w1/2,h1/2), angle_rot1)
    key_input = pygame.key.get_pressed()
    #0.66 = (248 - height of paddle) /300
    if abs(c1[0]+1j*c1[1]) <= 0.66:
        if key_input[pygame.K_w]:
            angle_rot1 += 3
            angle1 += 0.008
        if key_input[pygame.K_s]:
            angle_rot1 -= 3
            angle1 -= 0.008
    elif c1[1] < 0:
        if key_input[pygame.K_w]:
            angle_rot1 += 3
            angle1 += 0.008
    elif c1[1] > 0:
        if key_input[pygame.K_s]:
            angle_rot1 -= 3
            angle1 -= 0.008

    #move paddle of player 2
    c2=newballpos(wallplayer2center_x, wallplayer2center_y, -sqrt(1.8), angle2)
    c2_py = topygamecoords(c2[0], c2[1])
    blitRotate(screen, paddle2, (c2_py[0],c2_py[1]), (w2/2,h2/2), angle_rot2)
    key_input = pygame.key.get_pressed()
    if abs(c2[0]+1j*c2[1]) <= 0.66:
        if key_input[pygame.K_DOWN]:
            angle_rot2 += 3
            angle2 += 0.008
        if key_input[pygame.K_UP]:
            angle_rot2 -= 3
            angle2 -= 0.008
    elif c2[1] < 0:
        if key_input[pygame.K_UP]:
            angle_rot2 -= 3
            angle2 -= 0.008
    elif c2[1] > 0:
        if key_input[pygame.K_DOWN]:
            angle_rot2 += 3
            angle2 += 0.008


    help = topygamecoords(helppoint_x, helppoint_y)
    sol  = topygamecoords(solution[0], solution[1])
    pseudo = topygamecoords(pseudopos[0], pseudopos[1])
    # draw gamefield and figures
    pygame.draw.circle(screen, green,[topygamecoords(0,1.75)[0],topygamecoords(0,1.75)[1]],topygameradius(wallradius),5)
    pygame.draw.circle(screen, green,[topygamecoords(0,-1.75)[0],topygamecoords(0,-1.75)[1]],topygameradius(wallradius),5)
    pygame.draw.circle(screen, red,[topygamecoords(-1.75,0)[0],topygamecoords(-1.75,0)[1]],topygameradius(wallradius),5)
    pygame.draw.circle(screen, blue,[topygamecoords(1.75,0)[0],topygamecoords(1.75,0)[1]],topygameradius(wallradius),5)
    pygame.draw.circle(screen, ball_colour, [ballpos[0], ballpos[1]], ballradius)
    pygame.draw.circle(screen, black,[topygamecoords(ballgeodesiccenter_x, ballgeodesiccenter_y)[0],topygamecoords(ballgeodesiccenter_x,ballgeodesiccenter_y)[1]],topygameradius(ballgeodesicradius),5)
    pygame.draw.circle(screen, red, [help[0], help[1]], 10)
    pygame.draw.circle(screen, blue, [pseudo[0], pseudo[1]], 10)
    pygame.draw.circle(screen, green, [sol[0], sol[1]], 10)
    pygame.draw.polygon(screen, black, [[0,0],[0,377],[377,0]])
    pygame.draw.polygon(screen, black, [[801,0],[801-377,0],[801,377]])
    pygame.draw.polygon(screen, black, [[0,801],[0,801-377],[377,801]])
    pygame.draw.polygon(screen, black, [[801,801],[801-377,801],[801,801-377]])

    show_score(360, 10)
    # refresh Window
    pygame.display.update()

    # set refreshing time
    clock.tick(60)#normal 60

pygame.quit()
quit()
