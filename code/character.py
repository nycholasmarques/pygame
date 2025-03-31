import pygame
import os

class Character:
    def __init__(self, x, y, sprites_path=None, animation_frames=None, speed=3, is_enemy=False):
        self.x = x
        self.y = y
        self.vel_x = speed
        self.vel_y = 0
        self.gravity = 0.5
        self.jump_strength = -12
        self.is_jumping = False
        self.is_running = False
        self.is_shooting = False
        self.facing_right = True
        self.is_enemy = is_enemy
        self.health = 100
        self.max_health = 100
        self.attack_damage = 10 if not is_enemy else 15
        self.projectiles = []
        self.is_attacking = False
        self.attack_cooldown = 0
        self.is_animating = False
        self.is_dead = False

        self.animations = {}
        self.animation_frames = {}
        self.current_action = "idle"
        self.frame_index = 0
        self.frame_delay = 5
        self.frame_counter = 0
        self.hitbox_offset_x = 49
        self.hitbox_offset_y = 68
        self.hitbox_width = 30
        self.hitbox_height = 60
        self.FRAME_WIDTH = 25
        self.FRAME_HEIGHT = 25

        if sprites_path and animation_frames:
            self.load_sprites(sprites_path, animation_frames)

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        if self.health <= 0 and self.current_action != "dead":
            self.current_action = "dead"
            self.frame_index = 0
            self.is_animating = True
        return self.health <= 0

    def shoot(self):
        if self.attack_cooldown <= 0:
            if self.facing_right:
                gun_offset_x = 80
                gun_offset_y = 90
            else:
                gun_offset_x = 48
                gun_offset_y = 90

            self.projectiles.append({
                'x': self.x + gun_offset_x,
                'y': self.y + gun_offset_y,
                'direction': 1 if self.facing_right else -1,
                'speed': 10,
                'lifetime': 30
            })
            self.current_action = "shoot"
            self.frame_index = 0
            self.is_shooting = True
            self.is_animating = True
            self.attack_cooldown = 0.5

    def update_combat(self, dt, enemies, screen_width):
        """Atualiza projéteis e combate"""
        self.attack_cooldown = max(0, self.attack_cooldown - dt)

    def load_sprites(self, sprites_path, animation_frames):
        self.animations = {}
        for action, filename in sprites_path.items():
            if os.path.exists(filename):
                self.animations[action] = pygame.image.load(filename)
                print(f"Sprite carregado: {action} - {filename}, Size: {self.animations[action].get_size()}")
            else:
                print(f"Erro: Arquivo não encontrado - {filename}")
                self.animations[action] = pygame.Surface((50, 50))
        self.animations["dead"] = pygame.image.load("assets/character/Dead.png")
        print(f"Sprite carregado: dead - assets/character/Dead.png, Size: {self.animations['dead'].get_size()}")
        self.animation_frames = animation_frames
        self.animation_frames["dead"] = 4
        self.update_frame_size()

    def update_frame_size(self):
        """Atualiza tamanho dos frames e mantém hitbox fixa."""
        if self.animations:
            first_anim = next(iter(self.animations.values()))
            first_action = next(iter(self.animation_frames.keys()))
            self.FRAME_WIDTH = first_anim.get_width() // self.animation_frames[first_action]
            self.FRAME_HEIGHT = first_anim.get_height()
            print(f"FRAME_WIDTH: {self.FRAME_WIDTH}, FRAME_HEIGHT: {self.FRAME_HEIGHT}")
            print(f"Hitbox: {self.hitbox_width}x{self.hitbox_height} at offset ({self.hitbox_offset_x}, {self.hitbox_offset_y})")

    def get_frame(self, flip=False):
        """Retorna o frame atual da animação, invertido se necessário."""
        if self.current_action not in self.animations:
            return pygame.Surface((50, 50))

        sheet = self.animations[self.current_action]
        max_frames = self.animation_frames[self.current_action]
        actual_frame = min(self.frame_index, max_frames - 1)
        
        sheet_width = sheet.get_width()
        x_pos = actual_frame * self.FRAME_WIDTH
        
        if x_pos + self.FRAME_WIDTH > sheet_width:
            print(f"Error: Frame {actual_frame} exceeds {self.current_action} sprite sheet width ({sheet_width})")
            actual_frame = max_frames - 1
            x_pos = actual_frame * self.FRAME_WIDTH
        
        frame = sheet.subsurface((x_pos, 0, self.FRAME_WIDTH, self.FRAME_HEIGHT))
        return pygame.transform.flip(frame, flip, False)

    def update_animation(self):
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_counter = 0
            self.frame_index += 1
            max_frames = self.animation_frames[self.current_action]
            
            if self.current_action == "shoot":
                if self.frame_index >= max_frames:
                    keys = pygame.key.get_pressed()
                    move_x = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
                    self.current_action = "run" if (move_x != 0 and self.is_running) else "walk" if move_x != 0 else "idle"
                    self.frame_index = 0
                    self.is_shooting = False
                    self.is_animating = False
            elif self.current_action == "dead":
                if self.frame_index >= max_frames:
                    self.frame_index = max_frames - 1
                    self.is_dead = True
            else:
                self.frame_index %= max_frames

    def update_position(self, platforms, move_x):
        self.vel_y += self.gravity
        self.y += self.vel_y
        self.x += move_x * self.vel_x * (1.2 if self.is_running else 1)

        player_rect = pygame.Rect(
            self.x + self.hitbox_offset_x,
            self.y + self.hitbox_offset_y,
            self.hitbox_width,
            self.hitbox_height
        )

        for platform in platforms:
            platform_rect = pygame.Rect(*platform)
            if player_rect.colliderect(platform_rect):
                # Colisão por baixo (teto)
                if self.vel_y < 0 and player_rect.top < platform_rect.bottom:
                    self.y = platform_rect.bottom - self.hitbox_offset_y
                    self.vel_y = 0
                # Colisão por cima (chão)
                elif self.vel_y > 0 and player_rect.bottom > platform_rect.top:
                    self.y = platform_rect.top - self.hitbox_height - self.hitbox_offset_y
                    self.vel_y = 0
                    self.is_jumping = False
                elif move_x != 0:
                    # Verifica se a plataforma é alta demais para pular
                    if platform_rect.top < self.y + self.hitbox_offset_y - self.jump_strength * 10:
                        if move_x > 0 and player_rect.right > platform_rect.left and player_rect.left < platform_rect.left:
                            self.x = platform_rect.left - self.hitbox_width - self.hitbox_offset_x
                        elif move_x < 0 and player_rect.left < platform_rect.right and player_rect.right > platform_rect.right:
                            self.x = platform_rect.right - self.hitbox_offset_x
                    else:
                        self.y = platform_rect.top - self.hitbox_height - self.hitbox_offset_y
                        self.vel_y = 0
                        self.is_jumping = False

        self.vel_y = min(self.vel_y, 10)

    def draw(self, screen, camera_x=0):
        flip = not self.facing_right if not self.is_enemy else self.facing_right 
        frame = self.get_frame(flip)
        screen.blit(frame, (self.x - camera_x, self.y))