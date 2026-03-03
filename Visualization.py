import pygame
import sys
import time
import pickle
import random
from collections import defaultdict

# =========================
# CONFIG
# =========================
GRID_SIZE = 10
CELL_SIZE = 30
WINDOW_SIZE = GRID_SIZE * CELL_SIZE
FPS = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 180, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)

# Directions
UP = (0, -1)
RIGHT = (1, 0)
DOWN = (0, 1)
LEFT = (-1, 0)
DIRECTIONS = [UP, RIGHT, DOWN, LEFT]

# Actions
STRAIGHT = 0
TURN_LEFT = 1
TURN_RIGHT = 2
ACTIONS = [STRAIGHT, TURN_LEFT, TURN_RIGHT]

# =========================
# ENVIRONMENT
# =========================
class SnakeGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.direction = RIGHT
        self.snake = [(GRID_SIZE // 2, GRID_SIZE // 2)]
        self.food = self.spawn_food()
        self.done = False
        self.score = 0

    def spawn_food(self):
        while True:
            pos = (
                random.randint(0, GRID_SIZE - 1),
                random.randint(0, GRID_SIZE - 1)
            )
            if pos not in self.snake:
                return pos


def is_collision(pos, snake):
    x, y = pos
    if x < 0 or x >= GRID_SIZE or y < 0 or y >= GRID_SIZE:
        return True
    if pos in snake:
        return True
    return False


def get_new_direction(current_direction, action):
    idx = DIRECTIONS.index(current_direction)
    if action == STRAIGHT:
        return current_direction
    elif action == TURN_LEFT:
        return DIRECTIONS[(idx - 1) % 4]
    elif action == TURN_RIGHT:
        return DIRECTIONS[(idx + 1) % 4]


def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def step(game, action):
    game.direction = get_new_direction(game.direction, action)

    head_x, head_y = game.snake[0]
    dx, dy = game.direction
    new_head = (head_x + dx, head_y + dy)
    game.snake.insert(0, new_head)

    if is_collision(new_head, game.snake[1:]):
        game.done = True
        return

    if new_head == game.food:
        game.score += 1
        game.food = game.spawn_food()
    else:
        game.snake.pop()


# =========================
# STATE REPRESENTATION
# =========================
def get_state(snake, food, direction):
    head_x, head_y = snake[0]
    food_x, food_y = food

    state = (
        int(food_x < head_x),
        int(food_x > head_x),
        int(food_y < head_y),
        int(food_y > head_y),

        int(is_collision((head_x, head_y - 1), snake)),
        int(is_collision((head_x, head_y + 1), snake)),
        int(is_collision((head_x - 1, head_y), snake)),
        int(is_collision((head_x + 1, head_y), snake)),

        int(direction == UP),
        int(direction == DOWN),
        int(direction == LEFT),
        int(direction == RIGHT),
    )

    return state


# =========================
# LOAD TRAINED Q-TABLE
# =========================
with open("q_table.pkl", "rb") as f:
    q_table = pickle.load(f)

q_table = defaultdict(float, q_table)


def choose_best_action(state):
    q_values = [q_table[(state, a)] for a in ACTIONS]
    return ACTIONS[q_values.index(max(q_values))]


# =========================
# DRAWING
# =========================
def draw_grid(screen):
    for x in range(0, WINDOW_SIZE, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, WINDOW_SIZE))
    for y in range(0, WINDOW_SIZE, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (WINDOW_SIZE, y))


def draw_snake(screen, snake):
    for seg in snake:
        rect = pygame.Rect(
            seg[0] * CELL_SIZE,
            seg[1] * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
        pygame.draw.rect(screen, GREEN, rect)


def draw_food(screen, food):
    rect = pygame.Rect(
        food[0] * CELL_SIZE,
        food[1] * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
    )
    pygame.draw.rect(screen, RED, rect)


# =========================
# MAIN LOOP
# =========================
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 40))
    pygame.display.set_caption("Snake Q-Learning Demo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 30)

    game = SnakeGame()
    state = get_state(game.snake, game.food, game.direction)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        action = choose_best_action(state)
        step(game, action)

        if game.done:
            time.sleep(1)
            game.reset()

        state = get_state(game.snake, game.food, game.direction)

        screen.fill(WHITE)
        draw_grid(screen)
        draw_snake(screen, game.snake)
        draw_food(screen, game.food)

        score_text = font.render(f"Score: {game.score}", True, BLUE)
        screen.blit(score_text, (10, WINDOW_SIZE + 5))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()