import pygame
from character import Character
from background import Background
from enemy import Zombie
from hud import HUD

# Constantes globais
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PLATFORM_COLOR = (33, 19, 19)
WORLD_LIMIT_RIGHT = 3000
CAMERA_FOLLOW_THRESHOLD = SCREEN_WIDTH // 2
DEBUG_MODE = False

def init_game():
    """Inicializa os elementos do jogo."""
    background = Background("assets/background/city4/9.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
    player = Character(
        x=100, y=400,
        sprites_path={
            "idle": "assets/character/Idle.png",
            "walk": "assets/character/Walk.png",
            "run": "assets/character/Run.png",
            "shoot": "assets/character/Shot_1.png"
        },
        animation_frames={"idle": 7, "walk": 7, "run": 7, "shoot": 4}
    )
    hud = HUD(player)
    platforms = [
        (0, 300, 50, 500),
        (50, 500, 600, 300),
        (700, 450, 500, 300),
        (1250, 400, 450, 350),
        (1850, 350, 600, 400),
        (2600, 450, 400, 300),
        (WORLD_LIMIT_RIGHT - 50, 0, 50, 450),
        (WORLD_LIMIT_RIGHT - 50, 550, 50, 50)
    ]
    enemies = [
        Zombie(x=700, y=430),
        Zombie(x=850, y=430),
        Zombie(x=1000, y=430), 
        Zombie(x=1250, y=380),
        Zombie(x=1400, y=380),
        Zombie(x=1850, y=330),
        Zombie(x=2000, y=330),
        Zombie(x=2150, y=330),
        Zombie(x=2600, y=430),
        Zombie(x=2750, y=430)
    ]
    return background, player, hud, platforms, enemies, 0

def draw_darkened_background(screen, background):
    """Desenha o background escurecido."""
    background.draw(screen, 0)
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

def draw_menu(screen, font, selected_option, background):
    """Desenha o menu principal."""
    draw_darkened_background(screen, background)
    title = font.render("Zumbi Survival", True, (255, 255, 255))
    start = font.render("Iniciar", True, (0, 255, 0) if selected_option == 0 else (255, 255, 255))
    quit = font.render("Sair", True, (0, 255, 0) if selected_option == 1 else (255, 255, 255))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
    screen.blit(start, (SCREEN_WIDTH // 2 - start.get_width() // 2, 300))
    screen.blit(quit, (SCREEN_WIDTH // 2 - quit.get_width() // 2, 350))

def draw_loser(screen, font, selected_option, background):
    """Desenha a tela de derrota."""
    draw_darkened_background(screen, background)
    message = font.render("Você Perdeu!", True, (255, 0, 0))
    menu = font.render("Voltar ao Menu", True, (0, 255, 0) if selected_option == 0 else (255, 255, 255))
    screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, 200))
    screen.blit(menu, (SCREEN_WIDTH // 2 - menu.get_width() // 2, 300))

def draw_victory(screen, font, selected_option, background, zombie_deaths):
    """Desenha a tela de vitória com contador de zumbis mortos."""
    draw_darkened_background(screen, background)
    message = font.render("Você conseguiu chegar ao ponto final", True, (255, 255, 255))
    zombie_count = font.render(f"Zumbis Mortos: {zombie_deaths}", True, (255, 255, 255))
    menu = font.render("Voltar ao Menu", True, (0, 255, 0) if selected_option == 0 else (255, 255, 255))
    screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, 200))
    screen.blit(zombie_count, (SCREEN_WIDTH // 2 - zombie_count.get_width() // 2, 250))
    screen.blit(menu, (SCREEN_WIDTH // 2 - menu.get_width() // 2, 300))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Zumbi Survival")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 50)
    small_font = pygame.font.SysFont(None, 30)  # Fonte menor para instruções

    state = "menu"
    selected_option = 0
    camera_x = 0
    death_timer = 0
    zombie_deaths = 0

    background = Background("assets/background/city4/9.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
    player, hud, platforms, enemies = None, None, None, None

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if state == "menu":
                    if event.key == pygame.K_UP:
                        selected_option = max(0, selected_option - 1)
                    elif event.key == pygame.K_DOWN:
                        selected_option = min(1, selected_option + 1)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 0:
                            state = "game"
                            background, player, hud, platforms, enemies, zombie_deaths = init_game()
                            camera_x = 0
                            death_timer = 0
                        elif selected_option == 1:
                            running = False
                elif state == "loser" or state == "victory":
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        selected_option = 0
                    elif event.key == pygame.K_RETURN:
                        state = "menu"
                        selected_option = 0

        if state == "menu":
            draw_menu(screen, font, selected_option, background)
            pygame.display.flip()

        elif state == "game":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_f] and player.attack_cooldown <= 0:
                player.shoot()

            player.is_running = keys[pygame.K_LSHIFT]
            move_x = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]

            if move_x != 0 and not player.is_dead:
                new_x = player.x + move_x * player.vel_x * (1.2 if player.is_running else 1)
                if 0 <= new_x <= WORLD_LIMIT_RIGHT:
                    player.x = new_x
                player.facing_right = move_x > 0
                if not player.is_animating:
                    player.current_action = "run" if player.is_running else "walk"
                if player.x - camera_x > CAMERA_FOLLOW_THRESHOLD:
                    camera_x = player.x - CAMERA_FOLLOW_THRESHOLD
                elif player.x - camera_x < CAMERA_FOLLOW_THRESHOLD // 2:
                    camera_x = max(0, player.x - CAMERA_FOLLOW_THRESHOLD // 2)
            else:
                if not player.is_animating and not player.is_dead:
                    player.current_action = "idle"

            if keys[pygame.K_SPACE] and not player.is_jumping and not player.is_dead:
                player.vel_y = player.jump_strength
                player.is_jumping = True

            player.update_animation()
            player.update_position(platforms, move_x if not player.is_dead else 0)
            if player.y > SCREEN_HEIGHT:
                player.take_damage(player.max_health)

            player.update_combat(dt, enemies, SCREEN_WIDTH)

            for zombie in enemies[:]:
                zombie.update_ai(player, dt, platforms)
                zombie.update_animation(dt)
                zombie.update_position(platforms)
                if zombie.is_dead and zombie.current_action == "dead" and zombie.frame_index >= len(zombie.zombie_frames["dead"]) - 1:
                    enemies.remove(zombie)
                    zombie_deaths += 1

            if player.is_dead:
                death_timer += dt
                if death_timer >= 2.0:
                    state = "loser"
                    selected_option = 0
                    death_timer = 0

            screen.fill((0, 0, 0))
            background.draw(screen, camera_x)
            for platform in platforms:
                platform_rect = (platform[0] - camera_x, platform[1], platform[2], platform[3])
                pygame.draw.rect(screen, PLATFORM_COLOR, platform_rect)

            for proj in player.projectiles[:]:
                proj['x'] += proj['speed'] * proj['direction']
                proj['lifetime'] -= dt
                proj_x = proj['x'] - camera_x
                pygame.draw.rect(screen, (255, 0, 0), (proj_x, proj['y'], 10, 5))
                if proj_x < -10 or proj_x > SCREEN_WIDTH + 10 or proj['lifetime'] <= 0:
                    player.projectiles.remove(proj)
                    continue
                proj_rect = pygame.Rect(proj['x'], proj['y'], 10, 5)
                for platform in platforms:
                    platform_rect = pygame.Rect(platform[0], platform[1], platform[2], platform[3])
                    if proj_rect.colliderect(platform_rect):
                        player.projectiles.remove(proj)
                        break
                else:
                    for enemy in enemies:
                        if not enemy.is_dead:
                            enemy_rect = pygame.Rect(
                                enemy.x + enemy.hitbox_offset_x,
                                enemy.y + enemy.hitbox_offset_y,
                                enemy.hitbox_width,
                                enemy.hitbox_height
                            )
                            if proj_rect.colliderect(enemy_rect):
                                enemy.take_damage(player.attack_damage)
                                player.projectiles.remove(proj)
                                break

            for zombie in enemies:
                zombie.draw(screen, camera_x)
            player.draw(screen, camera_x)
            hud.draw(screen)

            # Exibe instruções no canto direito
            shoot_text = small_font.render("Atirar: F", True, (255, 255, 255))
            run_text = small_font.render("Correr: Shift", True, (255, 255, 255))
            screen.blit(shoot_text, (SCREEN_WIDTH - shoot_text.get_width() - 10, 10))
            screen.blit(run_text, (SCREEN_WIDTH - run_text.get_width() - 10, 40))

            if DEBUG_MODE:
                player_hitbox = pygame.Rect(
                    player.x + player.hitbox_offset_x - camera_x,
                    player.y + player.hitbox_offset_y,
                    player.hitbox_width,
                    player.hitbox_height
                )
                pygame.draw.rect(screen, (255, 0, 0), player_hitbox, 1)
                for zombie in enemies:
                    if not zombie.is_dead:
                        zombie_hitbox = pygame.Rect(
                            zombie.x + zombie.hitbox_offset_x - camera_x,
                            zombie.y + zombie.hitbox_offset_y,
                            zombie.hitbox_width,
                            zombie.hitbox_height
                        )
                        pygame.draw.rect(screen, (0, 255, 0), zombie_hitbox, 1)

            if player.x >= WORLD_LIMIT_RIGHT - 50 and player.y >= 450 and player.y <= 550:
                state = "victory"
                selected_option = 0

            pygame.display.flip()

        elif state == "loser":
            draw_loser(screen, font, selected_option, background)
            pygame.display.flip()

        elif state == "victory":
            draw_victory(screen, font, selected_option, background, zombie_deaths)
            pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()