import pygame
import random

# Coded by Mahdi Hasan, Do not copy :)
# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 300, 600
BLOCK_SIZE = 30
COLUMNS, ROWS = WIDTH // BLOCK_SIZE, HEIGHT // BLOCK_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),  # Cyan
    (0, 0, 255),    # Blue
    (255, 165, 0),  # Orange
    (255, 255, 0),  # Yellow
    (0, 255, 0),    # Green
    (128, 0, 128),  # Purple
    (255, 0, 0),    # Red
]

# Tetrimino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
]

class Tetrimino:
    def __init__(self, shape):
        self.shape = shape
        self.color = random.choice(COLORS)
        self.x = COLUMNS // 2 - len(shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        grid[y][x] = color
    return grid

def draw_grid(surface, grid):
    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            pygame.draw.rect(surface, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    for x in range(COLUMNS):
        pygame.draw.line(surface, WHITE, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, HEIGHT))
    for y in range(ROWS):
        pygame.draw.line(surface, WHITE, (0, y * BLOCK_SIZE), (WIDTH, y * BLOCK_SIZE))

def check_collision(tetrimino, grid):
    for y, row in enumerate(tetrimino.shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = tetrimino.x + x
                new_y = tetrimino.y + y
                if new_x < 0 or new_x >= COLUMNS or new_y >= ROWS or grid[new_y][new_x] != BLACK:
                    return True
    return False

def clear_rows(grid, locked_positions):
    cleared = 0
    for y in range(len(grid) - 1, -1, -1):
        if BLACK not in grid[y]:
            cleared += 1
            del grid[y]
            grid.insert(0, [BLACK for _ in range(COLUMNS)])
    if cleared:
        for (x, y) in list(locked_positions):
            if y >= cleared:
                locked_positions[(x, y - cleared)] = locked_positions.pop((x, y))
    return cleared

def draw_next_tetrimino(surface, next_tetrimino):
    font = pygame.font.Font(None, 30)
    label = font.render("Next Piece", True, WHITE)
    surface.blit(label, (WIDTH + 10, 10))
    for y, row in enumerate(next_tetrimino.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(
                    surface, next_tetrimino.color, 
                    (WIDTH + 10 + x * BLOCK_SIZE, 40 + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                )

def main():
    screen = pygame.display.set_mode((WIDTH + 150, HEIGHT))
    pygame.display.set_caption("Baler Tetris Game (Made by Mahdi Hasan)")

    clock = pygame.time.Clock()
    locked_positions = {}
    grid = create_grid(locked_positions)
    
    current_tetrimino = Tetrimino(random.choice(SHAPES))
    next_tetrimino = Tetrimino(random.choice(SHAPES))
    
    fall_time = 0
    fall_speed = 0.3
    score = 0
    
    running = True
    while running:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= fall_speed:
            current_tetrimino.y += 1
            if check_collision(current_tetrimino, grid):
                current_tetrimino.y -= 1
                for y, row in enumerate(current_tetrimino.shape):
                    for x, cell in enumerate(row):
                        if cell:
                            locked_positions[(current_tetrimino.x + x, current_tetrimino.y + y)] = current_tetrimino.color
                current_tetrimino = next_tetrimino
                next_tetrimino = Tetrimino(random.choice(SHAPES))
                if check_collision(current_tetrimino, grid):
                    running = False  # Game over
                score += clear_rows(grid, locked_positions) * 10
            fall_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_tetrimino.x -= 1
                    if check_collision(current_tetrimino, grid):
                        current_tetrimino.x += 1
                if event.key == pygame.K_RIGHT:
                    current_tetrimino.x += 1
                    if check_collision(current_tetrimino, grid):
                        current_tetrimino.x -= 1
                if event.key == pygame.K_DOWN:
                    current_tetrimino.y += 1
                    if check_collision(current_tetrimino, grid):
                        current_tetrimino.y -= 1
                if event.key == pygame.K_UP:
                    current_tetrimino.rotate()
                    if check_collision(current_tetrimino, grid):
                        for _ in range(3):  # Rotate back to original position
                            current_tetrimino.rotate()

        draw_grid(screen, grid)
        for y, row in enumerate(current_tetrimino.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        screen, current_tetrimino.color,
                        ((current_tetrimino.x + x) * BLOCK_SIZE,
                         (current_tetrimino.y + y) * BLOCK_SIZE,
                         BLOCK_SIZE, BLOCK_SIZE)
                    )
        draw_next_tetrimino(screen, next_tetrimino)

        pygame.display.flip()
        screen.fill(BLACK)

    pygame.quit()
    print(f"Game Over! Your Score: {score}")

if __name__ == "__main__":
    main()
