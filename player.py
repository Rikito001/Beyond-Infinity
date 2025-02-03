import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, groups, game):
        super().__init__(groups)
        self.game = game
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (0, 0, 0), [(0, PLAYER_SIZE), (PLAYER_SIZE, PLAYER_SIZE / 2), (0, 0)])
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.pos = pygame.Vector2(self.rect.center)
        self.initial_x = self.pos.x
        self.direction = pygame.Vector2(0, 1).normalize()
        self.going_up = False
        self.space_pressed = False
        self.alive = True

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not self.space_pressed:
            self.space_pressed = True
            self.going_up = not self.going_up
            self.direction.y = -1 if self.going_up else 1
            self.direction = self.direction.normalize()
        elif not keys[pygame.K_SPACE]:
            self.space_pressed = False

    def move(self, delta):
        # Vertical movement with game speed
        movement_speed = SCROLL_SPEED * self.game.speed_multiplier - 50
        self.pos.y += self.direction.y * movement_speed * delta
        self.pos.x = self.initial_x
        self.rect.center = self.pos

        if self.rect.top <= TUNNEL_TOP or self.rect.bottom >= TUNNEL_BOTTOM:
            self.alive = False
            self.game.state = 'game_over'
            pygame.mixer.music.stop()
            self.game.death_sound.play()
            self.game.current_music = None

    def update(self, delta):
        self.input()
        self.move(delta)
        self.rect.clamp_ip(pygame.Rect(0, TUNNEL_TOP, WINDOW_WIDTH, TUNNEL_BOTTOM - TUNNEL_TOP))