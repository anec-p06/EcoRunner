# TO RUN ENTER: python3 main.py IN TERMINAL

import pygame
import sys
import random
import os

pygame.init()

WIDTH = 900
HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Eco Runner")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Courier New", 24)
big_font = pygame.font.SysFont("Courier New", 48)

def draw_centered_text(text, font_used, colour, y):
    rendered_text = font_used.render(text, True, colour)
    x = (WIDTH - rendered_text.get_width()) // 2
    screen.blit(rendered_text, (x, y))


def load_image(path, size, fallback_colour):
    try:
        image = pygame.image.load(path)
        return pygame.transform.scale(image, size)
    except:
        surface = pygame.Surface(size)
        surface.fill(fallback_colour)
        return surface


player_image = load_image("assets/images/player.png", (50, 50), (0, 255, 120))
item_image = load_image("assets/images/item.png", (30, 30), (255, 215, 0))
hazard_image = load_image("assets/images/hazard.png", (40, 40), (255, 60, 60))
power_up = load_image("assets/images/powerups.png", (40, 40), (255, 60, 60))
background_image = load_image("assets/images/background.png", (WIDTH, HEIGHT), (30, 30, 40))


class GameObject:
    def __init__(self, x, y, width, height, image):
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self.image = image
        self.rect = pygame.Rect(x, y, width, height)

    def update(self):
        self.rect.x = self._x
        self.rect.y = self._y

    def draw(self, surface):
        surface.blit(self.image, (self._x, self._y))


class Player(GameObject):
    def __init__(self, x, y, health):
        super().__init__(x, y, 50, 50, player_image)
        self.__normal_speed = 5
        self.__speed = self.__normal_speed
        self.__health = health
        self.__score = 0
        self.speed_boost_active = False
        self.speed_boost_start = 0

    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self._x -= self.__speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self._x += self.__speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self._y -= self.__speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self._y += self.__speed

        self._x = max(0, min(WIDTH - self._width, self._x))
        self._y = max(0, min(HEIGHT - self._height, self._y))

    def add_score(self, amount):
        self.__score += amount

    def take_damage(self, damage):
        self.__health -= damage

    def activate_speed_boost(self):
        self.__speed = 9
        self.speed_boost_active = True
        self.speed_boost_start = pygame.time.get_ticks()

    def update_powerups(self):
        if self.speed_boost_active:
            if pygame.time.get_ticks() - self.speed_boost_start >= 5000:
                self.__speed = self.__normal_speed
                self.speed_boost_active = False

    def get_score(self):
        return self.__score

    def get_health(self):
        return self.__health


class Item(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 30, 30, item_image)
        self.points = 10

    def apply_effect(self, player):
        player.add_score(self.points)


class PowerUp(Item):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = power_up
        self.rect = pygame.Rect(x, y, 40, 40)

    def apply_effect(self, player):
        player.activate_speed_boost()

    def apply_effect(self, player):
        player.activate_speed_boost()


class Hazard(GameObject):
    def __init__(self, x, y, speed):
        super().__init__(x, y, 40, 40, hazard_image)
        self.damage = 10
        self.speed = speed
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])

    def move(self):
        self._x += self.speed * self.direction_x
        self._y += self.speed * self.direction_y

        if self._x <= 0 or self._x >= WIDTH - self._width:
            self.direction_x *= -1

        if self._y <= 0 or self._y >= HEIGHT - self._height:
            self.direction_y *= -1


class Game:
    def __init__(self):
        self.running = True
        self.state = "menu"
        self.difficulty = "Normal"
        self.final_score_saved = False
        self.setup_game()

    def setup_game(self):
        if self.difficulty == "Beginner":
            health = 150
            self.game_time = 90
            item_count = 10
            hazard_count = 1
            hazard_speed = 1
            powerup_count = 4

        elif self.difficulty == "Easy":
            health = 120
            self.game_time = 75
            item_count = 8
            hazard_count = 2
            hazard_speed = 2
            powerup_count = 3

        elif self.difficulty == "Normal":
            health = 100
            self.game_time = 60
            item_count = 6
            hazard_count = 4
            hazard_speed = 3
            powerup_count = 2

        elif self.difficulty == "Hard":
            health = 80
            self.game_time = 45
            item_count = 5
            hazard_count = 6
            hazard_speed = 4
            powerup_count = 1

        elif self.difficulty == "Extreme":
            health = 60
            self.game_time = 35
            item_count = 4
            hazard_count = 8
            hazard_speed = 5
            powerup_count = 1

        self.player = Player(100, 100, health)
        self.items = []
        self.hazards = []
        self.powerups = []
        self.start_ticks = pygame.time.get_ticks()
        self.final_score_saved = False

        for i in range(item_count):
            self.items.append(
                Item(
                    random.randint(50, WIDTH - 80),
                    random.randint(50, HEIGHT - 80)
                )
            )

        for i in range(hazard_count):
            self.hazards.append(
                Hazard(
                    random.randint(50, WIDTH - 80),
                    random.randint(50, HEIGHT - 80),
                    hazard_speed
                )
            )

        for i in range(powerup_count):
            self.powerups.append(
                PowerUp(
                    random.randint(50, WIDTH - 80),
                    random.randint(50, HEIGHT - 80)
                )
            )

    def save_score(self):
        if not self.final_score_saved:
            with open("leaderboard.txt", "a") as file:
                file.write(str(self.player.get_score()) + "\n")
            self.final_score_saved = True

    def get_high_score(self):
        if not os.path.exists("leaderboard.txt"):
            return 0

        with open("leaderboard.txt", "r") as file:
            scores = [
                int(line.strip())
                for line in file
                if line.strip().isdigit()
            ]

        if len(scores) == 0:
            return 0

        return max(scores)

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:

                if self.state == "menu":

                    if event.key == pygame.K_1:
                        self.difficulty = "Beginner"
                    elif event.key == pygame.K_2:
                        self.difficulty = "Easy"
                    elif event.key == pygame.K_3:
                        self.difficulty = "Normal"
                    elif event.key == pygame.K_4:
                        self.difficulty = "Hard"
                    elif event.key == pygame.K_5:
                        self.difficulty = "Extreme"
                    elif event.key == pygame.K_SPACE:
                        self.setup_game()
                        self.state = "playing"

                elif self.state == "game_over" or self.state == "win":

                    if event.key == pygame.K_r:
                        self.setup_game()
                        self.state = "playing"
                    elif event.key == pygame.K_m:
                        self.state = "menu"

    def update(self):
        if self.state != "playing":
            return

        keys = pygame.key.get_pressed()

        self.player.move(keys)
        self.player.update()
        self.player.update_powerups()

        for item in self.items:
            item.update()

        for powerup in self.powerups:
            powerup.update()

        for hazard in self.hazards:
            hazard.move()
            hazard.update()

        for item in self.items[:]:
            if self.player.rect.colliderect(item.rect):
                item.apply_effect(self.player)
                self.items.remove(item)

        for powerup in self.powerups[:]:
            if self.player.rect.colliderect(powerup.rect):
                powerup.apply_effect(self.player)
                self.powerups.remove(powerup)

        for hazard in self.hazards:
            if self.player.rect.colliderect(hazard.rect):
                self.player.take_damage(hazard.damage)
                hazard._x = random.randint(50, WIDTH - 80)
                hazard._y = random.randint(50, HEIGHT - 80)

        seconds_passed = (pygame.time.get_ticks() - self.start_ticks) // 1000
        time_left = self.game_time - seconds_passed

        if time_left <= 0 or self.player.get_health() <= 0:
            self.save_score()
            self.state = "game_over"

        if len(self.items) == 0:
            self.player.add_score(100)
            self.save_score()
            self.state = "win"

    def draw_menu(self):
        screen.fill((20, 20, 30))

        title = big_font.render(
            "ECO RUNNER",
            True,
            (0, 255, 120)
        )

        subtitle = font.render(
            "Collect items, avoid hazards and beat the timer!",
            True,
            (255, 255, 255)
        )       

        controls_info = font.render(
            "Use WASD or Arrow Keys to Move",
            True,
            (200, 200, 200)
        )
        
        difficulty = font.render(
            f"Difficulty: {self.difficulty}",
            True,
            (255, 215, 0)
        )
        controls1 = font.render(
            "1 Beginner   2 Easy   3 Normal",
            True,
            (255, 255, 255)
        )
        controls2 = font.render(
            "4 Hard       5 Extreme",
            True,
            (255, 255, 255)
        )
        controls3 = font.render(
            "Press SPACE to Start",
            True,
            (255, 255, 255)
        )
        high_score = font.render(
            f"High Score: {self.get_high_score()}",
            True,
            (0, 200, 255)
        )

        # Centre all menu text so it always fits neatly on the screen.
        draw_centered_text("ECO RUNNER", big_font, (0, 255, 120), 100)
        draw_centered_text("Collect items, avoid hazards and beat the timer!", font, (255,255,255), 180)
        draw_centered_text("Use WASD or Arrow Keys to Move", font, (200,200,200), 220)
        draw_centered_text(f"Difficulty: {self.difficulty}", font, (255,215,0), 280)
        draw_centered_text("1 Beginner   2 Easy   3 Normal", font, (255,255,255), 350)
        draw_centered_text("4 Hard       5 Extreme", font, (255,255,255), 400)
        draw_centered_text("Press SPACE to Start", font, (255,255,255), 470)
        draw_centered_text(f"High Score: {self.get_high_score()}", font, (0,200,255), 530)

    def draw_game(self):
        screen.blit(background_image, (0, 0))

        for item in self.items:
            item.draw(screen)

        for powerup in self.powerups:
            powerup.draw(screen)

        for hazard in self.hazards:
            hazard.draw(screen)

        self.player.draw(screen)

        seconds_passed = (pygame.time.get_ticks() - self.start_ticks) // 1000
        time_left = max(0, self.game_time - seconds_passed)

        score_text = font.render(
            f"Score: {self.player.get_score()}",
            True,
            (255, 255, 255)
        )
        health_text = font.render(
            f"Health: {self.player.get_health()}",
            True,
            (255, 255, 255)
        )
        timer_text = font.render(
            f"Time: {time_left}",
            True,
            (255, 255, 255)
        )
        difficulty_text = font.render(
            f"Mode: {self.difficulty}",
            True,
            (255, 255, 255)
        )

        screen.blit(score_text, (20, 20))
        screen.blit(health_text, (20, 60))
        screen.blit(timer_text, (20, 100))
        screen.blit(difficulty_text, (20, 140))

        if self.player.speed_boost_active:
            boost_text = font.render(
                "Speed Boost Active!",
                True,
                (0, 180, 255)
            )
            screen.blit(boost_text, (20, 180))

    def draw_game_over(self):
        self.draw_game()

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        draw_centered_text("GAME OVER", big_font, (255, 60, 60), 180)

        draw_centered_text(
            f"Final Score: {self.player.get_score()}",
            font,
            (255, 255, 255),
            260
        )

        draw_centered_text(
            f"High Score: {self.get_high_score()}",
            font,
            (0, 200, 255),
            310
        )

        draw_centered_text(
            "Press R to Restart",
            font,
            (255, 255, 255),
            380
        )

        draw_centered_text(
            "Press M for Menu",
            font,
            (255, 255, 255),
            430
        )
        
    def draw_win(self):
        self.draw_game()

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        win_text = big_font.render("YOU WIN!", True, (0, 255, 120))
        score_text = font.render(
            f"Final Score: {self.player.get_score()}",
            True,
            (255, 255, 255)
        )
        high_score = font.render(
            f"High Score: {self.get_high_score()}",
            True,
            (0, 200, 255)
        )
        restart = font.render("Press R to Play Again", True, (255, 255, 255))
        menu = font.render("Press M for Menu", True, (255, 255, 255))

        draw_centered_text("YOU WIN!", big_font, (0, 255, 120), 180)
        draw_centered_text(f"Final Score: {self.player.get_score()}", font, (255,255,255), 260)
        draw_centered_text(f"High Score: {self.get_high_score()}", font, (0,200,255), 310)
        draw_centered_text("Press R to Play Again", font, (255,255,255), 380)
        draw_centered_text("Press M for Menu", font, (255,255,255), 430)

    def draw(self):
        if self.state == "menu":
            self.draw_menu()

        elif self.state == "playing":
            self.draw_game()

        elif self.state == "game_over":
            self.draw_game_over()

        elif self.state == "win":
            self.draw_win()

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()


game = Game()
game.run()
