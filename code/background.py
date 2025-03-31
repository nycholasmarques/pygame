import pygame

class Background:
    def __init__(self, image_path, screen_size):
        self.image = pygame.image.load(image_path).convert()
        self.image = pygame.transform.scale(self.image, screen_size)
        self.width = self.image.get_width()
    
    def draw(self, screen, camera_x=0):
        # Repete o fundo para simular movimento infinito
        offset_x = -(camera_x % self.width)
        screen.blit(self.image, (offset_x, 0))
        if offset_x < 0:
            screen.blit(self.image, (offset_x + self.width, 0))