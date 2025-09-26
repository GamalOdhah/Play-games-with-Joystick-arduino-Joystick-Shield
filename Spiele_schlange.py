import pygame
import random
import sys
import serial
import time

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the display
WIDTH = 640
HEIGHT = 480
BLOCK_SIZE = 20
FPS = 10

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 150, 0)
RED = (255, 0, 0)
LIGHT_RED = (255, 100, 100)
BROWN = (139, 69, 19)
LIGHT_GREEN = (144, 238, 144)

# Font
font = pygame.font.SysFont(None, 35)
small_font = pygame.font.SysFont(None, 25)

# Serial for Arduino
try:
    ser = serial.Serial('COM7', 9600, timeout=0.1)
    joystick_available = True
except:
    joystick_available = False
    ser = None

# Sounds (placeholder beeps)
eat_sound = pygame.mixer.Sound(pygame.mixer.Sound(buffer=b'\x00\x00\x00\x00\x00\x00\x00\x00'))
game_over_sound = pygame.mixer.Sound(pygame.mixer.Sound(buffer=b'\x00\x00\x00\x00\x00\x00\x00\x00'))

def draw_background():
    screen.fill(LIGHT_GREEN)
    for x in range(0, WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, WHITE, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, WHITE, (0, y), (WIDTH, y), 1)

def draw_snake(snake_body):
    for block in snake_body:
        pygame.draw.circle(screen, DARK_GREEN, (block[0] + BLOCK_SIZE//2, block[1] + BLOCK_SIZE//2), BLOCK_SIZE//2 - 2)

def draw_food(food_pos):
    pygame.draw.circle(screen, RED, (food_pos[0] + BLOCK_SIZE//2, food_pos[1] + BLOCK_SIZE//2), BLOCK_SIZE//2)
    pygame.draw.circle(screen, LIGHT_RED, (food_pos[0] + BLOCK_SIZE//2 - 2, food_pos[1] + BLOCK_SIZE//2 - 2), 3)

def get_random_food(snake_body):
    while True:
        x = random.randint(0, (WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        if [x, y] not in snake_body:
            return [x, y]

def message(msg, color, x, y):
    mesg = font.render(msg, True, color)
    screen.blit(mesg, [x, y])

def display_score(score):
    text = small_font.render("Score: " + str(score), True, BLACK)
    screen.blit(text, [10, 10])

def draw_button(text, x, y, w, h, color):
    pygame.draw.rect(screen, color, (x, y, w, h))
    text_surf = font.render(text, True, BLACK)
    screen.blit(text_surf, (x + 10, y + 10))

def start_screen():
    while True:
        draw_background()
        message("Snake Game", BLACK, WIDTH / 2 - 80, HEIGHT / 2 - 50)
        draw_button("Start", WIDTH / 2 - 50, HEIGHT / 2, 100, 50, WHITE)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if WIDTH / 2 - 50 <= mouse_x <= WIDTH / 2 + 50 and HEIGHT / 2 <= mouse_y <= HEIGHT / 2 + 50:
                    return

        joystick_data = read_joystick()
        if joystick_data:
            joyX, joyY, joyBtn, btnA, btnB, btnC, btnD = joystick_data
            if btnC == 0:
                return

        clock.tick(FPS)

def read_joystick():
    if not joystick_available:
        return None
    try:
        line = ser.readline().decode('utf-8').strip()
        if line:
            parts = line.split(',')
            if len(parts) == 7:
                joyX, joyY, joyBtn, btnA, btnB, btnC, btnD = map(int, parts)
                return joyX, joyY, joyBtn, btnA, btnB, btnC, btnD
    except:
        pass
    return None

def game_loop():
    game_over = False
    game_close = False
    paused = False
    prev_btnA = 1

    x1 = WIDTH // 2
    y1 = HEIGHT // 2

    x1_change = 0
    y1_change = 0

    snake_body = []
    length_of_snake = 1
    score = 0

    food_pos = get_random_food(snake_body)

    last_direction = None

    while not game_over:

        while game_close:
            draw_background()
            message("You Lost! Score: " + str(score), RED, WIDTH / 6, HEIGHT / 3)
            draw_button("Try Again", WIDTH / 2 - 50, HEIGHT / 2, 100, 50, WHITE)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        return  # Restart
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if WIDTH / 2 - 50 <= mouse_x <= WIDTH / 2 + 50 and HEIGHT / 2 <= mouse_y <= HEIGHT / 2 + 50:
                        return  # Restart

            joystick_data = read_joystick()
            if joystick_data:
                joyX, joyY, joyBtn, btnA, btnB, btnC, btnD = joystick_data
                if btnC == 0:  # Button C for Play Again
                    return  # Restart
                if btnA == 0:
                    game_over = True
                    game_close = False

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change = -BLOCK_SIZE
                    y1_change = 0
                    last_direction = 'LEFT'
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change = BLOCK_SIZE
                    y1_change = 0
                    last_direction = 'RIGHT'
                elif event.key == pygame.K_UP and y1_change == 0:
                    y1_change = -BLOCK_SIZE
                    x1_change = 0
                    last_direction = 'UP'
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    y1_change = BLOCK_SIZE
                    x1_change = 0
                    last_direction = 'DOWN'
                elif event.key == pygame.K_p:
                    paused = not paused

        # Joystick input
        joystick_data = read_joystick()
        if joystick_data:
            joyX, joyY, joyBtn, btnA, btnB, btnC, btnD = joystick_data
            # Thresholds for direction
            if joyX > 600 and last_direction != 'LEFT':  # Right
                x1_change = BLOCK_SIZE
                y1_change = 0
                last_direction = 'RIGHT'
            elif joyX < 400 and last_direction != 'RIGHT':  # Left
                x1_change = -BLOCK_SIZE
                y1_change = 0
                last_direction = 'LEFT'
            elif joyY > 600 and last_direction != 'DOWN':  # Up (inverted)
                y1_change = -BLOCK_SIZE
                x1_change = 0
                last_direction = 'UP'
            elif joyY < 400 and last_direction != 'UP':  # Down (inverted)
                y1_change = BLOCK_SIZE
                x1_change = 0
                last_direction = 'DOWN'
            if btnA == 0 and prev_btnA == 1:
                paused = not paused
            prev_btnA = btnA

        if paused:
            draw_background()
            message("Paused", BLACK, WIDTH / 2 - 50, HEIGHT / 2 - 80)
            draw_button("Resume", WIDTH / 2 - 120, HEIGHT / 2, 100, 50, WHITE)
            draw_button("Play Again", WIDTH / 2 + 20, HEIGHT / 2, 100, 50, WHITE)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if WIDTH / 2 - 120 <= mouse_x <= WIDTH / 2 - 20 and HEIGHT / 2 <= mouse_y <= HEIGHT / 2 + 50:
                        paused = False
                    elif WIDTH / 2 + 20 <= mouse_x <= WIDTH / 2 + 120 and HEIGHT / 2 <= mouse_y <= HEIGHT / 2 + 50:
                        return  # Restart
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = False

            joystick_data = read_joystick()
            if joystick_data:
                joyX, joyY, joyBtn, btnA, btnB, btnC, btnD = joystick_data
                if btnA == 0 and prev_btnA == 1:
                    paused = False
                elif btnC == 0:  # Button C for Play Again
                    return  # Restart
                prev_btnA = btnA

            clock.tick(FPS)
            continue

        # Wrap around
        x1 += x1_change
        y1 += y1_change
        if x1 >= WIDTH:
            x1 = 0
        elif x1 < 0:
            x1 = WIDTH - BLOCK_SIZE
        if y1 >= HEIGHT:
            y1 = 0
        elif y1 < 0:
            y1 = HEIGHT - BLOCK_SIZE

        draw_background()

        snake_head = [x1, y1]
        snake_body.append(snake_head)
        if len(snake_body) > length_of_snake:
            del snake_body[0]

        # Check self collision
        for segment in snake_body[:-1]:
            if segment == snake_head:
                game_close = True
                game_over_sound.play()

        draw_snake(snake_body)
        draw_food(food_pos)
        display_score(score)

        pygame.display.update()

        if x1 == food_pos[0] and y1 == food_pos[1]:
            food_pos = get_random_food(snake_body)
            length_of_snake += 1
            score += 1
            eat_sound.play()

        clock.tick(FPS)

    if ser:
        ser.close()
    pygame.quit()
    sys.exit()

while True:
    start_screen()
    game_loop()
