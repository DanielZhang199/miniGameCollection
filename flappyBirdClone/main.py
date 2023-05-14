import pygame
import player

pygame.init()
# SCALE = get_scale()

infoObject = pygame.display.Info()
SCREEN = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN)

SCALE_Y = infoObject.current_h / 720
SCALE_X = infoObject.current_w / 1280
running = True

player = player.Player(500, 400, SCALE_Y)

while running:
    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
            elif event.key == pygame.K_ESCAPE:
                running = False

    # Fill the background with dark gray
    SCREEN.fill((63, 63, 63))

    # Draw player
    pygame.draw.circle(SCREEN, (0, 0, 255), (player.get_x(), player.get_y()), 25 * SCALE_Y)

    # Update the display
    pygame.display.flip()

    pygame.time.Clock().tick(60)
    player.tick()

pygame.quit()
