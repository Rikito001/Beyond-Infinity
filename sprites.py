import pygame
from settings import *


class Spike(pygame.sprite.Sprite):
    def __init__(self, pos, is_top, groups):
        super().__init__(groups)
        self.image = pygame.Surface((SPIKE_SIZE, SPIKE_SIZE), pygame.SRCALPHA)
        if is_top:
            pygame.draw.polygon(self.image, (0, 0, 0),
                                [(SPIKE_SIZE // 2, SPIKE_SIZE), (SPIKE_SIZE, 0), (0, 0)])
        else:
            pygame.draw.polygon(self.image, (0, 0, 0),
                                [(SPIKE_SIZE // 2, 0), (SPIKE_SIZE, SPIKE_SIZE), (0, SPIKE_SIZE)])

        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pygame.Vector2(self.rect.topleft)

    def update(self, delta):
        self.pos.x -= SCROLL_SPEED * delta
        self.rect.x = self.pos.x
        if self.rect.right < 0:
            self.kill()