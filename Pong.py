'''
Created on Apr 1, 2016

@author: Louis Barrett
contact: louisbarrett98@gmail.com
'''

from tkinter import Tk, Frame, Canvas

import time

isScore = "null"
prevKey = ""
key = ""

# These two variable ensure that the two keys 'w' ands 's' cannot be pressed at the same time.
# Without these there is a glitch with movement of the paddle
wPressed = False
sPressed = False

debug = False   #<-- Change this to see some probably useless debug output

"""
*****************
In progress, i.e. what to do next: Change size of paddles so they're smaller and possibly change bounce patterns or add
a "limit" to the bounce angle of the ball. Make the AI of the computer paddle much better (less jittery).
*****************
"""


class App:  # class which draws base stuff like the canvas which we will draw the ball

    def __init__(self, master):
        master.minsize(height=400, width=500)
        frame = Frame(master)  # initialize frame
        frame.place(height=400, width=500, relheight=400,
                    relwidth=500)  # <-- I would suggest drawing it or else nothing will show up

        self.canvas = Canvas(root, width=500, height=400, bd=0,
                             highlightthickness=0)  # Draw the canvas which is where everything is drawn
        self.canvas.place(x=0, y=0, height=400, width=500, in_=frame)  # Draw the canvas

        self.canvas.rsttimer = Timer()  # Caused issues with movement

        """""""""
        Game Props
        """""""""

        self.canvas.create_rectangle(0, 0, 500, 400, fill="black")  # Black background
        self.net = createRect(self.canvas, 240, -5, 20, 410, "white")  # White "net"

        """"""""""
        Game Objects
        """""""""
        self.ball = Ball(self.canvas, "white")  # Instantiates the ball class
        self.usrpaddle = Paddle(self.canvas, "white", 10, 10)  # Instantiates the paddle class for user
        self.cpupaddle = Paddle(self.canvas, "white", 460, 100)  # Instantiates the paddle class for cpu

        """"""""""
        Game Props cont. (this is here so that the ball will appear to go "under" the text)
        """""""""
        # Score for player
        self.userScore = self.canvas.create_text(200, 20, font=("Courier New", 36, "bold"), text=self.usrpaddle.score,
                                                 fill="white")
        # self.usrpts = Label(self.canvas, font=("Courier New", 36, "bold"), text="10", foreground="white", bg="black")
        # self.usrpts.place(x=173, y=5, in_=self.canvas)

        # Score for CPU
        self.cpuScore = self.canvas.create_text(300, 20, font=("Courier New", 36, "bold"), text=self.cpupaddle.score,
                                                fill="white")
        # self.cpupts = Label(self.canvas, font=("Courier New", 36, "bold"), text="10", foreground="white", bg="black")
        # self.cpupts.place(x=293, y=5, in_=self.canvas)

    def update(self):  # Update method to update the screen(i.e. move the ball or the paddle)
        self.usrpaddle.updateUser()
        self.canvas.itemconfigure(self.userScore, text=self.usrpaddle.score)
        self.cpupaddle.updateCPU(self.ball.id)
        self.canvas.itemconfigure(self.cpuScore, text=self.cpupaddle.score)
        self.ball.checkCollisions(self.usrpaddle.id)
        self.ball.checkCollisions(self.cpupaddle.id)
        # self.net.draw()

    def draw(self):
        self.cpupaddle.draw()
        self.usrpaddle.draw()
        self.ball.draw()


class createRect:  # I made a create rectangle class because I like using width and height better than the confusing bbox
    def __init__(self, canvas, x, y, w, l, color):
        self.canvas = canvas
        self.x = x
        self.y = y
        a = x + w
        b = y + l
        self.id = canvas.create_rectangle(x, y, a, b, fill=color)

    def draw(self):
        self.canvas.move(self.id, 0, 0)


class Timer:
    def __init__(self):
        self.running = False
        self.stopped = True
        self.tm = 0
        self.current_time = 0

    def start(self, ct):
        self.tm = ct
        self.current_time = time.time()

    def check(self):
        if time.time() < (self.current_time + self.tm):
            return False
        else:
            return True


class Ball:  # Ball class which holds all stuff for the ball on the screen
    def __init__(self, canvas, color):
        self.canvas = canvas
        self.isCollision = False
        self.id = canvas.create_oval(10, 10, 25, 25, fill=color, activeoutline="")
        # self.canvas.coords(self.id, 100, 100, 115, 115)
        self.canvas.move(self.id, 240, 200)
        self.velx = -4.5
        self.vely = 1.5
        self.timer = Timer()

    def draw(self):
        rect = self.canvas.coords(self.id)
        if (self.isCollision == False and self.canvas.rsttimer.check()):
            self.canvas.coords(self.id, (self.velx + rect[0]), (self.vely + rect[1]), (self.velx + rect[2]),
                               (self.vely + rect[3]))
        else:
            self.canvas.coords(self.id, 240, 200, 255, 215)
            # self.canvas.move(self.id, self.velx, self.vely)
            # print box[2] - box[0]
            # print box[3]

    def checkCollisions(self, item):
        circle = self.canvas.bbox(self.id)
        rect = self.canvas.bbox(item)
        collision = False

        """"""""""
        Collision detection formula:
        
        rect coords(from the very top left of rect): (x1, y1)
        w = width of rect
        l = length of rect
        
        circle coords(from the very top left of the bounding box of the circle): (x2, y2)
        lc = length of circle(the bounding box around the circle again): the diameter
        
        1) If the absolute value of (x1 - x2) is < w then: (This one checks if the x values intersected within the width of the rect, if so it moves on to the next step)
        
        2) If the (y2 + lc) is >= y1 then: (This one checks if any part of the y value of the circle is greater than the y value of the rect, if it is it moves on to the next step)
        
        3) If y2 < (y1 + l) then: (This one checks to see if any part of the y value of the circle is less than the very bottom end of the rect, if so we now have detected a collision!!)
        
        Also for reference:
        rect[0] is left X coord
        rect[1] is top Y coord
        rect[2] is right X coord
        rect[3] is bottom Y coord
        """""""""
        if abs(rect[0] - circle[0]) < (rect[2] - rect[0]):  # Step 1 as listed above
            if (circle[1] + (circle[3] - circle[1])) >= rect[1]:  # Step 2 as listed above
                if circle[1] < (rect[1] + (rect[3] - rect[1])):  # Step 3 as listed above
                    if self.timer.check():  # The timer just makes sure no collision happens too often(this fixed a glitch where the ball would sort of get stuck in the paddle)
                        if debug:
                            print ("Collision")

                        """""""""
                        This next section of code simulates the more "fluid" feel of the ball bouncing off of the paddle. So basically it alters the pitch or angle at which
                        the ball bounces off the paddles. It can hit an area in the "Top", "Middle", or "Bottom" of the paddle and then sets the bounce angle of the ball
                        based on that where the ball hits.
                        """""""""

                        # MIDDLE
                        if (circle[1] + ((circle[3] - circle[1]) / 2)) > (rect[1] + 30) and (
                            circle[1] + ((circle[3] - circle[1]) / 2)) < (rect[1] + 70):
                            if debug:
                                print (circle[1] + ((circle[3] - circle[1]) / 2))
                                print (rect[1] + 5)
                                print ("Middle")
                                
                            self.vely = self.vely * .9
                            self.velx = self.velx * -1
                            self.timer.start(1)
                            
                        # TOP
                        elif (circle[1] + ((circle[3] - circle[1]) / 2)) < (rect[1] + 30):
                            if debug:
                                print (circle[1] + ((circle[3] - circle[1]) / 2))
                                print (rect[1] + 5)
                                print ("Top edge")
                            
                            self.vely = self.vely * 1.2
                            self.velx = self.velx * -1
                            self.timer.start(1)

                            # BOTTOM
                        elif (circle[1] + ((circle[3] - circle[1]) / 2)) > (rect[1] + 70):
                            self.vely = self.vely * 1.2
                            self.velx = self.velx * -1
                            self.timer.start(1)
                            if debug:
                                print ("Bottom edge")

                        # Everything else. Which I believe is nothing because the aforementioned "Top", "Middle", and "Bottom" cover the length of the whole paddle
                        else:
                            self.velx = self.velx * -1
                            self.timer.start(1)
                            # self.vely = self.vely * -1

        global isScore  # declare that isScore is a global variable so we can use it here
        
        if debug:
            print (self.vely)
            
        if collision != True:
            if circle[0] <= 0:  # x value Collided behind User
                # self.canvas.itemconfig(self.id, state=HIDDEN)
                # self.canvas.move(self.id, 250, 0)
                isScore = "cpu"
                self.canvas.rsttimer.start(2)
                # self.velx = self.velx * -1
                self.velx = 4.5
                self.vely = 1.5
                self.draw()
                # self.canvas.itemconfig(self.id, state=NORMAL)
            elif circle[0] >= 483:  # x value Collided behind CPU
                isScore = "user"
                self.canvas.rsttimer.start(2)
                # self.velx = self.velx * -1
                self.velx = -4.5
                self.vely = 1.5
                self.draw()
                # self.canvas.move(self.id, self.velx, self.vely)
                # self.canvas.move(self.id, 0, 0)
            elif circle[1] >= 383:  # y value
                self.vely = self.vely * -1
                self.draw()
                # self.canvas.move(self.id, self.velx, self.vely)
                # self.canvas.move(self.id, 0, 0)
            elif circle[1] <= 0:  # y value
                self.vely = self.vely * -1
                self.draw()
                # self.canvas.move(self.id, self.velx, self.vely)
                # self.canvas.move(self.id, 0, 0)
            else:
                # self.canvas.move(self.id, self.velx, self.vely)
                pass


class Paddle:  # Paddle class which holds all stuff for the ball on the screen(can this be inherited for the paddle AI?)
    def __init__(self, canvas, color, x, y):
        self.canvas = canvas
        self.length = 50
        self.width = 20
        self.score = 0
        # 20 wide by 100 length
        self.id = canvas.create_rectangle(self.width, self.length, 10, 10, fill=color)
        self.canvas.move(self.id, x, y)
        self.velX = 0.0
        self.velY = 0.0

    def updateUser(self):
        global key
        global prevKey
        global isScore
        # print key

        # print(self.canvas.coords(self.id))

        if isScore == "user":
            self.score += 1
            isScore = "null"

        if key == "w":  # Moves paddle according to what key is pressed
            # self.canvas.move(self.id, 0, -5)
            self.velY = -5
            prevKey = "w"
        elif key == "s":  # Same as above
            # self.canvas.move(self.id, 0, 5)
            self.velY = 5
            prevKey = "s"
        else:
            # self.canvas.move(self.id, 0, 0)
            self.velY = 0
            prevKey = ""

    def updateCPU(self, item):
        obj = self.canvas.bbox(item)
        rect = self.canvas.bbox(self.id)
        global isScore

        if isScore == "cpu":
            self.score += 1
            isScore = "null"

        # FIX: fidgeting of cpu paddle

        if ((rect[1] + ((rect[3] - rect[1]) / 2)) < (
            obj[1] + ((obj[3] - obj[1]) / 2)) + 4 and self.canvas.rsttimer.check()):
            # self.canvas.move(self.id, 0, 0.2)
            self.velY = 4

        elif ((rect[1] + ((rect[3] - rect[1]) / 2)) > (
            obj[1] + ((obj[3] - obj[1]) / 2)) + 4 and self.canvas.rsttimer.check()):
            # self.canvas.move(self.id, 0, -0.2)
            self.velY = -4

        else:
            self.velY = 1
            if self.canvas.rsttimer.check() == False:
                self.velY = 0
                self.canvas.coords(self.id, 470, 155, 480, 195)

    def draw(self):
        rect = self.canvas.coords(self.id)
        bbox = self.canvas.bbox(self.id)

        if (bbox[1] + (bbox[3] - bbox[1])) >= 400 and self.velY > 0:
            pass
        elif bbox[1] <= 0 and self.velY < 0:
            pass
        else:
            # if(self.canvas.rsttimer.check() == False):
            self.canvas.coords(self.id, rect[0], (self.velY + rect[1]), rect[2], (self.velY + rect[3]))
            # else:
            # 460, 100
            # pass
            # self.canvas.coords(self.id, 460, 100, 480, 200)


root = Tk()
root.wm_title("Pong")
root.resizable(width=False, height=False)

app = App(root)  # run the app class that will draw frame and do everything else


def on_keypress(event):  # Key listener event which will return the key that was pressed
    global key
    global wPressed, sPressed  # <-- see reference for these variables at top of code
    key = event.keysym
    if key == "w":
        wPressed = True
        sPressed = False
    if key == "s":
        sPressed = True
        wPressed = False
    if key != "w" and key != "s":
        key = ""
        sPressed = False
        wPressed = False
        # app.update()
        # print "Pressed: ", key


def on_keyrelease(event):  # Makes sure that key is set to nothing when nothing is being pressed
    global key
    global wPressed, sPressed  # <-- see reference for these variables at top of code
    if event.keysym == "w" and sPressed:
        pass
    elif event.keysym == "s" and wPressed:
        pass
    elif event.keysym == "w" and wPressed:
        key = ""
        sPressed = False
        wPressed = False
    elif event.keysym == "s" and sPressed:
        key = ""
        wPressed = False
        sPressed = False
        # app.update()


root.bind_all("<KeyRelease>", on_keyrelease)
root.bind_all("<KeyPress>", on_keypress)

"""""""""
These next lines setup FPS in an OK way for this type of game. On a more resource intensive game you'd want to separate the
draw and update functions so that physics is updated constantly and the only thing that would vary on a slow computer would 
be the FPS. If you were to use this game loop on an extremely slow computer then it would just make everything(including the FPS and physics)
of the game really slow, but since this is just Pong it should do okay.
"""""""""

fps = 60  # FPS, pretty self explanatory
skipticks = 1 / fps  # how many ticks are we allowed to skip?

nexttick = time.time()  # gets the time when the game started

sleeptime = 0  # placeholder for later

while True:

    app.update()  # update the game; so basically update all variables, vectors, speeds, etc... Keep in mind this does not draw the objects to the screen
    app.draw()  # draw everything
    # root.update_idletasks() #update root
    root.update()  # update root

    # This next if statement basically sees how long we can wait before updating the screen again.
    nexttick += skipticks
    sleeptime = nexttick - time.time()
    if sleeptime >= 0:
        time.sleep(sleeptime)
    else:
        # Program is totes running behind
        pass


# root.mainloop()
# root.destroy() # needed for Wing...?? NAH
