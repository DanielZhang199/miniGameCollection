import pygame
import player
import obstacle


if __name__ == "__main__":

    pygame.init()
    pygame.display.set_caption('Minimalist Flappy Bird')

    HEIGHT = 1440
    WIDTH = 2560
    FPS = 60

    MONITOR_SIZE = pygame.display.Info()
    WINDOW = pygame.display.set_mode((MONITOR_SIZE.current_w // 2, MONITOR_SIZE.current_h // 2), pygame.RESIZABLE)
    SCREEN = pygame.Surface((WIDTH, HEIGHT))

    OBSTACLE_INTERVAL = int(1.5 * FPS)
    PLAYER_X = 500
    PLAYER_START_Y = 400

    running = True
    player = player.Player(PLAYER_X, PLAYER_START_Y)
    obstacles = [obstacle.Obstacle()]
    cleared_obstacles = []
    obstacle_timer = OBSTACLE_INTERVAL
    score = 0
    font = pygame.font.SysFont('Impact.ttf', 120)
    fullscreen = False

    score_text = font.render("0", True, (0, 0, 0))
    text_rect = score_text.get_rect()
    text_rect.center = (WIDTH // 2, HEIGHT // 8)

    while running:
        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                WINDOW.blit(pygame.transform.scale(SCREEN, WINDOW.get_rect().size), (0, 0))
                pygame.display.flip()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F11:
                    if fullscreen:
                        WINDOW = pygame.display.set_mode((MONITOR_SIZE.current_w // 2, MONITOR_SIZE.current_h // 2),
                                                         pygame.RESIZABLE)
                    else:
                        WINDOW = pygame.display.set_mode((MONITOR_SIZE.current_w, MONITOR_SIZE.current_h),
                                                         pygame.FULLSCREEN)
                    fullscreen = not fullscreen

        SCREEN.fill((255, 238, 179))

        # Draw and update objects
        pygame.draw.rect(SCREEN, (184, 231, 225), pygame.Rect(player.get_x(), player.get_y(), 80, 80))
        player.tick()

        clone = obstacles.copy()
        for element in obstacles:
            dimensions = element.get_dimensions()
            if dimensions[0][0] < -100:
                clone.remove(element)
            pygame.draw.rect(SCREEN, (158, 111, 33), pygame.Rect(dimensions[0]))
            pygame.draw.rect(SCREEN, (158, 111, 33), pygame.Rect(dimensions[1]))
            result = element.tick((player.get_x(), player.get_y()))
            if result == 1:
                clone.remove(element)
                score = 0
            elif result == 2:
                score += 1
        obstacles = clone

        if obstacle_timer > 0:
            obstacle_timer -= 1
        else:
            obstacles.append(obstacle.Obstacle())
            obstacle_timer = OBSTACLE_INTERVAL

        # Show score
        score_text = font.render(str(score), True, (200, 155, 80))
        SCREEN.blit(score_text, text_rect)

        # Update the display
        WINDOW.blit(pygame.transform.scale(SCREEN, WINDOW.get_rect().size), (0, 0))
        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

    pygame.quit()
