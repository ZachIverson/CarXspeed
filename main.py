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

# Screen ratio
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
CAR_WIDTH, CAR_HEIGHT = 85, 135
BIG_CAR_WIDTH, BIG_CAR_HEIGHT = 160, 145  # for player3

# Load images
road_img = pygame.transform.scale(pygame.image.load("assets/road.png"), (WIDTH, HEIGHT))
player_car_imgs = [
    pygame.transform.scale(pygame.image.load("assets/player1.png"), (CAR_WIDTH, CAR_HEIGHT)),
    pygame.transform.scale(pygame.image.load("assets/player2.png"), (95, 135)),
    pygame.transform.scale(pygame.image.load("assets/player3.png"), (BIG_CAR_WIDTH, BIG_CAR_HEIGHT))
]
enemy_car_imgs = [
    pygame.transform.scale(pygame.image.load("assets/enemy1.png"), (130, 135)),
    pygame.transform.scale(pygame.image.load("assets/enemy2.png"), (130, 150)),
    pygame.transform.scale(pygame.image.load("assets/enemy3.png"), (130, 135)),
    pygame.transform.scale(pygame.image.load("assets/enemy4.png"), (85, 135)),
    pygame.transform.scale(pygame.image.load("assets/enemy5.png"), (85, 135))
]

# Power-up and heart lives images
powerup_imgs = {
    "shield": pygame.transform.scale(pygame.image.load("assets/shield.png"), (40, 40)),
    "star": pygame.transform.scale(pygame.image.load("assets/star.png"), (40, 40))
}
heart_img = pygame.transform.scale(pygame.image.load("assets/heart.png"), (30, 30))

# Game state
score = 0
high_score = 0

# Load high score
try:
    with open("highscore.txt", "r") as file:
        high_score = int(file.read())
except:
    high_score = 0
    
def show_ready_go():
    countdown = [("READY", (255, 0, 0)), ("GO!", (0, 255, 0))]  # Red for READY, Green for GO
    for text, color in countdown:
        screen.fill(BLACK)
        screen.blit(road_img, (0, 0))
        draw_text(text, 80, WIDTH // 2, HEIGHT // 2, color)
        pygame.display.update()
        pygame.time.wait(1000)

def draw_text(text, size, x, y, color=WHITE):
    font_obj = pygame.font.SysFont(None, size)
    text_surface = font_obj.render(text, True, color)
    rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, rect)

def draw_hearts(lives):
    for i in range(lives):
        screen.blit(heart_img, (WIDTH // 2 - 50 + i * 35, 60))

def draw_powerup_icons(powerup_icons):
    for i, (icon_kind, timer) in enumerate(powerup_icons):
        icon_img = pygame.transform.scale(powerup_imgs[icon_kind], (50, 50))  # make icons bigger
        y_pos = HEIGHT - 60 - i * 60
        screen.blit(icon_img, (10, y_pos))

        # Determine the name based on the icon_kind
        powerup_name = ""
        if icon_kind == "shield":
            powerup_name = "Shield"
        elif icon_kind == "star":
            powerup_name = "Score Multiplier"

        # Show power-up name
        draw_text(powerup_name, 25, 140, y_pos + 15, WHITE) # Adjusted x and y for name positioning

        # Show countdown in seconds beside icon
        seconds_left = max(timer // 60, 0)  # Convert frames to seconds (assuming 60 FPS)
        draw_text(f"{seconds_left}s", 25, 140, y_pos + 35, WHITE) # Adjusted x and y for timer positioning


def show_menu():
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
    def __init__(self, x, y, img, name="generic", hitbox_scale=(0.5, 0.85)):
        self.img = img
        self.name = name
        self.rect = img.get_rect(topleft=(x, y))
        self.hitbox_scale = hitbox_scale
        self.visible = True
        self.blink_timer = 0

    def draw(self):
        if self.visible:
            screen.blit(self.img, self.rect)

    def move(self, dy):
        self.rect.y += dy

    def get_hitbox(self):
        hitbox = self.rect.copy()
        hitbox.width = int(self.rect.width * self.hitbox_scale[0])
        hitbox.height = int(self.rect.height * self.hitbox_scale[1])
        hitbox.center = self.rect.center
        return hitbox

class PowerUp:
    def __init__(self, x, y, kind):
        self.kind = kind
        self.image = powerup_imgs[kind]
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self):
        screen.blit(self.image, self.rect)

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

def game_loop(player_choice):
    global score, high_score
    running = True
    paused = False

    player_img = player_car_imgs[player_choice]
    car_width = player_img.get_width()
    lanes = [LANE_WIDTH * i + (LANE_WIDTH - car_width) // 2 for i in range(3)]
    px = lanes[1]
    py = HEIGHT - player_img.get_height() - 10
    player_name = f"player{player_choice + 1}"
    hitbox_scale = (0.6, 0.85) if player_choice in [0, 1] else (0.4, 0.6)
    player = Car(px, py, player_img, name=player_name, hitbox_scale=hitbox_scale)

    enemies = []
    enemy_timer = 0
    enemy_interval = 40

    powerups = []
    powerup_timer = 0
    powerup_interval = 900  # 15 seconds at 60 FPS
    shield_active = False
    shield_timer = 0
    multiplier_active = False
    multiplier_timer = 0
    powerup_icons = []

    road_y = 0
    score = 0
    lives = 3
    show_ready_go()  #Show "READY/GO!" before the game starts

    # Define power-up durations in frames
    SHIELD_DURATION_FRAMES = 10 * 60  # 10 seconds * 60 FPS
    MULTIPLIER_DURATION_FRAMES = 13 * 60 # 13 seconds * 60 FPS

    while running:
        screen.fill(BLACK)
        screen.blit(road_img, (0, road_y))
        screen.blit(road_img, (0, road_y - HEIGHT))
        road_y += 5
        if road_y >= HEIGHT:
            road_y = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                paused = not paused

        if paused:
            draw_text("Paused", 60, WIDTH // 2, HEIGHT // 2)
            pygame.display.update()
            clock.tick(60)
            continue

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.rect.left > 0:
            player.rect.x -= 5
        if keys[pygame.K_RIGHT] and player.rect.right < WIDTH:
            player.rect.x += 5
        if keys[pygame.K_UP] and player.rect.top > 0:
            player.rect.y -= 5
        if keys[pygame.K_DOWN] and player.rect.bottom < HEIGHT:
            player.rect.y += 5

        enemy_timer += 1
        if enemy_timer > enemy_interval:
            img = random.choice(enemy_car_imgs)
            lane = random.choice([LANE_WIDTH * i + (LANE_WIDTH - img.get_width()) // 2 for i in range(3)])
            enemies.append(Car(lane, -img.get_height(), img))
            enemy_timer = 0

        powerup_timer += 1
        if powerup_timer > powerup_interval:
            kind = random.choice(["shield", "star"])
            x = random.choice([LANE_WIDTH * i + (LANE_WIDTH - 40) // 2 for i in range(3)])
            powerups.append(PowerUp(x, -40, kind))
            powerup_timer = 0

        speed = 5 + score // 10
        for enemy in enemies[:]:
            enemy.move(speed)
            enemy.draw()
            if enemy.rect.top > HEIGHT:
                enemies.remove(enemy)
                score += 2 if multiplier_active else 1

        for p in powerups[:]:
            p.move(speed)
            p.draw()
            if p.rect.top > HEIGHT:
                powerups.remove(p)
            elif player.rect.colliderect(p.rect):
                if p.kind == "shield":
                    shield_active = True
                    shield_timer = SHIELD_DURATION_FRAMES  # Set to 10 seconds
                    powerup_icons.append(("shield", SHIELD_DURATION_FRAMES))
                elif p.kind == "star":
                    multiplier_active = True
                    multiplier_timer = MULTIPLIER_DURATION_FRAMES  # Set to 13 seconds
                    powerup_icons.append(("star", MULTIPLIER_DURATION_FRAMES))
                powerups.remove(p)

        if shield_active:
            shield_timer -= 1
            if shield_timer <= 0:
                shield_active = False

        if multiplier_active:
            multiplier_timer -= 1
            if multiplier_timer <= 0:
                multiplier_active = False

        for i, (icon, timer) in enumerate(powerup_icons[:]):
            timer -= 1
            if timer <= 0:
                powerup_icons.remove((icon, timer + 1))
            else:
                powerup_icons[i] = (icon, timer)

        if any(player.get_hitbox().colliderect(e.get_hitbox()) for e in enemies):
            if shield_active:
                pass
            else:
                lives -= 1
                if lives <= 0:
                    draw_game_over_animation()
                    running = False
                else:
                    player.blink_timer = 60
                    enemies.clear()

        if player.blink_timer > 0:
            player.visible = not player.visible
            player.blink_timer -= 1
        else:
            player.visible = True

        player.draw()
        draw_text(f"Score: {score}", 30, 70, 30)
        draw_text(f"High Score: {high_score}", 30, WIDTH - 130, 30)
        draw_hearts(lives)
        draw_powerup_icons(powerup_icons)
        pygame.display.update()
        clock.tick(60)

    if score > high_score:
        with open("highscore.txt", "w") as file:
            file.write(str(score))
        high_score = score

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


