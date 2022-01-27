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
font_normal = pygame.font.Font('pixChicago.ttf', 32)
font_small = pygame.font.Font('pixChicago.ttf', 25)
end_background = pygame.transform.scale(pygame.image.load('Gameoverbg.png'), (width, height))
# open window
screen = pygame.display.set_mode((width, height))

# title
pygame.display.set_caption("Ping Pong")

# game runs aslong as true
gameactive = True

# screen update
clock = pygame.time.Clock()

ball_colour = white
movement = 0
direction = 1

#paddle information
angle1 = 0
angle_rot1 = 0

angle2 = 0
angle_rot2 = 0

image = pygame.image.load('paddle.jpg')
image = pygame.transform.scale(image, (8,50))
paddle1 = image
paddle2 = image
#otherwise we'll get a background for the image
image.set_colorkey((0,0,0))

w1, h1 = paddle1.get_size()
w2, h2 = paddle2.get_size()

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
paddleradius = sqrt(1.8)

#Creating first geodesic
ballgeodesiccenter_x = 0
ballgeodesiccenter_y = 0
ballgeodesicradius = 0

maxrad = 10
#needed to find next ballgeodesic
helppoint_x = 0
helppoint_y = 0
solution = (0,0)

#needed to find correct direction
pseudopos = (0,0)

# shows wether the ball will be reset or not
start = True


#function to change current ballgeodesic
def ballgeodesic(wall):
    global ballgeodesiccenter_x, ballgeodesiccenter_y, ballgeodesicradius
    #see numeration of walls
    if wall == 1:
        helppoint(solution[0], solution[1], wallupcenter_x, wallupcenter_y)
    elif wall == 2:
        helppoint(solution[0], solution[1], wallplayer2center_x, wallplayer2center_y)
        print("Helppopint:", helppoint_x, helppoint_y)
    elif wall == 3:
        helppoint(solution[0], solution[1], walldowncenter_x, walldowncenter_y)
    elif wall == 4:
        helppoint(solution[0], solution[1], wallplayer1center_x, wallplayer1center_y)
    else:
        print("ERROR input must be in the set of {1,2,3,4}")
    p1 = xy_to_PD(solution[0],solution[1])
    p2 = xy_to_PD(helppoint_x,helppoint_y)
    g = PDGeodesic(p1,p2)
    center = g._center.getComplex()
    ballgeodesiccenter_x = center.real
    ballgeodesiccenter_y = center.imag
    ballgeodesicradius = g._radius

#euclidean
#def ball_radius(x,y):
#    if sqrt((x - 401)**2 + (y- 401)**2) >= 300:
#        return 0
#    else:
#        return round(15-(15*sqrt((x - 401)**2 + (y- 401)**2))/300)

#hyperbolic
def ball_radius(x,y):
    z0=x+y*1j    
    z1=0
    return round(5*(1/distance(z0,z1)))

def blitRotate(surf, image, pos, originPos, angle):
    #to get the left corner of the image
    image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

    #rotated offset from pivot to center; 
    #vector2 function rotates in the opposite direction than transform
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # rotated image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

    # rotate and blit the image
    surf.blit(rotated_image, rotated_image_rect)

def distance(z0,z1):
    distance = cmath.acosh(1+2*(abs(z0-z1)**2)/((1-abs(z0)**2)*(1-abs(z1)**2)))
    return abs(distance)

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

def game_over_text(win):
    over_text2 = font_normal.render(str(score_value_player1) + " : " + str(score_value_player2), True, white)
    over_text3 = font_small.render("Press R to restart or Esc to exit the game.", True, white)
    if score_value_player1 == win:
        over_text1 = font_normal.render("Player 1 won!", True, white)
    if score_value_player2 == win:
        over_text1 = font_normal.render("Player 2 won!", True, white)
    over_text1_rect = over_text1.get_rect(center=(width/2, height/4))
    over_text2_rect = over_text2.get_rect(center=(width/2, height/3))
    over_text3_rect = over_text3.get_rect(center=(width/2, 3*height/4))
    screen.blit(over_text1, over_text1_rect)
    screen.blit(over_text2, over_text2_rect)
    screen.blit(over_text3, over_text3_rect)


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

def helptangent(variables):
    (x,y) = variables

    first_eq = (x - ballgeodesiccenter_x)**2 + (y-ballgeodesiccenter_y)**2 - ballgeodesicradius**2
    second_eq = m_tangent*x + b_tangent - y
    return [first_eq, second_eq]

def newballpos(center_x, center_y, radius, t):
    newballpos = [center_x + radius*cos(2*pi*t), center_y + radius*sin(2*pi*t)]
    return newballpos

def newgeodesic(x1, y1, x2, y2):
    global ballgeodesiccenter_x, ballgeodesiccenter_y, ballgeodesicradius
    p1 = xy_to_PD(x1, y1)
    p2 = xy_to_PD(x2, y2)
    g = PDGeodesic(p1,p2)
    center = g._center.getComplex()
    ballgeodesiccenter_x = center.real
    ballgeodesiccenter_y = center.imag
    ballgeodesicradius = g._radius

#euclidean
#def paddle_scaling(x,y):
#     if sqrt((x-401)**2 + (y-401)**2) >=300:
#         return (0,0)
#     else:
#         return (round(16-(16*sqrt((x - 401)**2 + (y- 401)**2))/300), 90-(90*sqrt((x - 401)**2 + (y- 401)**2))/300)

#hyperbolic
def paddle_scaling(x,y):
    z0=x+y*1j
    z1=0
    return (round(16*1/distance(z0,z1)),round(90*1/distance(z0,z1)))
 
def PD_to_xy(point):
    x = point.getReal()
    y = point.getImag()
    return (x,y)

def pseudorand():
    #x = random.randint(1,2)
    global movement, direction, wall, solution
    x = np.random.random_integers(1,4)
    if x == 1:
        newgeodesic(0.3, 0.4, 0.45, 0.2)
        movement = 0.55
        direction = 1
        wall = 2
        solution = opt.fsolve(wallplayer2intersection, (0.1,1) )
        oldsolution = solution
    if x == 2:
        newgeodesic(0.3, 0.4, 0.45, 0.2)
        movement = 0.6
        direction = -1
        wall = 1
        solution = opt.fsolve(wallupintersection, (0.1,1) )
        oldsolution = solution
    if x == 3:
        newgeodesic(0.1, -0.5, -0.22, 0.3)
        movement = 0.075
        direction = -1
        wall = 3
        solution = opt.fsolve(walldownintersection, (0.1,1))
        oldsolution = solution
    if x == 4:
        newgeodesic(-0.1, 0.22, -0.3, -0.5)
        movement = 0.95
        direction = -1
        wall = 3
        solution = opt.fsolve(walldownintersection, (0.1,1))
        oldsolution = solution

def show_score(x, y):
    score = font_normal.render(str(score_value_player1) + " : " + str(score_value_player2), True, (255, 255, 255))
    screen.blit(score, (x, y))

#function to calculate pygame coordinates into normal coordinates
def topygamecoords(xcord, ycord):
    point = [round(401 + xcord*300), round(401 - ycord*300)]
    return point

def topygameradius(radius):
    return 300*radius

def walldownintersection(variables):
    (x,y) = variables

    first_eq = (x-walldowncenter_x)**2+(y-walldowncenter_y)**2 - wallradius**2
    second_eq = (x-ballgeodesiccenter_x)**2+(y-ballgeodesiccenter_y)**2 - ballgeodesicradius**2
    return [first_eq, second_eq]

def wallplayer1intersection(variables):
    (x,y) = variables

    first_eq = (x-wallplayer1center_x)**2+(y-wallplayer1center_y)**2 - paddleradius**2
    second_eq = (x-ballgeodesiccenter_x)**2+(y-ballgeodesiccenter_y)**2 - ballgeodesicradius**2
    return [first_eq, second_eq]

def wallplayer2intersection(variables):
    (x,y) = variables

    first_eq = (x-wallplayer2center_x)**2+(y-wallplayer2center_y)**2 - paddleradius**2
    second_eq = (x-ballgeodesiccenter_x)**2+(y-ballgeodesiccenter_y)**2 - ballgeodesicradius**2
    return [first_eq, second_eq]

def wallupintersection(variables):
    (x,y) = variables

    first_eq = (x-wallupcenter_x)**2+(y-wallupcenter_y)**2 - wallradius**2
    second_eq = (x-ballgeodesiccenter_x)**2+(y-ballgeodesiccenter_y)**2 - ballgeodesicradius**2
    return [first_eq, second_eq]

def xy_to_PD(x,y):
    z = PDPoint(complex(x,y))
    return(z)

# loop of main programm
while gameactive:

    win = 10

    # check if an action has taken place
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameactive = False

    while score_value_player1 < win and score_value_player2 < win:
        # integrate game logic here
        if start == True:
            pseudorand() #creates a new pseudo random geodesic
            nextintersection = topygamecoords(solution[0], solution[1])
            start = False

        helpballpos = newballpos(ballgeodesiccenter_x, ballgeodesiccenter_y, ballgeodesicradius, movement)
        if ballgeodesicradius == 0:
            movement += direction * 0.001/maxrad
        else:
            movement +=  direction * 0.001/ballgeodesicradius
        ballpos = topygamecoords(helpballpos[0], helpballpos[1])
        ballradius = ball_radius(ballpos[0], ballpos[1])

        #makes the ball switch geodesics when hitting a wall
        if (ballpos[0] - nextintersection[0])**2 + (ballpos[1] - nextintersection[1])**2 <= ballradius**2 and (wall == 1 or wall == 3):
            if wall == 1:
                wall_x = wallupcenter_x
                wall_y = wallupcenter_y
            if wall == 3:
                wall_x = walldowncenter_x
                wall_y = walldowncenter_y
            #sound.play()
            ballgeodesic(wall)
            movement = atan2(solution[1]- ballgeodesiccenter_y, solution[0] - ballgeodesiccenter_x)/(2*pi)
            if ballgeodesicradius == 0:
                pseudomovement = movement + direction * 0.001/maxrad
            else:
                pseudomovement = movement + direction * 0.001/ballgeodesicradius
            pseudopos = newballpos(ballgeodesiccenter_x, ballgeodesiccenter_y, ballgeodesicradius, pseudomovement)
            if (pseudopos[0] - wall_x)**2 + (pseudopos[1]-wall_y)**2 < wallradius**2:
                direction *= -1
            oldsolution = solution
            findsolution2()
            nextintersection = topygamecoords(solution[0],solution[1])
        elif (helpballpos[0] - wallplayer2center_x)**2 + (helpballpos[1] - wallplayer2center_y)**2 <= wallradius**2 and wall == 2:
            score_value_player1 += 1
            start = True
        elif (helpballpos[0] - wallplayer1center_x)**2 + (helpballpos[1] - wallplayer1center_y)**2 <= wallradius**2 and wall == 4:
            score_value_player2 += 1
            start = True

        # delete gamefield
        screen.fill(black)

        # draw gamefield and figures
        pygame.draw.circle(screen, orange, [401,401],300)

        #paddles
        #move paddle of player 1
        c1=newballpos(wallplayer1center_x,wallplayer1center_y, paddleradius,angle1)
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
        paddle1 = pygame.transform.scale(paddle1, paddle_scaling(c1_py[0],c1_py[1]))

        #move paddle of player 2
        c2=newballpos(wallplayer2center_x, wallplayer2center_y, -paddleradius, angle2)
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
        paddle2 = pygame.transform.scale(paddle2, paddle_scaling(c2_py[0],c2_py[1]))

        #ball bounces of paddle 1
        #1.8 is the radius of the paddle geodesic
        if c1_py[0] - paddle1.get_width()/2 <= nextintersection[0] <= c1_py[0] + paddle1.get_width()/2 and c1_py[1] - paddle1.get_height()/2 <= nextintersection[1] <= c1_py[1] + paddle1.get_height()/2 and (ballpos[0] - nextintersection[0])**2 + (ballpos[1] - nextintersection[1])**2 <= ballradius**2:
            #sound.play()
            ballgeodesic(wall)
            movement = atan2(solution[1]- ballgeodesiccenter_y, solution[0] - ballgeodesiccenter_x)/(2*pi)
            if ballgeodesicradius == 0:
                pseudomovement = movement + direction * 0.001/maxrad
            else:
                pseudomovement = movement + direction * 0.001/ballgeodesicradius
            pseudopos = newballpos(ballgeodesiccenter_x, ballgeodesiccenter_y, ballgeodesicradius, pseudomovement)
            if (pseudopos[0] - wallplayer1center_x)**2 + (pseudopos[1] - wallplayer1center_y)**2 < paddleradius**2:
                direction *= -1
            oldsolution = solution
            findsolution2()
            nextintersection = topygamecoords(solution[0],solution[1])

        #ball bounces of paddle 2
        #1.8 is the radius of the paddle geodesic
        if c2_py[0] + paddle2.get_width()/2 >= nextintersection[0] >= c2_py[0] - paddle2.get_width()/2 and c2_py[1] - paddle2.get_height()/2 <= nextintersection[1] <= c2_py[1] + paddle2.get_height()/2 and (ballpos[0] - nextintersection[0])**2 + (ballpos[1] - nextintersection[1])**2 <= ballradius**2:
        #sound.play()
            ballgeodesic(wall)
            movement = atan2(solution[1]- ballgeodesiccenter_y, solution[0] - ballgeodesiccenter_x)/(2*pi)
            if ballgeodesicradius == 0:
                pseudomovement = movement + direction * 0.001/maxrad
            else:
                pseudomovement = movement + direction * 0.001/ballgeodesicradius
            pseudopos = newballpos(ballgeodesiccenter_x, ballgeodesiccenter_y, ballgeodesicradius, pseudomovement)
            if (pseudopos[0] - wallplayer2center_x)**2 + (pseudopos[1] - wallplayer2center_y)**2 < paddleradius**2:
                direction *= -1
            oldsolution = solution
            findsolution2()
            nextintersection = topygamecoords(solution[0],solution[1])

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
        pygame.event.pump() # process event queue
        # set refreshing time
        clock.tick(60)#normal 60

    screen.fill(black)
    screen.blit(end_background, (0,0))
    game_over_text(win)
    pygame.display.update()
    decision = pygame.key.get_pressed()
    if decision[pygame.K_r]:
        score_value_player1 = 0
        score_value_player2 = 0
        start = True
    elif decision[pygame.K_ESCAPE]:
        gameactive = False

    # set refreshing time
    clock.tick(60)#normal 60

pygame.quit()
quit()
