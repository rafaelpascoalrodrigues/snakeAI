import sys
import numpy as np
import random
import pygame
from pygame.locals import *

# AI
import ai_random_play

INPUT_CONTROL_MANUAL = 0
INPUT_CONTROL_RANDOM_PLAY = 1

# Screen size
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Game field
FIELD_POSITION = (660, 20)
FIELD_BORDER = 5
FIELD_SEGMENTS_WIDTH = 40
FIELD_SEGMENTS_HEIGHT = 45

SEGMENT_SIZE = 15

# Sensors data position
SENSORS_DATA_POSITION = (10, 320)

# Color palette
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)

# Directions
KEEP = -1
DOWN = 0
RIGHT = 1
UP = 2
LEFT = 3

# Snake initial parameters
SNAKE_INITIAL = [(1, 1), (1, 1)]
SNAKE_INITIAL_DIRECTION = DOWN
SNAKE_KEEP_DIRECTION = KEEP


def play(input_control: int = INPUT_CONTROL_MANUAL, seed: int = None, machine_run: bool = False,
         script_play: [int] = None) -> {}:
    # Initialize recurrent game elements
    snake_segment_asset = pygame.Surface((SEGMENT_SIZE, SEGMENT_SIZE))
    snake_segment_asset.fill(COLOR_WHITE)

    food_asset = pygame.Surface((SEGMENT_SIZE, SEGMENT_SIZE))
    food_asset.fill(COLOR_RED)

    # Assignment of visual elements
    screen = None
    clock = None
    font = None
    font_options = None
    font_data = None

    # Ignore visual elements if running a machine requested run
    if not machine_run:
        # Initialize pygame window
        pygame.init()
        pygame.display.set_caption('snake')
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        clock = pygame.time.Clock()

        # Prepare text styles
        font = pygame.font.Font(pygame.font.get_default_font(), 36)
        font_options = pygame.font.Font(pygame.font.get_default_font(), 16)
        font_data = pygame.font.SysFont('monospace', 12, True)

    fixed_random_seed = True
    prng = random.Random()
    if seed is None:
        fixed_random_seed = False
        seed = random.randrange(sys.maxsize)

    # Game initial parameters
    prng.seed(seed, 2)
    snake = [] + SNAKE_INITIAL
    direction = SNAKE_INITIAL_DIRECTION
    input_direction = SNAKE_KEEP_DIRECTION
    score = 0
    moves = 0
    history = []
    food = (-1, -1)
    game_is_over = False

    # Game loop
    set_initial = True
    game_running = True
    while game_running:
        # Set frame rate if not running a machine requested run
        if not machine_run:
            clock.tick(10)

        # Set initial parameters on a new game
        if set_initial:
            if fixed_random_seed:
                prng.seed(seed, 2)
            set_initial = False
            snake = [] + SNAKE_INITIAL
            direction = SNAKE_INITIAL_DIRECTION
            input_direction = SNAKE_KEEP_DIRECTION
            moves = 0
            history = []
            score = 0
            food = (-1, -1)
            game_is_over = False

        # Ignore input events if running a machine requested run
        if not machine_run:
            # Capture events
            for event in pygame.event.get():
                # Quit event
                if event.type == QUIT:
                    game_running = False

                # Keyboard events
                elif event.type == KEYDOWN:
                    # Restart game event
                    if event.key == K_r:
                        input_control = INPUT_CONTROL_MANUAL
                        set_initial = True

                    # Toggle renew of the random seed on each execution
                    elif event.key == K_0:
                        fixed_random_seed = not fixed_random_seed

                    # Restart game with AI Control
                    elif event.key == K_1:
                        input_control = INPUT_CONTROL_RANDOM_PLAY
                        set_initial = True

                    # Movement events
                    elif input_control == INPUT_CONTROL_MANUAL:
                        if event.key == K_DOWN or event.key == K_s:
                            input_direction = DOWN
                        elif event.key == K_RIGHT or event.key == K_d:
                            input_direction = RIGHT
                        elif event.key == K_UP or event.key == K_w:
                            input_direction = UP
                        elif event.key == K_LEFT or event.key == K_a:
                            input_direction = LEFT

        # Validate the movement
        if direction == DOWN and input_direction == UP:
            input_direction = -1
        elif direction == RIGHT and input_direction == LEFT:
            input_direction = -1
        elif direction == UP and input_direction == DOWN:
            input_direction = -1
        elif direction == LEFT and input_direction == RIGHT:
            input_direction = -1
        elif input_direction != -1:
            direction = input_direction
            input_direction = -1

        # Apply the movement
        moves += 1
        history += [direction]
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
            food = (prng.randint(0, FIELD_SEGMENTS_WIDTH - 1), prng.randint(0, FIELD_SEGMENTS_HEIGHT - 1))
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
            # Finish the request if running a machine requested run
            if machine_run:
                return {"score": score, "moves": moves, "history": history}
            continue

        # Initialize sensors
        sensors = {
            "snake": (0, 0),
            "walls": {
                "color": (0, 255, 180),
                "down": (0, 0), "right": (0, 0), "up": (0, 0), "left": (0, 0),
                "down_right": (0, 0),  "up_right": (0, 0), "up_left": (0, 0), "down_left": (0, 0)
            },
            "self": {
                "color": (0, 180, 255),
                "down": (0, 0), "right": (0, 0), "up": (0, 0), "left": (0, 0),
                "down_right": (0, 0),  "up_right": (0, 0), "up_left": (0, 0), "down_left": (0, 0)
            },
            "food": {
                "color": (255, 90, 90),
                "down": (0, 0), "right": (0, 0), "up": (0, 0), "left": (0, 0),
                "down_right": (0, 0),  "up_right": (0, 0), "up_left": (0, 0), "down_left": (0, 0)
            }
        }

        # Calculate sensors positions
        field_x = FIELD_POSITION[0] + FIELD_BORDER
        field_y = FIELD_POSITION[1] + FIELD_BORDER
        pos_x = field_x + snake[0][0] * SEGMENT_SIZE + SEGMENT_SIZE // 2
        pos_y = field_y + snake[0][1] * SEGMENT_SIZE + SEGMENT_SIZE // 2

        # Sensor to the walls
        sensors['snake'] = (pos_x, pos_y)
        sensors['walls']['down'] = (pos_x, field_y + SEGMENT_SIZE * FIELD_SEGMENTS_HEIGHT)
        sensors['walls']['left'] = (field_x, pos_y)
        sensors['walls']['up'] = (pos_x, field_y)
        sensors['walls']['right'] = (field_x + SEGMENT_SIZE * FIELD_SEGMENTS_WIDTH, pos_y)

        diagonal = field_x + SEGMENT_SIZE * FIELD_SEGMENTS_WIDTH - pos_x
        if (pos_y + diagonal) > (field_y + SEGMENT_SIZE * (FIELD_SEGMENTS_WIDTH + 4)):
            diagonal = field_y + SEGMENT_SIZE * FIELD_SEGMENTS_HEIGHT - pos_y
        sensors['walls']['down_right'] = (pos_x + diagonal, pos_y + diagonal)

        diagonal = field_x + SEGMENT_SIZE * FIELD_SEGMENTS_WIDTH - pos_x
        if (pos_y - diagonal) < field_y:
            diagonal = - (field_y - pos_y)
        sensors['walls']['up_right'] = (pos_x + diagonal, pos_y - diagonal)

        diagonal = field_x - pos_x
        if (pos_y + diagonal) < field_y:
            diagonal = field_y - pos_y
        sensors['walls']['up_left'] = (pos_x + diagonal, pos_y + diagonal)

        diagonal = field_x - pos_x
        if (pos_y - diagonal) > (field_y + SEGMENT_SIZE * (FIELD_SEGMENTS_WIDTH + 4)):
            diagonal = - (field_y + SEGMENT_SIZE * FIELD_SEGMENTS_HEIGHT - pos_y)
        sensors['walls']['down_left'] = (pos_x + diagonal, pos_y - diagonal)

        # Sensor to the snake segments
        sensors['self']['down'] = sensors['walls']['down']
        sensors['self']['right'] = sensors['walls']['right']
        sensors['self']['up'] = sensors['walls']['up']
        sensors['self']['left'] = sensors['walls']['left']

        sensors['self']['down_right'] = sensors['walls']['down_right']
        sensors['self']['up_right'] = sensors['walls']['up_right']
        sensors['self']['up_left'] = sensors['walls']['up_left']
        sensors['self']['down_left'] = sensors['walls']['down_left']

        for segment in snake[1:]:
            if segment[0] == snake[0][0]:
                fixed = sensors['self']['up'][0]
                distance = field_y + segment[1] * SEGMENT_SIZE + SEGMENT_SIZE // 2

                if segment[1] < snake[0][1] and sensors['self']['up'][1] < distance:
                    sensors['self']['up'] = (fixed, distance + SEGMENT_SIZE // 2)
                elif segment[1] > snake[0][1] and sensors['self']['down'][1] > distance:
                    sensors['self']['down'] = (fixed, distance - SEGMENT_SIZE // 2)

            elif segment[1] == snake[0][1]:
                fixed = sensors['self']['left'][1]
                distance = field_x + segment[0] * SEGMENT_SIZE + SEGMENT_SIZE // 2

                if segment[0] < snake[0][0] and sensors['self']['left'][0] < distance:
                    sensors['self']['left'] = (distance + SEGMENT_SIZE // 2, fixed)
                elif segment[0] > snake[0][0] and sensors['self']['right'][0] > distance:
                    sensors['self']['right'] = (distance - SEGMENT_SIZE // 2, fixed)

            diagonal = (segment[0] - snake[0][0], segment[1] - snake[0][1])
            if np.absolute(diagonal[0]) == np.absolute(diagonal[1]):
                distance_x = field_x + segment[0] * SEGMENT_SIZE
                distance_y = field_y + segment[1] * SEGMENT_SIZE
                distance_new = np.sqrt((distance_x - pos_x) ** 2 + (distance_y - pos_y) ** 2)

                if diagonal[0] > 0 and diagonal[1] > 0:
                    distance_old = np.sqrt((sensors['self']['down_right'][0] - pos_x) ** 2 + (sensors['self']['down_right'][1] - pos_y) ** 2)
                    if distance_new < distance_old:
                        sensors['self']['down_right'] = (distance_x, distance_y)

                elif diagonal[0] > 0 and diagonal[1] < 0:
                    distance_old = np.sqrt((sensors['self']['up_right'][0] - pos_x) ** 2 + (sensors['self']['up_right'][1] - pos_y) ** 2)
                    if distance_new < distance_old:
                        sensors['self']['up_right'] = (distance_x - (SEGMENT_SIZE & 0x1), distance_y + SEGMENT_SIZE)

                elif diagonal[0] < 0 and diagonal[1] < 0:
                    distance_old = np.sqrt((sensors['self']['up_left'][0] - pos_x) ** 2 + (sensors['self']['up_left'][1] - pos_y) ** 2)
                    if distance_new < distance_old:
                        sensors['self']['up_left'] = (distance_x + SEGMENT_SIZE, distance_y + SEGMENT_SIZE)

                elif diagonal[0] < 0 and diagonal[1] > 0:
                    distance_old = np.sqrt((sensors['self']['down_left'][0] - pos_x) ** 2 + (sensors['self']['down_left'][1] - pos_y) ** 2)
                    if distance_new < distance_old:
                        sensors['self']['down_left'] = (distance_x + SEGMENT_SIZE, distance_y - (SEGMENT_SIZE & 0x1))

        # Sensor to the food
        sensors['food']['down'] = (pos_x, pos_y)
        sensors['food']['right'] = (pos_x, pos_y)
        sensors['food']['up'] = (pos_x, pos_y)
        sensors['food']['left'] = (pos_x, pos_y)

        sensors['food']['down_right'] = (pos_x, pos_y)
        sensors['food']['up_right'] = (pos_x, pos_y)
        sensors['food']['up_left'] = (pos_x, pos_y)
        sensors['food']['down_left'] = (pos_x, pos_y)

        if snake[0][0] == food[0]:
            if snake[0][1] > food[1]:
                sensors['food']['up'] = (pos_x, field_y + food[1] * SEGMENT_SIZE + SEGMENT_SIZE)
            elif snake[0][1] < food[1]:
                sensors['food']['down'] = (pos_x, field_y + food[1] * SEGMENT_SIZE)
        elif snake[0][1] == food[1]:
            if snake[0][0] < food[0]:
                sensors['food']['right'] = (field_x + food[0] * SEGMENT_SIZE, pos_y)
            elif snake[0][0] > food[0]:
                sensors['food']['left'] = (field_x + food[0] * SEGMENT_SIZE + SEGMENT_SIZE, pos_y)

        diagonal = (food[0] - snake[0][0], food[1] - snake[0][1])
        if np.absolute(diagonal[0]) == np.absolute(diagonal[1]):
            distance_x = field_x + food[0] * SEGMENT_SIZE
            distance_y = field_y + food[1] * SEGMENT_SIZE

            if diagonal[0] > 0 and diagonal[1] > 0:
                sensors['food']['down_right'] = (distance_x, distance_y)

            elif diagonal[0] > 0 and diagonal[1] < 0:
                sensors['food']['up_right'] = (distance_x - (SEGMENT_SIZE & 0x1), distance_y + SEGMENT_SIZE)

            elif diagonal[0] < 0 and diagonal[1] < 0:
                sensors['food']['up_left'] = (distance_x + SEGMENT_SIZE, distance_y + SEGMENT_SIZE)

            elif diagonal[0] < 0 and diagonal[1] > 0:
                sensors['food']['down_left'] = (distance_x + SEGMENT_SIZE, distance_y - (SEGMENT_SIZE & 0x1))

        # Call AI for directions
        if input_control == INPUT_CONTROL_MANUAL:
            pass
        elif machine_run and len(script_play) > moves:
            input_direction = script_play[moves]
        elif input_control == INPUT_CONTROL_RANDOM_PLAY:
            input_direction = ai_random_play.play()

        # Prevent draw the game if running a machine requested run
        if machine_run:
            continue

        # Draw the game

        # Clear the screen
        screen.fill(COLOR_BLACK)

        # Draw game information
        screen.blit(font.render('Score: ' + str(score), True, COLOR_WHITE), (10, 10))
        screen.blit(font.render('R to Restart Game', True, COLOR_WHITE), (10, 50))

        screen.blit(font_options.render(
            'Using ' + ('fixed' if fixed_random_seed else 'random') + ' food seed (0 to Change)',
            True, COLOR_WHITE), (340, 65))

        screen.blit(font_options.render('1 to Random Play', True, (
            COLOR_RED if input_control == INPUT_CONTROL_RANDOM_PLAY else COLOR_WHITE
        )), (10, 100))

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

        # Draw the sensors
        data_position = -2
        for sensor_obj in sensors:
            if sensor_obj == 'snake':
                continue

            for sensor_direction in sensors[sensor_obj]:
                data_position += 1
                if sensor_direction == 'color':
                    continue

                pygame.draw.line(screen, sensors[sensor_obj]['color'], sensors['snake'], sensors[sensor_obj][sensor_direction], 2)
                sensor_value = np.sqrt(
                    (sensors[sensor_obj][sensor_direction][0] - sensors['snake'][0]) ** 2 +
                    (sensors[sensor_obj][sensor_direction][1] - sensors['snake'][1]) ** 2
                )
                sensor_text = 'sensor_' + sensor_obj + '_' + sensor_direction + ':'
                sensor_text += (25 - len(sensor_text)) * ' ' + ("{:7.3f}".format(sensor_value))
                screen.blit(font_data.render(sensor_text, True, COLOR_WHITE), (
                    SENSORS_DATA_POSITION[0], SENSORS_DATA_POSITION[1] + data_position * 15
                ))

        # Update the screen
        pygame.display.update()

    # Quit the game
    pygame.quit()


def main():
    play()


if __name__ == '__main__':
    main()
