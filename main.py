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
        pygame.display.set_caption("Infinite Tunnel Runner")
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

    def spawn_spikes(self, delta):
        self.next_spawn -= SCROLL_SPEED * delta
        if self.next_spawn <= 0:
            x = WINDOW_WIDTH + SPIKE_SIZE
            is_top = choice([True, False])
            y = TUNNEL_TOP - SPIKE_SIZE + 65 if is_top else TUNNEL_BOTTOM - 63
            Spike((x, y), is_top, [self.all_sprites, self.spike_sprites])
            self.next_spawn = SEGMENT_WIDTH

    def check_collisions(self):
        if pygame.sprite.spritecollide(self.player, self.spike_sprites, False):
            self.player.alive = False
            self.state = 'game_over'
            return True
        return False

    def draw_tunnel(self):
        pygame.draw.line(self.display_surface, (0, 0, 0), (0, TUNNEL_TOP), (WINDOW_WIDTH, TUNNEL_TOP), 2)
        pygame.draw.line(self.display_surface, (0, 0, 0), (0, TUNNEL_BOTTOM), (WINDOW_WIDTH, TUNNEL_BOTTOM), 2)

    def draw_start_screen(self):
        self.display_surface.fill((255, 255, 255))
        title_text = "Tunnel Runner"
        start_text = "Press SPACE to start"

        title_surface = self.font.render(title_text, True, (0, 0, 0))
        start_surface = self.font.render(start_text, True, (0, 0, 0))

        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        start_rect = start_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 3))

        self.display_surface.blit(title_surface, title_rect)
        self.display_surface.blit(start_surface, start_rect)

    def draw_game_over_screen(self):
        self.display_surface.fill((255, 255, 255))

        game_over = self.font.render(f'Game Over! Score: {int(self.score)}', True, (0, 0, 0))
        game_over_rect = game_over.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))

        restart = self.font.render('Press R to restart', True, (0, 0, 0))
        restart_rect = restart.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))

        menu = self.font.render('Press M to return to main menu', True, (0, 0, 0))
        menu_rect = menu.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 70))

        self.display_surface.blit(game_over, game_over_rect)
        self.display_surface.blit(restart, restart_rect)
        self.display_surface.blit(menu, menu_rect)

    def run(self):
        while self.running:
            delta = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.state == 'start':
                        self.state = 'playing'
                    elif event.key == pygame.K_r and self.state == 'game_over':
                        self.setup_game()
                        self.state = 'playing'
                    elif event.key == pygame.K_m and self.state == 'game_over':
                        self.setup_game()
                        self.state = 'start'

            if self.state == 'start':
                self.draw_start_screen()
            elif self.state == 'playing':
                if self.player.alive:
                    self.spawn_spikes(delta)
                    self.all_sprites.update(delta)
                    self.check_collisions()
                    self.score += delta * 10

                    self.display_surface.fill((255, 255, 255))
                    self.draw_tunnel()
                    self.all_sprites.draw(self.display_surface)

                    score_text = self.font.render(f'Score: {int(self.score)}', True, (0, 0, 0))
                    self.display_surface.blit(score_text, (10, 10))
            elif self.state == 'game_over':
                self.draw_game_over_screen()

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    game = Game()
    game.run()