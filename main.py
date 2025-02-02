import pygame
import sys
from random import choice
from settings import *
from player import Player
from sprites import Spike


class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Beyond Infinity")
        self.clock = pygame.time.Clock()
        self.state = 'start'
        self.running = True
        self.setup_game()

    def setup_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.spike_sprites = pygame.sprite.Group()
        self.player = Player(self.all_sprites)
        self.scroll_offset = 0
        self.next_spawn = 0
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.current_speed = SCROLL_SPEED
        self.last_speed_increase = 0

    def spawn_spikes(self, delta):
        self.next_spawn -= self.current_speed * delta
        if self.next_spawn <= 0:
            x = WINDOW_WIDTH + SPIKE_SIZE
            is_top = choice([True, False])
            y = TUNNEL_TOP - SPIKE_SIZE + 65 if is_top else TUNNEL_BOTTOM - 63
            spike = Spike((x, y), is_top, [self.all_sprites, self.spike_sprites])
            spike.game = self
            self.next_spawn = SEGMENT_WIDTH

    def check_collisions(self):
        if pygame.sprite.spritecollide(self.player, self.spike_sprites, False):
            self.player.alive = False
            self.state = 'game_over'
            return True
        return False

    def draw_tunnel(self):
        # Entire screen
        self.display_surface.fill((0, 0, 0))

        # Tunnel area
        tunnel_rect = pygame.Rect(0, TUNNEL_TOP, WINDOW_WIDTH, TUNNEL_BOTTOM - TUNNEL_TOP)
        pygame.draw.rect(self.display_surface, (255, 255, 255), tunnel_rect)

        # Borderlines
        pygame.draw.line(self.display_surface, (0, 0, 0), (0, TUNNEL_TOP), (WINDOW_WIDTH, TUNNEL_TOP), 2)
        pygame.draw.line(self.display_surface, (0, 0, 0), (0, TUNNEL_BOTTOM), (WINDOW_WIDTH, TUNNEL_BOTTOM), 2)

    def draw_start_screen(self):
        self.display_surface.fill((0, 0, 0))
        title_text = "Beyond Infinity"
        start_text = "Press SPACE to start"
        exit_text = "Press ESC to exit"

        title_surface = self.font.render(title_text, True, (255, 255, 255))
        start_surface = self.font.render(start_text, True, (255, 255, 255))
        exit_surface = self.font.render(exit_text, True, (255, 255, 255))

        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        start_rect = start_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 3))
        exit_rect = exit_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 3 + 50))

        self.display_surface.blit(title_surface, title_rect)
        self.display_surface.blit(start_surface, start_rect)
        self.display_surface.blit(exit_surface, exit_rect)

    def draw_game_over_screen(self):
        self.display_surface.fill((0, 0, 0))

        game_over = self.font.render(f'Game Over! Score: {int(self.score)}', True, (255, 255, 255))
        game_over_rect = game_over.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))

        restart = self.font.render('Press SPACE to restart', True, (255, 255, 255))
        restart_rect = restart.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))

        menu = self.font.render('Press M to return to main menu', True, (255, 255, 255))
        menu_rect = menu.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 70))

        exit_text = self.font.render('Press ESC to exit', True, (255, 255, 255))
        exit_rect = exit_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 120))

        self.display_surface.blit(game_over, game_over_rect)
        self.display_surface.blit(restart, restart_rect)
        self.display_surface.blit(menu, menu_rect)
        self.display_surface.blit(exit_text, exit_rect)

    def run(self):
        while self.running:
            delta = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.state == 'start':
                        self.state = 'playing'
                    elif event.key == pygame.K_SPACE and self.state == 'game_over':
                        self.setup_game()
                        self.state = 'playing'
                    elif event.key == pygame.K_m and self.state == 'game_over':
                        self.setup_game()
                        self.state = 'start'
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

            if self.state == 'start':
                self.draw_start_screen()
            elif self.state == 'playing':
                if self.player.alive:
                    self.spawn_spikes(delta)
                    self.all_sprites.update(delta)
                    self.check_collisions()
                    self.score += delta * 10

                    current_hundred = (int(self.score) // 100) * 100
                    if current_hundred > self.last_speed_increase:
                        self.current_speed *= 1.05  # 5%
                        self.last_speed_increase = current_hundred

                    self.draw_tunnel()
                    self.draw_tunnel()
                    self.all_sprites.draw(self.display_surface)

                    score_text = self.font.render(f'Score: {int(self.score)}', True, (255, 255, 255))
                    self.display_surface.blit(score_text, (10, 10))

                    speed_multiplier = self.current_speed / SCROLL_SPEED
                    speed_text = self.font.render(f'Speed: {speed_multiplier:.2f}x', True, (255, 255, 255))
                    self.display_surface.blit(speed_text, (10, 50))
            elif self.state == 'game_over':
                self.draw_game_over_screen()

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    game = Game()
    game.run()