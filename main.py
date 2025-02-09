import pygame
import sys
import os
from random import choice

from high_score import HighScores
from settings import *
from player import Player
from sprites import Spike


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Beyond Infinity")
        self.clock = pygame.time.Clock()
        self.state = 'start'
        self.running = True
        self.difficulty = 'easy'  # Default
        self.difficulty_options = ['easy', 'medium', 'hard']
        self.selected_difficulty = 0  # Difficulty index
        self.background = pygame.image.load('Images/background.jpg').convert()
        self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))

        self.menu_options = ['play', 'scores', 'credits', 'exit']
        self.selected_menu = 0  # Choice index

        self.gameover_options = ['restart', 'menu', 'exit']
        self.selected_gameover = 0  # Choice index

        self.game_music = os.path.join('Sound', 'PixelRun.mp3')
        self.menu_music = os.path.join('Sound', 'MenuCoffee.mp3')
        self.death_sound = pygame.mixer.Sound(os.path.join('Sound', 'DeathEffect.wav'))
        pygame.mixer.music.load(self.menu_music)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        self.current_music = self.menu_music

        self.high_score = HighScores()

        self.setup_game()

    def setup_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.spike_sprites = pygame.sprite.Group()
        self.player = Player(self.all_sprites, self)
        self.scroll_offset = 0
        self.next_spawn = 0
        self.score = 0
        self.font = pygame.font.Font(None, 36)

        if self.difficulty == 'easy':
            self.speed_multiplier = 1.0
            self.score_multiplier = 1.0
        elif self.difficulty == 'medium':
            self.speed_multiplier = 1.5
            self.score_multiplier = 1.5
        else:  # hard
            self.speed_multiplier = 1.75
            self.score_multiplier = 1.75

        self.current_speed = SCROLL_SPEED * self.speed_multiplier
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
        for spike in self.spike_sprites:
            if self.player.get_collision_rect().colliderect(spike.rect):
                self.player.alive = False
                self.state = 'game_over'
                pygame.mixer.music.stop()
                self.death_sound.play()
                self.current_music = None
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

    def draw_credits_screen(self):
        self.display_surface.blit(self.background, (0, 0))

        credits_text = "Credits"
        github_text = "https://github.com/Rikito001"
        website_text = "rikito.eu"
        exit_text = "Press ESC: Back to Menu"

        credits_surface = self.font.render(credits_text, True, (0, 0, 0))
        github_surface = self.font.render(github_text, True, (0, 0, 0))
        website_surface = self.font.render(website_text, True, (0, 0, 0))
        exit_surface = self.font.render(exit_text, True, (0, 0, 0))

        credits_rect = credits_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        github_rect = github_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 5))
        website_rect = website_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 5 + 50))
        exit_rect = exit_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 5 + 150))

        self.display_surface.blit(credits_surface, credits_rect)
        self.display_surface.blit(github_surface, github_rect)
        self.display_surface.blit(website_surface, website_rect)
        self.display_surface.blit(exit_surface, exit_rect)

    def draw_difficulty_screen(self):
        self.display_surface.blit(self.background, (0, 0))

        title_text = "Select difficulty with arrows"
        easy_text = "Easy (1x speed, 1x score)"
        medium_text = "Medium (1.5x speed, 1.5x score)"
        hard_text = "Hard (1.75x speed, 1.75x score)"
        back_text = "Press ESC: Back to Menu"
        start_text = "Press SPACE to start"

        title_surface = self.font.render(title_text, True, (0, 0, 0))
        easy_surface = self.font.render(easy_text, True, (0, 255, 0) if self.difficulty == 'easy' else (0, 0, 0))
        medium_surface = self.font.render(medium_text, True, (0, 255, 0) if self.difficulty == 'medium' else (0, 0, 0))
        hard_surface = self.font.render(hard_text, True, (0, 255, 0) if self.difficulty == 'hard' else (0, 0, 0))
        back_surface = self.font.render(back_text, True, (0, 0, 0))
        start_surface = self.font.render(start_text, True, (0, 0, 0))

        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        easy_rect = easy_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 5))
        medium_rect = medium_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 5 + 50))
        hard_rect = hard_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 5 + 100))
        back_rect = back_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 5 + 200))
        start_rect = start_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 5 + 170))

        self.display_surface.blit(title_surface, title_rect)
        self.display_surface.blit(easy_surface, easy_rect)
        self.display_surface.blit(medium_surface, medium_rect)
        self.display_surface.blit(hard_surface, hard_rect)
        self.display_surface.blit(start_surface, start_rect)
        self.display_surface.blit(back_surface, back_rect)

    def draw_start_screen(self):
        self.display_surface.blit(self.background, (0, 0))

        title_text = "Beyond Infinity"
        start_text = "Play"
        scores_text = "High Scores"
        credits_text = "Credits"
        exit_text = "Exit (ESC)"

        title_surface = self.font.render(title_text, True, (0, 0, 0))
        start_surface = self.font.render(start_text, True, (0, 255, 0) if self.menu_options[self.selected_menu] == 'play' else (0, 0, 0))
        scores_surface = self.font.render(scores_text, True, (0, 255, 0) if self.menu_options[self.selected_menu] == 'scores' else (0, 0, 0))
        credits_surface = self.font.render(credits_text, True, (0, 255, 0) if self.menu_options[self.selected_menu] == 'credits' else (0, 0, 0))
        exit_surface = self.font.render(exit_text, True, (0, 255, 0) if self.menu_options[self.selected_menu] == 'exit' else (0, 0, 0))

        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        start_rect = start_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 5))
        scores_rect = scores_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 5 + 50))
        credits_rect = credits_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 5 + 100))
        exit_rect = exit_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 5 + 200))

        self.display_surface.blit(title_surface, title_rect)
        self.display_surface.blit(start_surface, start_rect)
        self.display_surface.blit(scores_surface, scores_rect)
        self.display_surface.blit(credits_surface, credits_rect)
        self.display_surface.blit(exit_surface, exit_rect)

    def check_high_score(self):
        return self.high_score.update_score(self.difficulty, self.score)

    def draw_game_over_screen(self):
        self.display_surface.fill((0, 0, 0))

        game_over_text = f'Game Over! Score: {int(self.score)}'
        difficulty_text = f'Difficulty: {self.difficulty.title()}'
        restart_text = 'Restart'
        menu_text = 'Main Menu'
        exit_text = 'Exit (ESC)'

        game_over_surface = self.font.render(game_over_text, True, (255, 255, 255))
        difficulty_surface = self.font.render(difficulty_text, True, (255, 255, 255))
        restart_surface = self.font.render(restart_text, True, (0, 255, 0) if self.gameover_options[self.selected_gameover] == 'restart' else (255, 255, 255))
        menu_surface = self.font.render(menu_text, True, (0, 255, 0) if self.gameover_options[self.selected_gameover] == 'menu' else (255, 255, 255))
        exit_surface = self.font.render(exit_text, True, (0, 255, 0) if self.gameover_options[self.selected_gameover] == 'exit' else (255, 255, 255))

        game_over_rect = game_over_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        difficulty_rect = difficulty_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        restart_rect = restart_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
        menu_rect = menu_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 70))
        exit_rect = exit_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 120))

        if self.check_high_score():
            high_score_text = "New High Score!"
            high_score_surface = self.font.render(high_score_text, True, (255, 255, 0))
            high_score_rect = high_score_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 150))
            self.display_surface.blit(high_score_surface, high_score_rect)

        self.display_surface.blit(game_over_surface, game_over_rect)
        self.display_surface.blit(difficulty_surface, difficulty_rect)
        self.display_surface.blit(restart_surface, restart_rect)
        self.display_surface.blit(menu_surface, menu_rect)
        self.display_surface.blit(exit_surface, exit_rect)

    def draw_high_scores_screen(self):
        self.display_surface.blit(self.background, (0, 0))

        title_text = "High Scores"
        easy_text = f"Easy: {self.high_score.get_score('easy')}"
        medium_text = f"Medium: {self.high_score.get_score('medium')}"
        hard_text = f"Hard: {self.high_score.get_score('hard')}"
        back_text = "Press ESC: Back to Menu"

        title_surface = self.font.render(title_text, True, (0, 0, 0))
        easy_surface = self.font.render(easy_text, True, (0, 0, 0))
        medium_surface = self.font.render(medium_text, True, (0, 0, 0))
        hard_surface = self.font.render(hard_text, True, (0, 0, 0))
        back_surface = self.font.render(back_text, True, (0, 0, 0))

        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        easy_rect = easy_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 5))
        medium_rect = medium_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 5 + 50))
        hard_rect = hard_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 5 + 100))
        back_rect = back_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 5 + 200))

        self.display_surface.blit(title_surface, title_rect)
        self.display_surface.blit(easy_surface, easy_rect)
        self.display_surface.blit(medium_surface, medium_rect)
        self.display_surface.blit(hard_surface, hard_rect)
        self.display_surface.blit(back_surface, back_rect)

    def run(self):
        while self.running:
            delta = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if self.state == 'start':
                        if event.key == pygame.K_UP:
                            self.selected_menu = (self.selected_menu - 1) % len(self.menu_options)
                        elif event.key == pygame.K_DOWN:
                            self.selected_menu = (self.selected_menu + 1) % len(self.menu_options)
                        elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            if self.menu_options[self.selected_menu] == 'play':
                                self.state = 'difficulty'
                            elif self.menu_options[self.selected_menu] == 'scores':
                                self.state = 'high_scores'
                            elif self.menu_options[self.selected_menu] == 'credits':
                                self.state = 'credits'
                            elif self.menu_options[self.selected_menu] == 'exit':
                                self.running = False
                        elif event.key == pygame.K_ESCAPE:
                            self.running = False
                    elif self.state == 'credits':
                        if event.key == pygame.K_ESCAPE:
                            self.state = 'start'
                    elif self.state == 'high_scores':
                        if event.key == pygame.K_ESCAPE:
                            self.state = 'start'
                    elif self.state == 'difficulty':
                        if event.key == pygame.K_UP:
                            self.selected_difficulty = (self.selected_difficulty - 1) % len(self.difficulty_options)
                            self.difficulty = self.difficulty_options[self.selected_difficulty]
                        elif event.key == pygame.K_DOWN:
                            self.selected_difficulty = (self.selected_difficulty + 1) % len(self.difficulty_options)
                            self.difficulty = self.difficulty_options[self.selected_difficulty]
                        elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            self.state = 'playing'
                            self.setup_game()
                            # Game music
                            if self.current_music != self.game_music:
                                pygame.mixer.music.stop()
                                pygame.mixer.music.load(self.game_music)
                                pygame.mixer.music.play(-1)
                                self.current_music = self.game_music
                        elif event.key == pygame.K_ESCAPE:
                            self.state = 'start'
                            # Menu music
                            if self.current_music != self.menu_music:
                                pygame.mixer.music.stop()
                                pygame.mixer.music.load(self.menu_music)
                                pygame.mixer.music.play(-1)
                                self.current_music = self.menu_music
                    elif self.state == 'game_over':
                        if event.key == pygame.K_UP:
                            self.selected_gameover = (self.selected_gameover - 1) % len(self.gameover_options)
                        elif event.key == pygame.K_DOWN:
                            self.selected_gameover = (self.selected_gameover + 1) % len(self.gameover_options)
                        elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            if self.gameover_options[self.selected_gameover] == 'restart':
                                self.setup_game()
                                self.state = 'playing'
                                # Game music
                                if self.current_music != self.game_music:
                                    pygame.mixer.music.stop()
                                    pygame.mixer.music.load(self.game_music)
                                    pygame.mixer.music.play(-1)
                                    self.current_music = self.game_music
                            elif self.gameover_options[self.selected_gameover] == 'menu':
                                self.setup_game()
                                self.state = 'start'
                                # Menu music
                                if self.current_music != self.menu_music:
                                    pygame.mixer.music.stop()
                                    pygame.mixer.music.load(self.menu_music)
                                    pygame.mixer.music.play(-1)
                                    self.current_music = self.menu_music
                            elif self.gameover_options[self.selected_gameover] == 'exit':
                                self.running = False
                        elif event.key == pygame.K_ESCAPE:
                            self.running = False

            if self.state == 'start':
                if self.current_music != self.menu_music:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(self.menu_music)
                    pygame.mixer.music.play(-1)
                    self.current_music = self.menu_music
                self.draw_start_screen()
            elif self.state == 'difficulty':
                self.draw_difficulty_screen()
            elif self.state == 'credits':
                self.draw_credits_screen()
            elif self.state == 'high_scores':
                self.draw_high_scores_screen()
            elif self.state == 'playing':
                if self.player.alive:
                    self.spawn_spikes(delta)
                    self.all_sprites.update(delta)
                    self.check_collisions()
                    self.score += delta * 10 * self.score_multiplier

                    current_hundred = (int(self.score) // 100) * 100
                    if current_hundred > self.last_speed_increase:
                        self.current_speed *= 1.05  # 5%
                        self.last_speed_increase = current_hundred

                    self.draw_tunnel()
                    self.all_sprites.draw(self.display_surface)

                    speed_multiplier = self.current_speed / SCROLL_SPEED
                    score_text = self.font.render(f'Score: {int(self.score)}', True, (255, 255, 255))
                    speed_text = self.font.render(f'Speed: {speed_multiplier:.2f}x', True, (255, 255, 255))
                    difficulty_text = self.font.render(f'Difficulty: {self.difficulty.title()}', True, (255, 255, 255))
                    high_score_text = self.font.render(f'High Score: {self.high_score.get_score(self.difficulty)}', True, (255, 255, 255))

                    speed_rect = speed_text.get_rect(center=(WINDOW_WIDTH // 2 - 150, 120))
                    score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2 + 150, 120))
                    difficulty_rect = difficulty_text.get_rect(center=(WINDOW_WIDTH // 2 - 150, 90))
                    high_score_rect = high_score_text.get_rect(center=(WINDOW_WIDTH // 2 + 150, 90))

                    self.display_surface.blit(speed_text, speed_rect)
                    self.display_surface.blit(score_text, score_rect)
                    self.display_surface.blit(difficulty_text, difficulty_rect)
                    self.display_surface.blit(high_score_text, high_score_rect)
            elif self.state == 'game_over':
                self.draw_game_over_screen()

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    game = Game()
    game.run()
    