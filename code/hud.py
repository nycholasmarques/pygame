import pygame

class HUD:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.SysFont('Arial', 24)
        self.heart_img = pygame.Surface((30, 30))
        self.heart_img.fill((255, 0, 0))
    
    def draw(self, screen):
        # Barra de vida
        health_width = 200 * (self.player.health / self.player.max_health)
        pygame.draw.rect(screen, (255, 0, 0), (10, 10, health_width, 20))
        pygame.draw.rect(screen, (255, 255, 255), (10, 10, 200, 20), 2)
        
        # Texto de vida
        health_text = self.font.render(f"{self.player.health}/{self.player.max_health}", True, (255, 255, 255))
        screen.blit(health_text, (220, 10))
        
        # Ícones de vida (opcional)
        for i in range(int(self.player.health / 20)):
            screen.blit(self.heart_img, (10 + i*35, 40))