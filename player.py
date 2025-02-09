import pygame
from settings import *
import math


class Player(pygame.sprite.Sprite):
    def __init__(self, groups, game):
        super().__init__(groups)
        self.game = game

        self.original_image = pygame.image.load('Images/Ship.png').convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (PLAYER_SIZE, PLAYER_SIZE))

        self.engine_images = [
            pygame.image.load('Images/Engine1.png').convert_alpha(),
            pygame.image.load('Images/Engine2.png').convert_alpha(),
            pygame.image.load('Images/Engine3.png').convert_alpha(),
            pygame.image.load('Images/Engine2.png').convert_alpha(),  # For smooth loop back
        ]

        engine_scale = (PLAYER_SIZE // 2, PLAYER_SIZE // 2)
        self.engine_images = [pygame.transform.scale(img, engine_scale)
                              for img in self.engine_images]

        self.engine_frame = 0
        self.engine_animation_speed = 10
        self.engine_animation_counter = 0

        # Combined image
        self.combined_surface = pygame.Surface((PLAYER_SIZE * 2, PLAYER_SIZE * 2), pygame.SRCALPHA)
        self.image = self.combined_surface

        # Visual rect
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        # Collision rect
        self.collision_rect = pygame.Rect(0, 0, PLAYER_SIZE * 0.6, PLAYER_SIZE * 0.6)
        self.collision_rect.center = self.rect.center

        self.pos = pygame.Vector2(self.rect.center)
        self.initial_x = self.pos.x
        self.direction = pygame.Vector2(0, 1).normalize()
        self.going_up = False
        self.space_pressed = False
        self.alive = True

        self.current_angle = -135
        self.update_combined_image()

    def update_combined_image(self):
        self.combined_surface.fill((0, 0, 0, 0))
        surface_center = pygame.Vector2(self.combined_surface.get_rect().center)

        # Offset/Engine behind ship
        if self.going_up:
            engine_offset = pygame.Vector2(0, PLAYER_SIZE * 0.5).rotate(-self.current_angle)
        else:
            engine_offset = pygame.Vector2(0, PLAYER_SIZE * 0.5).rotate(-self.current_angle)

        # Engine behind (draw)
        rotated_engine = pygame.transform.rotate(self.engine_images[self.engine_frame], self.current_angle)
        engine_pos = surface_center + engine_offset - pygame.Vector2(rotated_engine.get_width() // 2,
                                                                     rotated_engine.get_height() // 2)
        self.combined_surface.blit(rotated_engine, engine_pos)

        # Ship on top of engine
        rotated_ship = pygame.transform.rotate(self.original_image, self.current_angle)
        ship_pos = surface_center - pygame.Vector2(rotated_ship.get_width() // 2,
                                                   rotated_ship.get_height() // 2)
        self.combined_surface.blit(rotated_ship, ship_pos)

        self.image = self.combined_surface
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        self.collision_rect.center = self.rect.center

    def animate_engine(self):
        self.engine_animation_counter += 1
        if self.engine_animation_counter >= self.engine_animation_speed:
            self.engine_animation_counter = 0
            self.engine_frame = (self.engine_frame + 1) % len(self.engine_images)
            self.update_combined_image()

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not self.space_pressed:
            self.space_pressed = True
            self.going_up = not self.going_up
            self.direction.y = -1 if self.going_up else 1
            self.direction = self.direction.normalize()

            self.current_angle = -45 if self.going_up else -135
            self.update_combined_image()

        elif not keys[pygame.K_SPACE]:
            self.space_pressed = False

    def move(self, delta):
        movement_speed = SCROLL_SPEED * self.game.speed_multiplier - 50
        self.pos.y += self.direction.y * movement_speed * delta
        self.pos.x = self.initial_x
        self.rect.center = self.pos
        self.collision_rect.center = self.pos

        if self.collision_rect.top <= TUNNEL_TOP or self.collision_rect.bottom >= TUNNEL_BOTTOM:
            self.alive = False
            self.game.state = 'game_over'
            pygame.mixer.music.stop()
            self.game.death_sound.play()
            self.game.current_music = None

    def update(self, delta):
        if not self.game.countdown_active:
            self.input()
            self.move(delta)

        self.animate_engine()
        self.collision_rect.clamp_ip(pygame.Rect(0, TUNNEL_TOP, WINDOW_WIDTH, TUNNEL_BOTTOM - TUNNEL_TOP))
        self.rect.center = self.collision_rect.center

    def get_collision_rect(self):
        return self.collision_rect