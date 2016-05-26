import pygame

pygame.init()
WINSIZE = [1000, 1000]
screen = pygame.display.set_mode(WINSIZE)
clock = pygame.time.Clock()
fps = 1000
#milliseconds from last frame
new_time, old_time = None, None

done = False

while not done:
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # show fps and milliseconds
    if new_time:
        old_time = new_time
    new_time = pygame.time.get_ticks()
    if new_time and old_time:
        pygame.display.set_caption("fps: " + str(int(clock.get_fps())) + " ms: " + str(new_time-old_time))

    pygame.display.update()
