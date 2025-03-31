import pygame
import os
from character import Character


class Zombie(Character):
    def __init__(self, x, y):
        self.zombie_frames = self.load_all_frames()

        super().__init__(
            x=x, y=y, sprites_path=None, animation_frames=None, speed=2, is_enemy=True
        )

        self.current_action = "idle"
        self.frame_index = 0
        self.animation_speed = 0.2
        self.frame_time = 0
        self.attack_cooldown = 0
        self.attack_range = 50  # Reduzido para consistência
        self.is_dead = False
        self.health = 30

        if self.zombie_frames["idle"]:
            self.FRAME_WIDTH = self.zombie_frames["idle"][0].get_width()
            self.FRAME_HEIGHT = self.zombie_frames["idle"][0].get_height()

        self.hitbox_offset_x = 20  # Fixado para simetria
        self.hitbox_offset_y = self.FRAME_HEIGHT - 60
        self.hitbox_width = 40  # Reduzido para evitar alcance excessivo
        self.hitbox_height = 60

        self.render_x = x
        self.render_y = y
        self.smoothing_factor = 0.2

    def load_all_frames(self):
        frames = {
            "idle": self.load_frames("assets/zombie/Idle.png", 8),
            "walk": self.load_frames("assets/zombie/Walk.png", 8),
            "attack": self.load_frames("assets/zombie/Attack_1.png", 5),
            "dead": self.load_frames("assets/zombie/Dead.png", 5),
        }
        return frames

    def load_frames(self, path, frame_count):
        try:
            if not os.path.exists(path):
                print(f"ERRO: Arquivo não encontrado - {os.path.abspath(path)}")
                return []
            sheet = pygame.image.load(path)
            width = sheet.get_width() // frame_count
            height = sheet.get_height()
            return [
                sheet.subsurface((i * width, 0, width, height))
                for i in range(frame_count)
            ]
        except Exception as e:
            print(f"Erro ao carregar {path}: {e}")
            return [
                pygame.Surface((50, 50), pygame.SRCALPHA) for _ in range(frame_count)
            ]

    def get_frame(self, flip=False):
        try:
            frames = self.zombie_frames.get(self.current_action, [])
            if not frames:
                return pygame.Surface((50, 50), pygame.SRCALPHA)
            frame = frames[min(self.frame_index, len(frames) - 1)]
            return pygame.transform.flip(frame, flip, False)
        except Exception as e:
            print(f"Erro no get_frame: {e}")
            return pygame.Surface((50, 50), pygame.SRCALPHA)

    def update_animation(self, dt):
        if not self.zombie_frames.get(self.current_action):
            return
        self.frame_time += dt
        frames = self.zombie_frames[self.current_action]
        if self.frame_time >= self.animation_speed:
            self.frame_time -= self.animation_speed
            self.frame_index += 1
            if self.current_action == "dead":
                if self.frame_index >= len(frames):
                    self.is_dead = True
                    self.frame_index = len(frames) - 1
            elif self.current_action == "attack" and self.frame_index >= len(frames):
                self.current_action = "idle"
                self.frame_index = 0
            else:
                self.frame_index %= len(frames)

    def update_ai(self, player, dt, platforms):
        if self.current_action == "dead" or self.is_dead:
                if self.current_action == "dead" and self.frame_index >= len(self.zombie_frames["dead"]) - 1:
                    self.is_dead = True
                return

        if self.health <= 0:
                print("Zumbi morreu, iniciando animação de morte")
                self.current_action = "dead"
                self.frame_index = 0
                self.vel_x = 0
                return

        player_rect = pygame.Rect(
            player.x + player.hitbox_offset_x,
            player.y + player.hitbox_offset_y,
            player.hitbox_width,
            player.hitbox_height,
        )
        zombie_rect = pygame.Rect(
            self.x + self.hitbox_offset_x,
            self.y + self.hitbox_offset_y,
            self.hitbox_width,
            self.hitbox_height,
        )

        player_on_platform = False
        zombie_on_platform = False
        for platform in platforms:
            plat_rect = pygame.Rect(platform[0], platform[1], platform[2], platform[3])
            if player_rect.colliderect(plat_rect) or (
                player_rect.bottom == plat_rect.top
                and plat_rect.collidepoint(player_rect.midbottom)
            ):
                player_on_platform = platform
            if zombie_rect.colliderect(plat_rect) or (
                zombie_rect.bottom == plat_rect.top
                and plat_rect.collidepoint(zombie_rect.midbottom)
            ):
                zombie_on_platform = platform

        if player_on_platform != zombie_on_platform:
            self.current_action = "idle"
            return

        dist_x = player.x - self.x
        dist_y = player.y - self.y
        self.facing_right = dist_x > 0

        # Ataque baseado em colisão direta para consistência
        if zombie_rect.colliderect(player_rect):
            if self.attack_cooldown <= 0:
                self.current_action = "attack"
                self.frame_index = 0
                player.take_damage(self.attack_damage)
                self.attack_cooldown = 1.0
            else:
                self.attack_cooldown -= dt
                if self.current_action != "attack":
                    self.current_action = "idle"
            return

        if abs(dist_x) > 20:
            self.current_action = "walk"
            if abs(dist_y) < 50:
                move_speed = self.vel_x * dt * 60
                self.x += move_speed if dist_x > 0 else -move_speed
            else:
                self.current_action = "idle"
        else:
            self.current_action = "idle"

    def update_position(self, platforms):
        self.vel_y += self.gravity
        self.y += self.vel_y
        self.render_x += (self.x - self.render_x) * self.smoothing_factor
        self.render_y += (self.y - self.render_y) * self.smoothing_factor

        hitbox = pygame.Rect(
            self.x + self.hitbox_offset_x,
            self.y + self.hitbox_offset_y,
            self.hitbox_width,
            self.hitbox_height,
        )

        for platform in platforms:
            plat_rect = pygame.Rect(*platform)
            if hitbox.colliderect(plat_rect):
                if self.vel_y > 0 and hitbox.bottom > plat_rect.top:
                    self.y = plat_rect.top - self.hitbox_height - self.hitbox_offset_y
                    self.vel_y = 0
                    self.is_jumping = False
                elif self.vel_y < 0 and hitbox.top < plat_rect.bottom:
                    self.y = plat_rect.bottom - self.hitbox_offset_y
                    self.vel_y = 0
        self.vel_y = min(self.vel_y, 10)

    def draw(self, screen, camera_x=0):
        if not hasattr(self, "zombie_frames") or not self.zombie_frames.get(
            self.current_action
        ):
            return
        flip = not self.facing_right
        frame = self.get_frame(flip)
        screen.blit(frame, (round(self.render_x - camera_x), round(self.render_y)))
        try:
            if (
                DEBUG_MODE and not self.is_dead
            ):  # Só desenha hitbox se não estiver morto
                hitbox_rect = pygame.Rect(
                    self.x + self.hitbox_offset_x - camera_x,
                    self.y + self.hitbox_offset_y,
                    self.hitbox_width,
                    self.hitbox_height,
                )
                pygame.draw.rect(screen, (0, 255, 0), hitbox_rect, 1)
        except NameError:
            pass
