import pygame
import time
import random
import os

from numpy import *
from numpy.random import *

pygame.surfarray.use_arraytype('numpy')


os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()
WINSIZE = [900, 800]
screen = pygame.display.set_mode(WINSIZE, pygame.FULLSCREEN)
                                 # pygame.HWSURFACE|pygame.OPENGL|pygame.DOUBLEBUF) NOFRAME |pygame.DOUBLEBUF
clock = pygame.time.Clock()
fps = 1000
#milliseconds from last frame
new_time, old_time = None, None

done = False

while not done:
    clock.tick(200)

    for event in pygame.event.get():
        if event.type == pygame.KEYUP:
            done = True

    # show fps and milliseconds
    if new_time:
        old_time = new_time
    new_time = int(time.time() * 1000)
    #pygame.time.get_ticks()
    if new_time and old_time:
        #pygame.display.set_caption("fps: " + str(int(clock.get_fps())) + " ms: " + str(new_time-old_time))

        print str(int(clock.get_fps()))
        #print new_time-old_time

    # pygame.draw.rect(screen, (22,220,220), pygame.Rect(
    #     random.randint(100, 500),
    #     random.randint(100, 500),
    #     random.randint(10, 50),
    #     random.randint(10, 50),
    # ), False)

    pygame.display.flip()
