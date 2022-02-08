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
turquoise = (0,206,209)
grey = (112, 128, 144)
red     = ( 153, 0, 0)
green   = ( 0, 153, 0)
blue = ( 72, 61, 139)
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
wallup_p1 = PDPoint(complex(0.7,0.5))
wallup_p2 = PDPoint(complex(-0.7,0.5))
wallup = PDGeodesic(wallup_p1, wallup_p2)
wallupcenter = wallup._center.getComplex()
wallupcenter_x = wallupcenter.real
wallupcenter_y = wallupcenter.imag
wallupradius = wallup._radius
#2
wallplayer2_p1 = PDPoint(complex(0.7,0.5))
wallplayer2_p2 = PDPoint(complex(0.7,-0.5))
wallplayer2 = PDGeodesic(wallplayer2_p1, wallplayer2_p2)
wallplayer2center = wallplayer2._center.getComplex()
wallplayer2center_x = wallplayer2center.real
wallplayer2center_y = wallplayer2center.imag
wallplayer2radius = wallplayer2._radius
#3
walldown_p1 = PDPoint(complex(0.7,-0.5))
walldown_p2 = PDPoint(complex(-0.7,-0.5))
walldown = PDGeodesic(walldown_p1, walldown_p2)
walldowncenter = walldown._center.getComplex()
walldowncenter_x = walldowncenter.real
walldowncenter_y = walldowncenter.imag
walldownradius = walldown._radius
#4
wallplayer1_p1 = PDPoint(complex(-0.7,0.5))
wallplayer1_p2 = PDPoint(complex(-0.7,-0.5))
wallplayer1 = PDGeodesic(wallplayer1_p1, wallplayer1_p2)
wallplayer1center = wallplayer1._center.getComplex()
wallplayer1center_x = wallplayer1center.real
wallplayer1center_y = wallplayer1center.imag
wallplayer1radius = wallplayer1._radius
#changes wallradius depending on the wall(difference between wallup/walldown and wallpayer1/wallplayer2)
wallradius = 0
wallcenter = (0,0)
paddleradius = sqrt(0.6)

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

#calculates a ball radius depending on the distance to the center
def ball_radius(x,y):
    if sqrt(x**2 + y**2) >= 1:
        return 0
    else:
        return 15*(1-(x**2 + y**2))

#originPos is position of the mid point in the rectangle (not using cords just general length of the rectangle)
#pos is the postion the origin is supposed to have
def blitRotate(surf, image, pos, originPos, angle):
    # offset from pivot to center
    image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

    # rotated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # rotated image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

    # rotate and blit the image
    surf.blit(rotated_image, rotated_image_rect)

#calculates the hyperbolic distance
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
                if dist > 1.0e-15 and abs(solutions[i][0] + solutions[i][1]*1j) <= 0.8:
                    min = dist
                    j = i
            else:
                if dist < min and dist > 1.0e-15 and abs(solutions[i][0] + solutions[i][1]*1j) <= 0.8:
                    min = dist
                    j = i
        wall = j+1
        solution = solutions[j]

#creates the text for game over screen
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
            b_tangent = solution_y - m_tangent*solution_x + 0.0001
        elif center_x == wallupcenter_x and center_y == wallupcenter_y :
            b_tangent = solution_y - m_tangent*solution_x - 0.0001
        elif center_x == wallplayer1center_x and center_y == wallplayer1center_y :
            b_tangent = solution_y - m_tangent*solution_x - 0.0001
        elif center_x == wallplayer2center_x and center_y == wallplayer2center_y :
            b_tangent = solution_y - m_tangent*solution_x + 0.0001

        helpsolve = opt.fsolve(helptangent, (solution_x,solution_y))
        orthintersect_y = m_tangent*(b_orthogonal - b_tangent)/(m_tangent - n) + b_tangent
        orthintersect_x = (b_orthogonal - b_tangent)/(m_tangent - n)
        helppoint_y = 2*orthintersect_y - helpsolve[1]
        helppoint_x = 2*orthintersect_x - helpsolve[0]

    elif center_y - solution_y == 0:
            if center_x == wallplayer1center_x and center_y == wallplayer1center_y :
                helppoint_x = solution_x + 0.001
                helppoint_y = solution_y + 0.001
            elif center_x == wallplayer2center_x and center_y == wallplayer2center_y :
                helppoint_x = solution_x - 0.001
                helppoint_y = solution_y - 0.001
            else:
                print("Something went very wrong.")
    elif center_x - solution_x == 0:
            if center_x == walldowncenter_x and center_y == walldowncenter_y :
                helppoint_y = solution_y + 0.001
                helppoint_x = solution_x - 0.001
            elif center_x == wallupcenter_x and center_y == wallupcenter_y :
                helppoint_y = solution_y - 0.001
                helppoint_x = solution_x + 0.001
            else:
                print("Something went very wrong.")

#calculates the neccessary
def helptangent(variables):
    (x,y) = variables
    first_eq = (x - ballgeodesiccenter_x)**2 + (y-ballgeodesiccenter_y)**2 - ballgeodesicradius**2
    second_eq = m_tangent*x + b_tangent - y
    return [first_eq, second_eq]

#calculates the new ball position to make the ball move smoothly
def newballpos(center_x, center_y, radius, t):
    newballpos = [center_x + radius*cos(2*pi*t), center_y + radius*sin(2*pi*t)]
    return newballpos

#creates a new geodesic depending on two points
def newgeodesic(x1, y1, x2, y2):
    global ballgeodesiccenter_x, ballgeodesiccenter_y, ballgeodesicradius
    p1 = xy_to_PD(x1, y1)
    p2 = xy_to_PD(x2, y2)
    g = PDGeodesic(p1,p2)
    center = g._center.getComplex()
    ballgeodesiccenter_x = center.real
    ballgeodesiccenter_y = center.imag
    ballgeodesicradius = g._radius

#making the paddle get smaller depending on the distance to the center
def paddle_scaling(x,y):
    if sqrt((x- 401)**2 + (y - 401)**2) >=300:
        return (0,0)
    else:
        return (round(16-(16*sqrt((x - 401)**2 + (y- 401)**2)/300)), round(90-(90*sqrt((x-401)**2 + (y-401)**2)/300)))

#makes a PD point and finds the fitting (x,y) point
def PD_to_xy(point):
    x = point.getReal()
    y = point.getImag()
    return (x,y)

#chooses a new start geodesic when ball restarts it's pseudo random because it chooses randomly out of 10 possible geodesics
def pseudorand():
    #x = random.randint(1,2)
    global movement, direction, wall, solution
    x = np.random.random_integers(1,10)
    if x == 1:
        newgeodesic(0.3, 0.4, 0.45, 0.2)
        movement = 0.60
        direction = 1
        wall = 2
        solution = opt.fsolve(wallplayer2intersection, (0.1,1) )
        oldsolution = solution
    if x == 2:
        newgeodesic(-0.0662, 0.2629, 0.2868, 0.0756)
        movement = -0.3475
        direction = 1
        wall = 2
        solution = opt.fsolve(wallplayer2intersection, (0.1,1) )
        oldsolution = solution
    if x == 3:
        newgeodesic(-0.12, -0.11, -0.45, -0.2)
        movement = 0.275
        direction = 1
        wall = 4
        solution = opt.fsolve(wallplayer1intersection, (0.1,1))
        oldsolution = solution
    if x == 4:
        newgeodesic(-0.05, 0.22, -0.3, -0.5)
        movement = -0.04
        direction = -1
        wall = 3
        solution = opt.fsolve(walldownintersection, (0.1,1))
        oldsolution = solution
    if x == 5:
        newgeodesic(0.4473, -0.2192, 0.1314, -0.1148)
        movement = -0.8
        direction = -1
        wall = 2
        solution = opt.fsolve(wallplayer2intersection, (0.1,1))
        oldsolution = solution
    if x == 6:
        newgeodesic(0.252, -0.0883, 0.265, -0.089)
        movement = 0.249
        direction = -1
        wall = 2
        solution = opt.fsolve(wallplayer2intersection, (0.1,1))
        oldsolution = solution
    if x == 7:
        newgeodesic(-0.2275, 0.2389, 0.029, -0.249)
        movement = 0.075
        direction = -1
        wall = 3
        solution = opt.fsolve(walldownintersection, (0.1, 1))
        oldsolution = solution
    if x == 8:
        newgeodesic(-0.2937, -0.1265, -0.2555, 0.2046)
        movement = 0.0096
        direction = -1
        wall = 3
        solution = opt.fsolve(walldownintersection, (0.1, 1))
        oldsolution = solution
    if x == 9:
        newgeodesic(-0.1683, -0.2514, -0.0005, -0.1368)
        movement = 0.3551
        direction = -1
        wall = 3
        solution = opt.fsolve(walldownintersection, (0.1, 1))
        oldsolution = solution
    if x == 10:
        newgeodesic(-0.497, -0.088, -0.398, -0.163)
        movement = 0.1
        direction = 1
        wall = 4
        solution = opt.fsolve(wallplayer1intersection, (0.1, 1))
        oldsolution = solution

#shows current score of player 1 and player 2
def show_score(x, y):
    score = font_normal.render(str(score_value_player1) + " : " + str(score_value_player2), True, (255, 255, 255))
    screen.blit(score, (x, y))

#function to calculate normal coordinates into pygame coordinates
def topygamecoords(xcord, ycord):
    point = [round(401 + xcord*300), round(401 - ycord*300)]
    return point

#function to calculate radius into pygame radius
def topygameradius(radius):
    return 300*radius

#finds the solution to the lower wall
def walldownintersection(variables):
    (x,y) = variables

    first_eq = (x-walldowncenter_x)**2+(y-walldowncenter_y)**2 - walldownradius**2
    second_eq = (x-ballgeodesiccenter_x)**2+(y-ballgeodesiccenter_y)**2 - ballgeodesicradius**2
    return [first_eq, second_eq]

#finds the solution to the player 1 paddle
def wallplayer1intersection(variables):
    (x,y) = variables

    first_eq = (x-wallplayer1center_x)**2+(y-wallplayer1center_y)**2 - paddleradius**2
    second_eq = (x-ballgeodesiccenter_x)**2+(y-ballgeodesiccenter_y)**2 - ballgeodesicradius**2
    return [first_eq, second_eq]

#finds the solution to the player 2 paddle
def wallplayer2intersection(variables):
    (x,y) = variables

    first_eq = (x-wallplayer2center_x)**2+(y-wallplayer2center_y)**2 - paddleradius**2
    second_eq = (x-ballgeodesiccenter_x)**2+(y-ballgeodesiccenter_y)**2 - ballgeodesicradius**2
    return [first_eq, second_eq]

#gives out the wallradius of the desired wall
def wallrad(wall):
    global wallradius
    if(wall == 1): wallradius = wallupradius
    if(wall == 2): wallradius = wallplayer2radius
    if(wall == 3): wallradius = walldownradius
    if(wall == 4): wallradius = wallplayer1radius
    return(wallradius)

#finds the solution to the upper wall
def wallupintersection(variables):
    (x,y) = variables

    first_eq = (x-wallupcenter_x)**2+(y-wallupcenter_y)**2 - wallupradius**2
    second_eq = (x-ballgeodesiccenter_x)**2+(y-ballgeodesiccenter_y)**2 - ballgeodesicradius**2
    return [first_eq, second_eq]

#converts (x,y) coordinates into a PD point
def xy_to_PD(x,y):
    z = PDPoint(complex(x,y))
    return(z)

# loop of main programm
while gameactive:

    win = 5

    #check if an action has taken place and makes it possible to quit game when game over
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameactive = False

    #makes the game run until a player has won
    while score_value_player1 < win and score_value_player2 < win and gameactive:

        input = pygame.key.get_pressed()
        if input[pygame.K_ESCAPE]:
            gameactive = False

        # integrate game logic here
        if start == True:
            pseudorand() #creates a new pseudo random geodesic
            nextintersection = topygamecoords(solution[0], solution[1])
            start = False

        helpballpos = newballpos(ballgeodesiccenter_x, ballgeodesiccenter_y, ballgeodesicradius, movement)
        if ballgeodesicradius == 0:
            movement += direction * 0.001*((score_value_player1 + score_value_player2)/4 + 1)/maxrad
        else:
            movement +=  direction * 0.001*((score_value_player1 + score_value_player2)/4 + 1)/ballgeodesicradius
        ballpos = topygamecoords(helpballpos[0], helpballpos[1])
        ballradius = ball_radius(helpballpos[0], helpballpos[1])
        #makes the ball switch geodesics when hitting a wall
        if (ballpos[0] - nextintersection[0])**2 + (ballpos[1] - nextintersection[1])**2 <= ballradius**2 and (wall == 1 or wall == 3):
            if wall == 1:
                wall_x = wallupcenter_x
                wall_y = wallupcenter_y
                wallradius = wallrad(wall)
            if wall == 3:
                wall_x = walldowncenter_x
                wall_y = walldowncenter_y
                wallradius = wallrad(wall)
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
        elif (helpballpos[0] - wallplayer2center_x)**2 + (helpballpos[1] - wallplayer2center_y)**2 <= wallrad(2)**2 and wall == 2:
            score_value_player1 += 1
            start = True
        elif (helpballpos[0] - wallplayer1center_x)**2 + (helpballpos[1] - wallplayer1center_y)**2 <= wallrad(4)**2 and wall == 4:
            score_value_player2 += 1
            start = True
        elif (helpballpos[0] - wallupcenter_x)**2 + (helpballpos[1] - wallupcenter_y)**2 < wallrad(1)**2 - 0.1:
            start = True
        elif (helpballpos[0] - walldowncenter_x)**2 + (helpballpos[1] - walldowncenter_y)**2 < wallrad(3)**2 - 0.1:
            start = True
        # delete gamefield
        screen.fill(black)

        # draw gamefield and figures
        pygame.draw.circle(screen, blue, [401,401],300)

        #paddles
        #move paddle of player 1
        c1=newballpos(wallplayer1center_x,wallplayer1center_y, paddleradius,angle1)
        c1_py = topygamecoords(c1[0], c1[1])
        blitRotate(screen, paddle1, (c1_py[0],c1_py[1]), (w1/2,h1/2), angle_rot1)
        key_input = pygame.key.get_pressed()
        #0.66 = (248 - height of paddle) /300
        x = paddle1.get_height()
        if abs(c1[0]+1j*c1[1]) <= 0.66 or c1[1] < 0:
            if key_input[pygame.K_w]:
                angle_rot1 += 3
                angle1 += 0.008
        if abs(c1[0]+1j*c1[1]) <= 0.8 or c1[1] > 0:
            if key_input[pygame.K_s]:
                angle_rot1 -= 3
                angle1 -= 0.008
        paddle1 = pygame.transform.scale(paddle1, paddle_scaling(c1_py[0],c1_py[1]))

        #move paddle of player 2
        c2=newballpos(wallplayer2center_x, wallplayer2center_y, -paddleradius, angle2)
        c2_py = topygamecoords(c2[0], c2[1])
        blitRotate(screen, paddle2, (c2_py[0],c2_py[1]), (w2/2,h2/2), angle_rot2)
        key_input = pygame.key.get_pressed()
        y = paddle2.get_height()
        if abs(c2[0]+1j*c2[1]) <= 0.66 or c2[1] < 0:
            if key_input[pygame.K_UP]:
                angle_rot2 -= 3
                angle2 -= 0.008
        if abs(c2[0]+1j*c2[1]) <= 0.75 or c2[1] > 0:
            if key_input[pygame.K_DOWN]:
                angle_rot2 += 3
                angle2 += 0.008
        paddle2 = pygame.transform.scale(paddle2, paddle_scaling(c2_py[0],c2_py[1]))

        #ball bounces of paddle 1
        #1.8 is the radius of the paddle geodesic
        if c1_py[0] - paddle1.get_width()/2 - ballradius <= nextintersection[0] <= c1_py[0] + paddle1.get_width()/2 + ballradius and c1_py[1] - paddle1.get_height()/2 - ballradius <= nextintersection[1] <= c1_py[1] + paddle1.get_height()/2 + ballradius and (ballpos[0] - nextintersection[0])**2 + (ballpos[1] - nextintersection[1])**2 <= ballradius**2:
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
        if c2_py[0] + paddle2.get_width()/2 + ballradius >= nextintersection[0] >= c2_py[0] - paddle2.get_width()/2 - ballradius and c2_py[1] - paddle2.get_height()/2 - ballradius <= nextintersection[1] <= c2_py[1] + paddle2.get_height()/2 + ballradius and (ballpos[0] - nextintersection[0])**2 + (ballpos[1] - nextintersection[1])**2 <= ballradius**2:
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

        #these variables are for debugging purposes
        #help = topygamecoords(helppoint_x, helppoint_y)
        #sol  = topygamecoords(solution[0], solution[1])
        #pseudo = topygamecoords(pseudopos[0], pseudopos[1])
        # draw gamefield and figures
        pygame.draw.circle(screen, grey,[topygamecoords(wallupcenter_x,wallupcenter_y)[0],topygamecoords(wallupcenter_x,wallupcenter_y)[1]],topygameradius(wallup._radius),5)
        pygame.draw.circle(screen, grey,[topygamecoords(walldowncenter_x,walldowncenter_y)[0],topygamecoords(walldowncenter_x,walldowncenter_y)[1]],topygameradius(walldown._radius),5)
        pygame.draw.circle(screen, red,[topygamecoords(wallplayer1center_x,wallplayer1center_y)[0],topygamecoords(wallplayer1center_x,wallplayer1center_y)[1]],topygameradius(wallplayer1._radius),5)
        pygame.draw.circle(screen, turquoise,[topygamecoords(wallplayer2center_x,wallplayer2center_y)[0],topygamecoords(wallplayer2center_x,wallplayer2center_y)[1]],topygameradius(wallplayer2._radius),5)
        pygame.draw.circle(screen, ball_colour, [ballpos[0], ballpos[1]], ballradius)
        #the following drawings are for debugging purposes
        #pygame.draw.circle(screen, black,[topygamecoords(ballgeodesiccenter_x, ballgeodesiccenter_y)[0],topygamecoords(ballgeodesiccenter_x,ballgeodesiccenter_y)[1]],topygameradius(ballgeodesicradius),5)
        #pygame.draw.circle(screen, red, [help[0], help[1]], 10)
        #pygame.draw.circle(screen, blue, [pseudo[0], pseudo[1]], 10)
        #pygame.draw.circle(screen, green, [sol[0], sol[1]], 10)
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

    #this part creates the game over screen
    screen.fill(black)
    screen.blit(end_background, (0,0))
    game_over_text(win)
    pygame.display.update()
    decision = pygame.key.get_pressed()
    #restart
    if decision[pygame.K_r]:
        score_value_player1 = 0
        score_value_player2 = 0
        start = True
    #exit game
    elif decision[pygame.K_ESCAPE]:
        gameactive = False

    # set refreshing time
    clock.tick(60)#normal 60

pygame.quit()
quit()
