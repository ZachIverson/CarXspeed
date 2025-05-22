#-----------------------
#main.py
#Zach Ignacio
#May 17, 2025
#Large Scale Project
#-----------------------

import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 480, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CarXspeed")

# Clock and font
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Game variables
LANE_WIDTH = WIDTH // 3
CAR_WIDTH, CAR_HEIGHT = 80, 130
BIG_CAR_WIDTH, BIG_CAR_HEIGHT = 90, 140  # for player3

# Load images
road_img = pygame.transform.scale(pygame.image.load("assets/road.png"), (WIDTH, HEIGHT))
player_car_imgs = [
    pygame.transform.scale(pygame.image.load("assets/player1.png"), (CAR_WIDTH, CAR_HEIGHT)),
    pygame.transform.scale(pygame.image.load("assets/player2.png"), (CAR_WIDTH, CAR_HEIGHT)),
    pygame.transform.scale(pygame.image.load("assets/player3.png"), (BIG_CAR_WIDTH, BIG_CAR_HEIGHT))
]
enemy_car_imgs = [
    pygame.transform.scale(pygame.image.load(f"assets/enemy{i}.png"), (CAR_WIDTH, CAR_HEIGHT))
    for i in range(1, 6)
]

# Lane positions
lanes = [LANE_WIDTH * i + (LANE_WIDTH - CAR_WIDTH) // 2 for i in range(3)]

# Game state
score = 0
high_score = 0

# Load high score
try:
    with open("highscore.txt", "r") as file:
        high_score = int(file.read())
except:
    high_score = 0

def draw_text(text, size, x, y, color=WHITE):
    font_obj = pygame.font.SysFont(None, size)
    text_surface = font_obj.render(text, True, color)
    rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, rect)

def show_menu():
    selected = 0
    while True:
        screen.fill(BLACK)
        draw_text("CarXspeed", 60, WIDTH // 2, 80)
        draw_text("Choose Your Car:", 40, WIDTH // 2, 140)

        for i, car_img in enumerate(player_car_imgs):
            rect = car_img.get_rect(center=(LANE_WIDTH * i + LANE_WIDTH // 2, 250))
            screen.blit(car_img, rect)

        draw_text("Press 1, 2, or 3 to Select", 30, WIDTH // 2, 420)
        draw_text("Press ESC to Exit", 30, WIDTH // 2, 460)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_1:
                    return 0
                elif event.key == pygame.K_2:
                    return 1
                elif event.key == pygame.K_3:
                    return 2

        pygame.display.update()
        clock.tick(60)

class Car:
    def __init__(self, x, y, img):
        self.img = img
        self.rect = img.get_rect(topleft=(x, y))

    def draw(self):
        screen.blit(self.img, self.rect)

    def move(self, dy):
        self.rect.y += dy

def draw_game_over_animation():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    draw_text("GAME OVER", 60, WIDTH // 2, HEIGHT // 2 - 40, RED)
    pygame.display.update()
    pygame.time.wait(1500)

# Main game function
def game_loop(player_choice):
    global score, high_score
    running = True
    paused = False

    # Setup player car
    player_img = player_car_imgs[player_choice]
    px = lanes[1] if player_choice != 2 else lanes[1] - 5  # offset for bigger car
    py = HEIGHT - player_img.get_height() - 10
    player = Car(px, py, player_img)

    # Enemies list
    enemies = []
    enemy_timer = 0
    enemy_interval = 40

    # Road scroll
    road_y = 0

    score = 0

    while running:
        screen.fill(BLACK)

        # Draw moving road
        screen.blit(road_img, (0, road_y))
        screen.blit(road_img, (0, road_y - HEIGHT))
        road_y += 5
        if road_y >= HEIGHT:
            road_y = 0

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused

        if paused:
            draw_text("Paused", 60, WIDTH // 2, HEIGHT // 2)
            pygame.display.update()
            clock.tick(60)
            continue

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.rect.left > 0:
            player.rect.x -= 5
        if keys[pygame.K_RIGHT] and player.rect.right < WIDTH:
            player.rect.x += 5

        # Spawn enemies
        enemy_timer += 1
        if enemy_timer > enemy_interval:
            lane = random.choice(lanes)
            img = random.choice(enemy_car_imgs)
            enemies.append(Car(lane, -CAR_HEIGHT, img))
            enemy_timer = 0

        # Move and draw enemies
        speed = 5 + score // 10
        for enemy in enemies[:]:
            enemy.move(speed)
            enemy.draw()
            if enemy.rect.top > HEIGHT:
                enemies.remove(enemy)
                score += 1

            # Improve collision detection using reduced collision box
            player_collision_rect = player.rect.inflate(-20, -20)
            enemy_collision_rect = enemy.rect.inflate(-20, -20)
            if player_collision_rect.colliderect(enemy_collision_rect):
                draw_game_over_animation()
                running = False

        player.draw()

        # Draw score
        draw_text(f"Score: {score}", 30, 70, 30)
        draw_text(f"High Score: {high_score}", 30, WIDTH - 130, 30)

        pygame.display.update()
        clock.tick(60)

    if score > high_score:
        high_score = score
        with open("highscore.txt", "w") as file:
            file.write(str(high_score))

    # Game Over screen
    screen.fill(BLACK)
    draw_text("Game Over", 60, WIDTH // 2, HEIGHT // 2 - 60)
    draw_text(f"Score: {score}", 40, WIDTH // 2, HEIGHT // 2)
    draw_text("Press R to Restart or ESC to Exit", 30, WIDTH // 2, HEIGHT // 2 + 60)
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def main():
    player_choice = show_menu()
    game_loop(player_choice)

if __name__ == "__main__":
    main()

