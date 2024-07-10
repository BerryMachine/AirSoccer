from tkinter import *
import pymunk
import pymunk.util
from time import *
from math import *

# CONSTANTS

FPS = 1/30
BG = "MediumPurple4"
WIDTH = 1000
HEIGHT = 700
MIDW = WIDTH//2
MIDH = HEIGHT//2
GH = 50


# OBJECTS

# for cues and ball
class Ball:
    def __init__(self, space, static_body, type, x, y, r, c):
        self.type = type
        self.spawnx = x
        self.spawny = y
        self.r = r
        self.c = c
        self.x = x
        self.y = y

        # set up pymunk body
        self.body = pymunk.Body()
        self.body.position = (x, y)
        self.body.velocity = (0, 0)
        self.shape = pymunk.Circle(self.body, r)

        # ball properties
        if self.type == "ball": self.shape.mass = 2
        else: self.shape.mass = 7
        if self.type == "ball": self.shape.elasticity = 1
        else: self.shape.elasticity = 0.8

        # use pivot joint to add friction
        self.pivot = pymunk.PivotJoint(static_body, self.body, (0, 0), (0, 0))
        self.pivot.max_bias = 0
        if self.type == "ball": self.pivot.max_force = 300
        else: self.pivot.max_force = 700

        # add ball to physics space
        space.add(self.body, self.shape, self.pivot)

    # draw object
    def draw(self, screen):
        self.x = self.body.position[0]
        self.y = self.body.position[1]
        self.tkbody = screen.create_oval(self.x-self.r, self.y-self.r, self.x+self.r, self.y+self.r, fill=self.c)

    # delete object
    def delete(self, screen):
        screen.delete(self.tkbody)

    # reset object
    def reset(self):
        self.body.position = (self.spawnx, self.spawny)
        self.x = self.spawnx
        self.y = self.spawny
        self.body.velocity = (0, 0)
    

# for walls/border of game field
class Wall:
    # CONSTANTS
    c = "White"

    def __init__(self, space, coords):
        self.coords = coords
        self.body = pymunk.Body(body_type = pymunk.Body.STATIC)
        self.body.position = ((0, 0))
        self.shape = pymunk.Poly(self.body, coords)
        self.shape.elasticity = 0.6

        space.add(self.body, self.shape)

    # draw object
    def draw(self, screen):
        self.tkbody = screen.create_polygon(self.coords, fill=self.c)

    # delete object
    def delete(self, screen):
        screen.delete(self.tkbody)


# GAME WINDOW

root = Tk()
screen = Canvas(root, width=WIDTH, height=HEIGHT, background="MediumPurple4")


# FUNCTIONS

def setInitialValues():
    global space, turn, selected, impulse_circle, impulse_line, impulse_aim, cues_p1, cues_p2, ball, obj

    # PYMUNK SPACE
    space = pymunk.Space()
    static_body = space.static_body

    # initialize game variables
    turn = 1 # 1 for player 1, -1 for player 2
    selected = None
    impulse_circle = None
    impulse_line = None
    impulse_aim = [0, 0]

    # initialize objects
    cues_p1 = [
        Ball(space, static_body, "player1", MIDW//2, MIDH, 20, "cornflower blue"),
        Ball(space, static_body, "player1", MIDW//3, MIDH + 50, 20, "cornflower blue"),
        Ball(space, static_body, "player1", MIDW//3, MIDH - 50, 20, "cornflower blue")
            ]
    
    cues_p2 = [
        Ball(space, static_body, "player2", MIDW + MIDW//2, MIDH, 20, "coral"),
        Ball(space, static_body, "player2", WIDTH - MIDW//3, MIDH + 50, 20, "coral"),
        Ball(space, static_body, "player2", WIDTH - MIDW//3, MIDH - 50, 20, "coral")
    ]

    ball = Ball(space, static_body, "ball", MIDW, MIDH, 8, "white")

    obj = cues_p1.copy() + cues_p2.copy()
    obj.append(ball)

    # define wall coordinates
    wall_coords = [
        [(0, 0), (0, MIDH-GH), (100, MIDH-GH), (100, 0)],
        [(0, MIDH+GH), (0, HEIGHT), (100, HEIGHT), (100, MIDH+GH)],
        [(0, 0), (0, 100), (WIDTH, 100), (WIDTH, 0)],
        [(WIDTH-100, 0), (WIDTH-100, MIDH-GH), (WIDTH, MIDH-GH), (WIDTH, 0)],
        [(WIDTH-100, MIDH+GH), (WIDTH-100, HEIGHT), (WIDTH, HEIGHT), (WIDTH, MIDH+GH)],
        [(0, HEIGHT-100), (0, HEIGHT), (WIDTH, HEIGHT), (WIDTH, HEIGHT-100)],
        [(0, MIDH-GH), (0, MIDH+GH), (60, MIDH+GH), (60, MIDH-GH)],
        [(WIDTH-60, MIDH-GH), (WIDTH-60, MIDH+GH), (WIDTH, MIDH+GH), (WIDTH, MIDH-GH)]
    ]

    # create wall of game field
    for c in wall_coords:
        Wall(space, c).draw(screen)


def resetMap():
    global selected, impulse_circle, impulse_aim, obj

    # delete and reset all except walls
    screen.delete(impulse_circle)
    screen.delete(impulse_line)

    selected = None
    impulse_circle = None
    impulse_aim = [0, 0]
    
    for o in obj:
        o.delete(screen)
        o.reset()


def endGame():
    global running

    # delete guidelines
    screen.delete(impulse_circle)
    screen.delete(impulse_line)

    # display game ended text
    screen.create_text(MIDW, MIDH, text="GAME", fill="White", font="Helvetica 140 bold")
    screen.update()
    sleep(4)

    # delete all
    screen.delete("all")
    screen.update()

    # return to homeScreen
    homeScreen()


def drawObjects(score_p1, score_p2):
    global obj

    # draw all
    for o in obj:
        o.draw(screen)
        
    # display player scores and indicate the player turn
    if turn == 1:
        score_p1_text = screen.create_text(100, 50, text=(f"{username_p1}: {score_p1}"), fill="black", font=('Helvetica 15 bold'))
        score_p2_text = screen.create_text(WIDTH-100, 50, text=(f"{username_p2}: {score_p2}"), fill="black", font=('Helvetica 15'))
    else:
        score_p1_text = screen.create_text(100, 50, text=(f"{username_p1}: {score_p1}"), fill="black", font=('Helvetica 15'))
        score_p2_text = screen.create_text(WIDTH-100, 50, text=(f"{username_p2}: {score_p2}"), fill="black", font=('Helvetica 15 bold'))
    
    return score_p1_text, score_p2_text


def updateObjects():
    # update object positions
    space.step(FPS)


def deleteObjects(score_p1_text, score_p2_text):
    global obj

    # delete all
    for o in obj:
        o.delete(screen)
    screen.delete(score_p1_text)
    screen.delete(score_p2_text)
    

def checkWin(score_p1, score_p2):
    global ball, obj

    # if a cue is stationary in a goal, reset to its original position
    for o in obj:
        if o.body.velocity == (0, 0):
            if o.x < 100 or o.x > WIDTH-100:
                o.reset()

    # check if ball is in a net and update score
    if ball.y > MIDH - 40 and ball.y < MIDH + 40:
        if ball.x < 100:
            return score_p1, score_p2 + 1, True
        if ball.x > WIDTH-100:
            return score_p1 + 1, score_p2, True
        return score_p1, score_p2, False
    return score_p1, score_p2, False


def mouseClickHandler( e ):
    global turn, selected

    # prevent tracking if game is not running
    if running:
        # take cursor coordinates
        x = e.x
        y = e.y

        try:
            # determine selected cue
            if turn == 1:
                for cue in cues_p1:
                    if cue.x - cue.r < x and cue.x + cue.r > x:
                        if cue.y - cue.r < y and cue.y + cue.r > y:
                            selected = cue
                            return 
            else:
                for cue in cues_p2:
                    if cue.x - cue.r < x and cue.x + cue.r > x:
                        if cue.y - cue.r < y and cue.y + cue.r > y:
                            selected = cue
                            return 

            # calculate desired impulse
            if selected:
                # calculate strength of impulse
                fx = -40*(x - selected.x)
                fy = -40*(y - selected.y)
                r = sqrt((fx**2)+(fy**2))

                # cap impulse strength at 4000
                if r > 4000:
                    # preserve desired angle of impulse
                    scale = 4000/r
                    fx *= scale
                    fy *= scale
            
                # apply impulse
                selected.body.apply_impulse_at_local_point((fx, fy), (0, 0))
                # reset selected cue
                selected = None
                # switch turns
                turn *= -1

        except NameError:
            pass


def motion( e ):
    global impulse_aim

    # prevent tracking when not running
    if running:
        try:
            # calculate guideline
            if selected:
                # calculate angle and strength
                diff_x = selected.x - e.x
                diff_y = selected.y - e.y
                r = sqrt((diff_x**2)+(diff_y**2))

                # cap guideline length to 100
                if r > 100:
                    # preserve desired angle
                    scale = 100/r
                    diff_x *= scale
                    diff_y *= scale
                    
                # store values
                impulse_aim = [diff_x, diff_y]
        
        except NameError:
            pass
        


def runGame():
    global running, impulse_circle, impulse_line, impulse_aim, selected, cues_p1, cues_p2, ball, obj

    # clear home screen
    screen.delete("all")

    # button allows return to homescreen
    backButton = Button(screen, text="←", font=('Helvetica 16'), command=lambda: [screen.delete("all"), screen.update(), backButton.destroy(), homeScreen()])
    backButton.place(x=40, y=(HEIGHT-80))

    # set up game objects
    setInitialValues()
    
    # game variables
    score_p1 = 0
    score_p2 = 0

    running = True

    # game loop
    while running:

        # check goal/win conditions
        score_p1, score_p2, reset = checkWin(score_p1, score_p2)
        
        # end game
        if score_p1 == 2 or score_p2 == 2:
            endGame()
            return

        # reset map when goal is scored
        if reset:
            resetMap()

        # draw, update, sleep, delete
        score_p1_text, score_p2_text = drawObjects(score_p1, score_p2)
        if selected:
            impulse_circle = screen.create_oval(selected.x-100, selected.y-100, selected.x+100, selected.y+100, outline="linen", fill="")
            impulse_line = screen.create_line(selected.x, selected.y, selected.x+impulse_aim[0], selected.y+impulse_aim[1], fill="linen")

        screen.update()
        sleep(FPS)

        deleteObjects(score_p1_text, score_p2_text)
        if selected:
            screen.delete(impulse_circle)
            screen.delete(impulse_line)

        # update object positions
        updateObjects()  

    return


def aboutScreen():
    # display information on new screen
    background = screen.create_rectangle(0, 0, WIDTH, HEIGHT, outline="MediumPurple4", fill="MediumPurple4")
    aboutTitle = screen.create_text(MIDW, 170, text="ABOUT", fill="cornflower blue", font=('Helvetica 86 bold'))
    aboutText1 = screen.create_text(MIDW, 350, fill="white", justify=CENTER, text="Welcome to Air Soccer. Combining features from air hockey, billiards, and soccer,\nthis tactically challenging game is created to put your precision and accuracy to the test.\nHere are the rules:", font=('Helvetica 16'))
    aboutText2 = screen.create_text(MIDW, 500, fill="white", justify=LEFT, text="Objective: Score 2 goals in the opponent's net to win\n\nHow to play: This is a turn based game. Each player has 3 puck players that they can manipulate\nby selecting one and clicking to apply an impulse indicated through a guideline.\nProve your impressive physics skills by calculating angles to score on your opponent.", font=('Helvetica 16'))
  
    # button allows return to homeScreen 
    backButton = Button(screen, text="←", font=('Helvetica 16'), command=lambda: [screen.delete(background, aboutTitle, aboutText1, aboutText2), playButton.place(x=MIDW-50, y=(MIDH+MIDH//2)), aboutButton.place(x=MIDW-180, y=(MIDH+MIDH//2+7)), exitButton.place(x=MIDW+120, y=(MIDH+MIDH//2+7)), backButton.destroy()])
    backButton.place(x=40, y=(HEIGHT-80))


def homeScreen():
    global running, username_p1, username_p2, playButton, aboutButton, exitButton

    # game is not running
    running = False

    # player usernames
    username_p1 = "PLAYER 1"
    username_p2 = "PLAYER 2"

    # title text
    screen.create_text(MIDW - 250, MIDH-20, text="AIR", fill="cornflower blue", font=('Helvetica 86 bold'))
    screen.create_text(MIDW + 100, MIDH-20, text="SOCCER", fill="coral", font=('Helvetica 86 bold'))

    # button begins game
    playButton = Button(screen, text="PLAY", font=('Helvetica 24'), command=lambda: [exitButton.destroy(), aboutButton.destroy(), playButton.destroy(), runGame()])
    playButton.place(x=MIDW-50, y=(MIDH+MIDH//2))

    # button shows description of game
    aboutButton = Button(screen, text="About", font=('Helvetica 16'), command=lambda: [playButton.place_forget(), aboutButton.place_forget(), exitButton.place_forget(), aboutScreen()])
    aboutButton.place(x=MIDW-180, y=(MIDH+MIDH//2+7))

    # button ends program
    exitButton = Button(screen, text="Exit", font=('Helvetica 16'), command=quit)
    exitButton.place(x=MIDW+120, y=(MIDH+MIDH//2+7))




# call homeScreen function
root.after( 0, homeScreen )

# connect user inputs to functions
screen.bind( "<Button-1>", mouseClickHandler )
screen.bind( "<Motion>", motion )

screen.pack()
screen.focus_set()
root.mainloop()
