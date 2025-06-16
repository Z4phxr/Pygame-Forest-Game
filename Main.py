import pygame, sys
from Maps import LEVELS
from Images import IMAGES
from Settings import *
from Level import Level


screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock  = pygame.time.Clock()
    current_lvl = None
    level = None
    selected_lvl = 0
    state = "MAIN_MENU"
    running = True

    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                print(level.obstacles)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if state == "MAIN_MENU":
                    if start_rect.collidepoint(mx, my):
                        state = "LEVEL_SELECT"

                elif state == "LEVEL_SELECT":
                    for lvl_name, (rect, mapa) in LEVELS.items():
                        if rect.collidepoint(mx, my):
                            selected_lvl = lvl_name
                            current_lvl = int(lvl_name.split('_')[1])
                            level = Level(mapa, current_lvl)  # przekazujemy listę znaków, nie współrzędną
                            state = "PLAY"
                            break
                    if lvl_menu_rect.collidepoint(mx, my):
                        state = "MAIN_MENU"

                elif state == "GAME_OVER_WON":
                    if restart_rect.collidepoint(mx, my):
                        current_lvl = int(current_lvl) + 1
                        next_lvl_key = f"LEVEL_{current_lvl}"
                        selected_lvl = next_lvl_key  # <--- TO DODAJ
                        if next_lvl_key in LEVELS:
                            level = Level(LEVELS[next_lvl_key][1], current_lvl)
                            state = "PLAY"
                        else:
                            # jeśli poziomu nie ma, wróć do menu lub zakończ
                            state = "MAIN_MENU"
                            start_music()

                elif state == "GAME_OVER_LOST":
                    if next_rect.collidepoint(mx, my):
                        level = Level(LEVELS[selected_lvl][1], current_lvl)
                        state = "PLAY"
                    elif menu_rect1.collidepoint(mx, my):
                        state = "MAIN_MENU"
                        stop_music()
                elif state == "PLAY":
                    if game_menu_rect.collidepoint(mx, my):
                        state = "MAIN_MENU"
                        stop_music()
                    elif game_restart_rect.collidepoint(mx, my):
                        state = "PLAY"
                        level = Level(LEVELS[f"LEVEL_{current_lvl}"][1], current_lvl)

        if state == "MAIN_MENU":
            screen.blit(IMAGES["FOREST"], (0, 0))

        elif state == "LEVEL_SELECT":
            screen.blit(IMAGES["LEVELS"], (0, 0))

        elif state == "PLAY":
            level.update(keys)
            level.draw(screen)
            if not level.running:
                state = "GAME_OVER_LOST"
                if level.won:
                    state = 'GAME_OVER_WON'

        elif state == "GAME_OVER_WON":
            screen.blit(IMAGES["OVERLAY"], (0, 0))
            screen.blit(IMAGES["YOU_WON"], (0,0))
        elif state == "GAME_OVER_LOST":
            screen.blit(IMAGES["OVERLAY"], (0, 0))
            screen.blit(IMAGES["GAME_OVER"], (0,0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
