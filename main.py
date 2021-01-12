import random
import pygame
from pygame.locals import *

# Screen size
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Game field
FIELD_POSITION = (660, 20)
FIELD_BORDER = 5
FIELD_SEGMENTS_WIDTH = 40
FIELD_SEGMENTS_HEIGHT = 45

SEGMENT_SIZE = 15

# Color palette
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)

# Directions
DOWN = 0
RIGHT = 1
UP = 2
LEFT = 3

# Snake initial parameters
SNAKE_INITIAL = [(1, 1), (1, 1)]
SNAKE_INITIAL_DIRECTION = DOWN


def play():
    # Initialize recurrent game elements
    snake_segment_asset = pygame.Surface((SEGMENT_SIZE, SEGMENT_SIZE))
    snake_segment_asset.fill(COLOR_WHITE)

    food_asset = pygame.Surface((SEGMENT_SIZE, SEGMENT_SIZE))
    food_asset.fill(COLOR_RED)

    # Initialize pygame window
    pygame.init()
    pygame.display.set_caption('snake')
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Prepare text styles
    font = pygame.font.Font(pygame.font.get_default_font(), 36)

    # Game initial parameters
    snake = [] + SNAKE_INITIAL
    direction = SNAKE_INITIAL_DIRECTION
    input_direction = SNAKE_INITIAL_DIRECTION
    score = 0
    food = (-1, -1)
    game_is_over = False

    # Game loop
    set_initial = True
    game_running = True
    while game_running:
        # Set frame rate
        clock.tick(10)

        # Set initial parameters on a new game
        if set_initial:
            set_initial = False
            snake = [] + SNAKE_INITIAL
            direction = SNAKE_INITIAL_DIRECTION
            input_direction = SNAKE_INITIAL_DIRECTION
            score = 0
            food = (-1, -1)
            game_is_over = False

        # Capture events
        for event in pygame.event.get():
            # Quit event
            if event.type == QUIT:
                game_running = False

            # Keyboard events
            elif event.type == KEYDOWN:
                # Restart game event
                if event.key == K_r:
                    set_initial = True

                # Movement events
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    input_direction = DOWN
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    input_direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    input_direction = UP
                elif (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    input_direction = LEFT

        # Apply the movement
        direction = input_direction
        mov_x, mov_y = +0, +0
        if direction == DOWN:
            mov_x, mov_y = +0, +1
        elif direction == RIGHT:
            mov_x, mov_y = +1, +0
        elif direction == UP:
            mov_x, mov_y = +0, -1
        elif direction == LEFT:
            mov_x, mov_y = -1, +0
        snake = [(snake[0][0] + mov_x, snake[0][1] + mov_y)] + snake

        # Detect food collision
        if snake[0][0] == food[0] and snake[0][1] == food[1]:
            food = (-1, -1)
            score += 1
        else:
            snake = snake[:-1]

        # Create a food if already not exists
        while food[0] == -1:
            food = (random.randint(0, FIELD_SEGMENTS_WIDTH - 1), random.randint(0, FIELD_SEGMENTS_HEIGHT - 1))
            # Prevent create a food on a invalid place
            for segment in snake:
                if food[0] == segment[0] and food[1] == segment[1]:
                    food = (-1, -1)
                    break

        # Detect wall collision
        if (snake[0][0] < 0 or snake[0][0] >= FIELD_SEGMENTS_WIDTH) or (snake[0][1] < 0 or snake[0][1] >= FIELD_SEGMENTS_HEIGHT):
            game_is_over = True

        # Detect snake segment collision
        for segment in snake[1:]:
            if segment[0] == snake[0][0] and segment[1] == snake[0][1]:
                game_is_over = True

        # Interrupt game update after a collision
        if game_is_over:
            continue

        # Draw the game

        # Clear the screen
        screen.fill(COLOR_BLACK)

        # Draw game information
        screen.blit(font.render('Score: ' + str(score), True, COLOR_WHITE), (10, 10))
        screen.blit(font.render('R to Restart Game', True, COLOR_WHITE), (10, 50))

        # Draw field limits
        pygame.draw.rect(screen, COLOR_WHITE, (
            FIELD_POSITION[0],
            FIELD_POSITION[1],
            FIELD_SEGMENTS_WIDTH * SEGMENT_SIZE + FIELD_BORDER * 2,
            FIELD_SEGMENTS_HEIGHT * SEGMENT_SIZE + FIELD_BORDER * 2
        ), FIELD_BORDER)

        # Draw the food
        screen.blit(food_asset, (food[0] * SEGMENT_SIZE + FIELD_POSITION[0] + FIELD_BORDER, food[1] * SEGMENT_SIZE + FIELD_POSITION[1] + FIELD_BORDER))

        # Draw the snake
        for segment in snake:
            screen.blit(snake_segment_asset, (segment[0] * SEGMENT_SIZE + FIELD_POSITION[0] + FIELD_BORDER, segment[1] * SEGMENT_SIZE + FIELD_POSITION[1] + FIELD_BORDER))

        # Update the screen
        pygame.display.update()

    # Quit the game
    pygame.quit()


def main():
    play()


if __name__ == '__main__':
    main()
