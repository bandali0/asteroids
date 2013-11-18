"""
Simple asteroids clone written in Python
     _        _                 _     _     
    / \   ___| |_ ___ _ __ ___ (_) __| |___ 
   / _ \ / __| __/ _ \ '__/ _ \| |/ _` / __|
  / ___ \\__ \ ||  __/ | | (_) | | (_| \__ \
 /_/   \_\___/\__\___|_|  \___/|_|\__,_|___/
by Amin Bandali

"""
from __future__ import division
import math
import sys
import os
import datetime
import random
import pygame


##################################
# General Helper functions (START)
##################################

def load_image_convert_alpha(filename):
    """Load an image with the given filename from the images directory"""
    return pygame.image.load(os.path.join('images', filename)).convert_alpha()


def load_sound(filename):
    """Load a sound with the given filename from the sounds directory"""
    return pygame.mixer.Sound(os.path.join('sounds', filename))


def draw_centered(surface1, surface2, position):
    """Draw surface1 onto surface2 with center at position"""
    rect = surface1.get_rect()
    rect = rect.move(position[0]-rect.width//2, position[1]-rect.height//2)
    surface2.blit(surface1, rect)


def rotate_center(image, rect, angle):
        """rotate the given image around its center & return an image & rect"""
        rotate_image = pygame.transform.rotate(image, angle)
        rotate_rect = rotate_image.get_rect(center=rect.center)
        return rotate_image,rotate_rect


def distance(p, q):
    """Helper function to calculate distance between 2 points"""
    return math.sqrt((p[0]-q[0])**2 + (p[1]-q[1])**2)

################################
# General Helper functions (END)
################################


class GameObject(object):
    """All game objects have a position and an image"""
    def __init__(self, position, image, speed=0):
        # max speed should be 6.5
        self.image = image
        self.position = list(position[:])
        self.speed = speed

    def draw_on(self, screen):
        draw_centered(self.image, screen, self.position)

    def size(self):
        return max(self.image.get_height(), self.image.get_width())

    def radius(self):
        return self.image.get_width()/2


class Spaceship(GameObject):
    def __init__(self, position):
        """initializing an Spaceship object given it's position"""
        super(Spaceship, self).__init__(position,\
            load_image_convert_alpha('spaceship-off.png'))
        
        self.image_on = load_image_convert_alpha('spaceship-on.png')
        self.direction = [0, -1]
        self.is_throttle_on = False
        self.angle = 0

        # a list to hold the missiles fired by the spaceship
        # (that are active (on the screen))
        self.active_missiles = []

    def draw_on(self, screen):
        """Draw the spaceship on the screen"""

        # select the image, based on the fact that spaceship is accelerating
        # or not
        if self.is_throttle_on:
            new_image, rect = rotate_center(self.image_on, \
                self.image_on.get_rect(), self.angle)
        else:
            new_image, rect = rotate_center(self.image, \
                self.image.get_rect(), self.angle)
        
        draw_centered(new_image, screen, self.position)


    def move(self):
        """Do one frame's worth of updating for the object"""
        
        # calculate the direction from the angle variable
        self.direction[0] = math.sin(-math.radians(self.angle))
        self.direction[1] = -math.cos(math.radians(self.angle))

        # calculate the position from the direction and speed
        self.position[0] += self.direction[0]*self.speed
        self.position[1] += self.direction[1]*self.speed


    def fire(self):
        """create a new Missile and fire it!!"""

        # adjust the firing position of the missile based on the
        # angle of the spaceship.
        # adjust[] is used to help hold the position of the point
        # from where the missile should be fired. In other words,
        # for example missiles should be fired from the bottom of
        # the spaceship if it's facing down.
        adjust = [0, 0]
        adjust[0] = math.sin(-math.radians(self.angle))*self.image.get_width()
        adjust[1] = -math.cos(math.radians(self.angle))*self.image.get_height()

        # create a new missile using the calculated adjusted position
        new_missile = Missile((self.position[0]+adjust[0],\
                               self.position[1]+adjust[1]/2),\
                               self.angle)
        self.active_missiles.append(new_missile)



class Missile(GameObject):
    """Resembles a missile"""
    def __init__(self, position, angle, speed=15):
        super(Missile, self).__init__(position,\
            load_image_convert_alpha('missile.png'))

        self.angle = angle
        self.direction = [0, 0]
        self.speed = speed        


    def move(self):
        """Move the missile towards its destination"""

        # calculate the direction from the angle variable
        self.direction[0] = math.sin(-math.radians(self.angle))
        self.direction[1] = -math.cos(math.radians(self.angle))

        # calculate the position from the direction and speed
        self.position[0] += self.direction[0]*self.speed
        self.position[1] += self.direction[1]*self.speed

        
    
class Rock(GameObject):
    """Resembles a rock"""
    def __init__(self, position, size, speed=4):
        """Initialize a Rock object, given its position and size"""

        # if the size is valid
        if size in {"big", "normal", "small"}:

            # load the correct image from file
            str_filename = "rock-" + str(size) + ".png"
            super(Rock, self).__init__(position,\
                load_image_convert_alpha(str_filename))
            self.size = size
        
        else:
            # the size is not pre-defined
            return None

        self.position = list(position)

        self.speed = speed
        
        # create a random movement direction vector
        if bool(random.getrandbits(1)):
            rand_x = random.random()* -1
        else:
            rand_x = random.random()
        
        if bool(random.getrandbits(1)):
            rand_y = random.random() * -1
        else:
            rand_y = random.random()

        self.direction = [rand_x, rand_y]


    def move(self):
        """Move the rock"""

        self.position[0] += self.direction[0]*self.speed
        self.position[1] += self.direction[1]*self.speed



class MyGame(object):

    # defining and initializing game states
    PLAYING, DYING, GAME_OVER, STARTING, WELCOME = range(5)

    # defining custom events
    REFRESH, START, RESTART = range(pygame.USEREVENT, pygame.USEREVENT+3)

    def __init__(self):
        """Initialize a new game"""
        pygame.mixer.init()
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()

        # set up a 800 x 600 window
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))

        # use a black background
        self.bg_color = 0, 0, 0

        # loading the sound track for the game
        self.soundtrack = load_sound('soundtrack.wav')
        self.soundtrack.set_volume(.3)

        # loading the dying, game over and missile sounds
        self.die_sound = load_sound('die.wav')
        self.gameover_sound = load_sound('game_over.wav')
        self.missile_sound = load_sound('fire.wav')

        # get the default system font (with different sizes of 100, 50, 25)
        self.big_font = pygame.font.SysFont(None, 100)
        self.medium_font = pygame.font.SysFont(None, 50)
        self.small_font = pygame.font.SysFont(None, 25)
        # and make the game over text using the big font just loaded
        self.gameover_text = self.big_font.render('GAME OVER',\
            True, (255, 0, 0))

        # load a spaceship image (only used to display number of lives)
        self.lives_image = load_image_convert_alpha('spaceship-off.png')

        # Setup a timer to refresh the display FPS times per second
        self.FPS = 30
        pygame.time.set_timer(self.REFRESH, 1000//self.FPS)

        # a dictionary of death distances of different rock sizes
        self.death_distances = {"big":90,"normal":65 ,"small":40}

        # display the welcome screen
        self.do_welcome()

        # used to monitor missile firing time
        # to prevent firing too many missiles in a short time
        self.fire_time = datetime.datetime.now()


    def do_welcome(self):
        """make a welcome screen"""

        # go to WELCOME state
        self.state = MyGame.WELCOME

        # making the welcome title and description
        self.welcome_asteroids = self.big_font.render("Asteroids",\
                                                True, (255, 215, 0))
        self.welcome_desc =  self.medium_font.render(\
            "[Click anywhere/press Enter] to begin!", True, (35, 107, 142))


    def do_init(self):
        """This function is called in the beginning or when
        the game is restarted."""

        # holds the rocks
        self.rocks = []

        # minimum distance from spaceship when making rocks
        # this changes based on difficulty as the time passes
        self.min_rock_distance = 350

        # starting the game
        self.start()

        # create 4 big rocks
        for i in range(4):
            self.make_rock()

        # initialize the number of lives and the score
        self.lives = 3
        self.score = 0

        # counter used to help count seconds
        self.counter = 0
    

    def make_rock(self, size="big", pos=None):
        """Make a new rock"""

        # minimum margin when creating rocks
        margin = 200

        if pos == None:
            # no position was passed. make at a random location

            rand_x = random.randint(margin, self.width-margin)
            rand_y = random.randint(margin, self.height-margin)
            
            # while the co-ordinate is too close, discard it
            # and generate another one
            while distance((rand_x, rand_y), self.spaceship.position) < \
                    self.min_rock_distance:
                
                # choose another random co-ordinate
                rand_x = random.randint(0, self.width)
                rand_y = random.randint(0, self.height)

            temp_rock = Rock((rand_x, rand_y), size)

        else:
            # a position was given through arguments
            temp_rock = Rock(pos, size)

        # add the recently created rock the the actual rocks list
        self.rocks.append(temp_rock)


    def start(self):
        """Start the game by creating the spaceship object"""
        self.spaceship = Spaceship((self.width//2, self.height//2))
        self.missiles = []

        # start the sound track loop
        self.soundtrack.play(-1, 0, 1000)

        # set the state to PLAYING
        self.state = MyGame.PLAYING


    def run(self):
        """Loop forever processing events"""
        running = True
        while running:
            event = pygame.event.wait()

            # player is asking to quit
            if event.type == pygame.QUIT:
                running = False

            # time to draw a new frame
            elif event.type == MyGame.REFRESH:
                
                if self.state != MyGame.WELCOME:

                    keys = pygame.key.get_pressed()
                
                    if keys[pygame.K_SPACE]:
                        new_time = datetime.datetime.now()
                        if new_time - self.fire_time > \
                                datetime.timedelta(seconds=0.15):
                            # there should be a minimum of 0.15 delay between
                            # firing each missile

                            # fire a missile
                            self.spaceship.fire()

                            # play the sound
                            self.missile_sound.play()

                            # record the current fire time
                            self.fire_time = new_time

                    if self.state == MyGame.PLAYING:
                        # if the game is going on

                        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                            # when pressing "d" or "right arrow" rotate
                            # the spaceship clockwise by 10 degrees
                            self.spaceship.angle -= 10
                            self.spaceship.angle %= 360

                        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                            # when pressing "d" or "right arrow" rotate
                            # the spaceship counter clockwise by 10 degrees
                            self.spaceship.angle += 10
                            self.spaceship.angle %= 360

                        if keys[pygame.K_UP] or keys[pygame.K_w]:
                            # if "w" or "up arrow" is pressed,
                            # we should accelerate
                            self.spaceship.is_throttle_on = True
                            
                            # increase the speed
                            if self.spaceship.speed < 20:
                                self.spaceship.speed += 1
                        else:
                            # if the throttle key ("d" or "up")
                            # is not pressed, slow down
                            if self.spaceship.speed > 0:
                                self.spaceship.speed -= 1
                            self.spaceship.is_throttle_on = False

                        # if there are any missiles on the screen, process them
                        if len(self.spaceship.active_missiles) > 0:
                            self.missiles_physics()

                        # if there are any rocks, do their physics
                        if len(self.rocks) > 0:
                            self.rocks_physics()

                        # do the spaceship physics
                        self.physics()

                # draw everything
                self.draw()

            # resume after losing a life
            elif event.type == MyGame.START:
                pygame.time.set_timer(MyGame.START, 0) # turn the timer off
                if self.lives < 1:
                    self.game_over()
                else:
                    self.rocks = []
                    # make 4 rocks
                    for i in range(4):
                        self.make_rock()
                    # start again
                    self.start()

            # switch from game over screen to new game
            elif event.type == MyGame.RESTART:
                pygame.time.set_timer(MyGame.RESTART, 0) # turn the timer off
                self.state = MyGame.STARTING

            # user is clicking to start a new game
            elif event.type == pygame.MOUSEBUTTONDOWN \
                    and (self.state == MyGame.STARTING or\
                            self.state == MyGame.WELCOME):
                self.do_init()

            # user is pressing enter to start a new game
            elif event.type == pygame.KEYDOWN \
                    and event.key == pygame.K_RETURN and \
                        (self.state == MyGame.STARTING or \
                            self.state == MyGame.WELCOME):
                self.do_init()

            else:
                pass # an event type we don't handle            


    def game_over(self):
        """Losing a life"""
        self.soundtrack.stop()
        # play game over sound and wait for it to end before continuing
        self.state = MyGame.GAME_OVER
        self.gameover_sound.play()
        delay = int((self.gameover_sound.get_length()+1)*1000)
        pygame.time.set_timer(MyGame.RESTART, delay)


    def die(self):
        """Losing a life"""
        self.soundtrack.stop()
        # play dying sound and wait for it to end before continuing
        self.lives -= 1
        self.counter = 0        
        self.state = MyGame.DYING
        self.die_sound.play()
        delay = int((self.die_sound.get_length()+1)*1000)
        pygame.time.set_timer(MyGame.START, delay)


    def physics(self):
        """Do spaceship physics here"""
        
        if self.state == MyGame.PLAYING:

            # call the move function of the object
            self.spaceship.move()

            """Note that this is a good place to make the spaceship
            bounce for example, when it hits the walls (sides of screen)
            or make it not move out of screen when it reaches the borders.
            Due to lack of time, I can't implement any of them, but they are
            not hard to do at all."""


    def missiles_physics(self):
        """Do all the physics of missiles"""
        
        # if there are any active missiles
        if len(self.spaceship.active_missiles) >  0:
            for missile in self.spaceship.active_missiles:
                # move the missile
                missile.move()

                # check the collision with each rock
                for rock in self.rocks:
                    if rock.size == "big":
                        # if the missile hits a big rock, destroy it,
                        # make two medium sized rocks and give 20 scores
                        if distance(missile.position, rock.position) < 80:
                            self.rocks.remove(rock)
                            if missile in self.spaceship.active_missiles:
                                self.spaceship.active_missiles.remove(missile)
                            self.make_rock("normal", \
                                (rock.position[0]+10, rock.position[1]))
                            self.make_rock("normal", \
                                (rock.position[0]-10, rock.position[1]))
                            self.score += 20

                    elif rock.size == "normal":
                        # if the missile hits a medium sized rock, destroy it,
                        # make two small sized rocks and give 50 scores
                        if distance(missile.position, rock.position) < 55:
                            self.rocks.remove(rock)
                            if missile in self.spaceship.active_missiles:
                                self.spaceship.active_missiles.remove(missile)
                            self.make_rock("small", \
                                (rock.position[0]+10, rock.position[1]))
                            self.make_rock("small", \
                                (rock.position[0]-10, rock.position[1]))
                            self.score += 50
                    else:
                        # if the missile hits a small rock, destroy it,
                        # make one big rock if there are less than 10 rocks
                        # on the screen, and give 100 scores
                        if distance(missile.position, rock.position) < 30:
                            self.rocks.remove(rock)
                            if missile in self.spaceship.active_missiles:
                                self.spaceship.active_missiles.remove(missile)
                            
                            if len(self.rocks) < 10:
                                self.make_rock()
                            
                            self.score += 100


    def rocks_physics(self):
        """Move the rocks if there are any"""

        # if there are any rocks
        if len(self.rocks) > 0:

            for rock in self.rocks:
                # move the rock
                rock.move()


                # if the rock hits the spaceship, die once
                if distance(rock.position, self.spaceship.position) < \
                        self.death_distances[rock.size]:
                    self.die()

                # if the rock goes out of screen and there are less than
                # 10 rocks on the screen, create a new rock with the same size
                elif distance(rock.position, (self.width/2, self.height/2)) > \
                     math.sqrt((self.width/2)**2 + (self.height/2)**2):

                    self.rocks.remove(rock)
                    if len(self.rocks) < 10:
                        self.make_rock(rock.size)


    def draw(self):
        """Update the display"""
        # everything we draw now is to a buffer that is not displayed
        self.screen.fill(self.bg_color)
    
        # if we are not on the welcome screen
        if self.state != MyGame.WELCOME:

            # draw the spaceship
            self.spaceship.draw_on(self.screen)

            # if there are any active missiles draw them
            if len(self.spaceship.active_missiles) >  0:
                for missile in self.spaceship.active_missiles:
                    missile.draw_on(self.screen)

            # draw the rocks
            if len(self.rocks) >  0:
                for rock in self.rocks:
                    rock.draw_on(self.screen)

            # if we are in game play mode
            if self.state == MyGame.PLAYING:

                # increment the counter by 1
                self.counter += 1

                if self.counter == 20*self.FPS:
                # time to increase difficulty (20 secs without dying)

                    if len(self.rocks) < 15:  # keeping it sane
                        # add a new rock
                        self.make_rock()

                    # decrease the minimum rock creation distance
                    if self.min_rock_distance < 200:
                        self.min_rock_distance -= 50

                    # set the counter back to zero
                    self.counter = 0

            # create and display the text for score
            scores_text = self.medium_font.render(str(self.score),\
                                                    True, (0, 155, 0))
            draw_centered(scores_text, self.screen,\
                (self.width-scores_text.get_width(), scores_text.get_height()+\
                                                        10))

            # if the game is over, display the game over text
            if self.state == MyGame.GAME_OVER or self.state == MyGame.STARTING:
                draw_centered(self.gameover_text, self.screen,\
                                (self.width//2, self.height//2))

            # draw lives
            for i in range(self.lives):
                draw_centered(self.lives_image, self.screen,\
                    (self.lives_image.get_width()*i*1.2+40,\
                        self.lives_image.get_height()//2))

        else:
            # draw the welcome texts
            draw_centered(self.welcome_asteroids, self.screen,\
                (self.width//2, self.height//2\
                    -self.welcome_asteroids.get_height()))

            draw_centered(self.welcome_desc, self.screen,\
                (self.width//2, self.height//2\
                    +self.welcome_desc.get_height()))

        # flip buffers so that everything we have drawn gets displayed
        pygame.display.flip()


MyGame().run()
pygame.quit()
sys.exit()


# Sounds tracks from http://soundbible.com