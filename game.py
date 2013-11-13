"""Some simple skeleton code for a pygame game/animation

This skeleton sets up a basic 800x600 window, an event loop, and a
redraw timer to redraw at 30 frames per second.
"""
from __future__ import division
import math
import sys
import os
import datetime
import random
import pygame

def load_image(filename):
    """Load an image with the given filename from the images directory"""
    return pygame.image.load(os.path.join('images', filename))

def draw_centered(surface1, surface2, position):
    """Draw surface1 onto surface2 with center at position"""
    rect = surface1.get_rect()
    rect = rect.move(position[0]-rect.width//2, position[1]-rect.height//2)
    surface2.blit(surface1, rect)

def rotate_center(image, rect, angle):
        """rotate the given image around its center and return an image & rect"""
        rotate_image = pygame.transform.rotate(image, angle)
        rotate_rect = rotate_image.get_rect(center=rect.center)
        return rotate_image,rotate_rect

def distance(p, q):
    """Helper function to calculate distance between 2 points"""
    return math.sqrt((p[0]-q[0])**2 + (p[1]-q[1])**2)


class GameObject(object):
    """All game objects have a position and an image"""
    def __init__(self, position, image, speed=4):
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
        super(Spaceship, self).__init__(position, load_image('spaceship-off.png'))
        self.image_on = load_image('spaceship-on.png')
        self.direction = [0, -1]
        self.is_moving = False
        self.angle = 0

        self.active_missiles = []

    def draw_on(self, screen):
        """Draw the spaceship on the screen"""

        # select the image, based on the fact that spaceship is moving or not
        if self.is_moving:
            new_image, rect = rotate_center(self.image_on, self.image_on.get_rect(), self.angle)
        else:
            new_image, rect = rotate_center(self.image, self.image.get_rect(), self.angle)
        
        draw_centered(new_image, screen, self.position)


    def move(self):
        """Do one frame's worth of updating for the object"""
        
        self.direction[0] = math.sin(-math.radians(self.angle))
        self.direction[1] = -math.cos(math.radians(self.angle))

        self.position[0] += self.direction[0]*self.speed
        self.position[1] += self.direction[1]*self.speed


    def fire(self):
        """create a new Missile and fire it!!"""

        adjust = [0, 0]
        adjust[0] = math.sin(-math.radians(self.angle))*self.image.get_width()
        adjust[1] = -math.cos(math.radians(self.angle))*self.image.get_height()

        new_missile = Missile((self.position[0]+adjust[0],\
                               self.position[1]+adjust[1]/2),\
                               self.angle)
        self.active_missiles.append(new_missile)



class Missile(GameObject):
    """Resembles a missile"""
    def __init__(self, position, angle, speed=15):
        super(Missile, self).__init__(position, load_image('missile.png'))
        self.angle = angle
        self.direction = [0, 0]
        self.speed = speed        


    def move(self):
        """Move the missile towards its destination"""

        self.direction[0] = math.sin(-math.radians(self.angle))
        self.direction[1] = -math.cos(math.radians(self.angle))

        self.position[0] += self.direction[0]*self.speed
        self.position[1] += self.direction[1]*self.speed

        
    
class Rock(GameObject):
    """Resembles a rock"""
    def __init__(self, position, size):
        """Initialize a Rock object, given its position and size"""

        if size in {"big", "normal", "small"}:
            str_filename = "rock-" + str(size) + ".png"
            super(Rock, self).__init__(position, load_image(str_filename))
        else:
            return None

        self.position = position



class MyGame(object):
    def __init__(self):
        """Initialize a new game"""
        pygame.mixer.init()
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()

        # set up a 1024 x 768 window
        self.width = 1024
        self.height = 768
        self.screen = pygame.display.set_mode((self.width, self.height))

        # use a black background
        self.bg_color = 0, 0, 0

        # Setup a timer to refresh the display FPS times per second
        self.FPS = 30
        self.REFRESH = pygame.USEREVENT+1
        pygame.time.set_timer(self.REFRESH, 1000//self.FPS)

        self.spaceship = Spaceship((self.width//2, self.height//2))
        self.missiles = []

        self.rocks = []

        for i in range(4):
            self.make_rock()    

        self.fire_time = datetime.datetime.now()


    def make_rock(self):
        """Make a new rock"""

        margin = 200

        rand_x = random.randint(margin, self.width-margin)
        rand_y = random.randint(margin, self.height-margin)
        
        # while the co-ordinate is too close, discard it
        # and generate another one
        while distance((rand_x, rand_y), self.spaceship.position) < 350:
            # choose a random co-ordinate
            rand_x = random.randint(0, self.width)
            rand_y = random.randint(0, self.height)

        temp_rock = Rock((rand_x, rand_y), "big")
        self.rocks.append(temp_rock)

    def run(self):
        """Loop forever processing events"""
        running = True
        while running:
            event = pygame.event.wait()

            # player is asking to quit
            if event.type == pygame.QUIT:
                running = False

            # time to draw a new frame
            elif event.type == self.REFRESH:
                keys = pygame.key.get_pressed()
            
                if keys[pygame.K_SPACE]:
                    new_time = datetime.datetime.now()
                    if new_time - self.fire_time > datetime.timedelta(seconds=0.15):
                        self.spaceship.fire()
                        self.fire_time = new_time

                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.spaceship.angle -= 10
                    self.spaceship.angle %= 360
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.spaceship.angle += 10
                    self.spaceship.angle %= 360
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    self.physics()
                    self.spaceship.is_moving = True
                    # print self.spaceship.angle
                else:
                    self.spaceship.is_moving = False

                if len(self.spaceship.active_missiles) > 0:
                    self.missiles_physics()

                self.draw()

            else:
                pass # an event type we don't handle            


    def physics(self):
        """Do in-game physics here"""
        
        # call the move function of the object
        self.spaceship.move()

    def missiles_physics(self):
        
        # if there are any active missiles
        if len(self.spaceship.active_missiles) >  0:
            for missile in self.spaceship.active_missiles:
                missile.move()

                for rock in self.rocks:
                    if distance(missile.position, rock.position) < 70:
                        self.rocks.remove(rock)
                        self.spaceship.active_missiles.remove(missile)
                        self.make_rock()


    def draw(self):
        """Update the display"""
        # everything we draw now is to a buffer that is not displayed
        self.screen.fill(self.bg_color)
    
        self.spaceship.draw_on(self.screen)

        # if there are any active missiles
        if len(self.spaceship.active_missiles) >  0:
            for missile in self.spaceship.active_missiles:
                missile.draw_on(self.screen)

        # draw the rocks
        if len(self.rocks) >  0:
            for rock in self.rocks:
                rock.draw_on(self.screen)

        # flip buffers so that everything we have drawn gets displayed
        pygame.display.flip()


MyGame().run()
pygame.quit()
sys.exit()

