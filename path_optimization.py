import pygame
import random
from queue import PriorityQueue

# Screen and grid settings
WIDTH, HEIGHT = 800, 700
GRID_WIDTH, GRID_HEIGHT = 15, 10
CELL_SIZE = WIDTH // GRID_WIDTH
BUTTONS_START_MARGIN = 160
maxnSteps = 25   # Maximum allowed steps
FPS = 10  # Frames per second for animation

# Colors and points range
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (211, 211, 211)
VISITED_COLOR = (200, 200, 200)
PATH_COLOR = (255, 255, 0)
START_COLOR = (255, 165, 0)
TARGET_COLOR = (128, 0, 128)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Max Points Search with A*")

font = pygame.font.Font(None, 32)

# Generate objects with colors and points
OBJECT_POOL = [
    {'color': (255, 0, 0), 'points': 5},   # Red - 5 points
    {'color': (0, 255, 0), 'points': -3},  # Green - -3 points
    {'color': (0, 0, 255), 'points': 2},   # Blue - 2 points
    {'color': (255, 255, 0), 'points': 10},# Yellow - 10 points
    {'color': (0, 255, 255), 'points': -5},# Cyan - -5 points
    {'color': (255, 0, 255), 'points': 1}, # Magenta - 1 point
    {'color': (128, 128, 128), 'points': 3},# Gray - 3 points
    {'color': (128, 10, 128), 'points': -10},# Purple - -10 points
    {'color': (255, 165, 0), 'points': 7}   # Orange - 7 points
]

def place_objects(nObjects=25):
    for _ in range(nObjects):
        x, y = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
        while grid[y][x] is not None or (y, x) in [start, target]:  # Avoid placing on start/target
            x, y = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
        grid[y][x] = random.choice(OBJECT_POOL)

# Get neighbors
def get_neighbors(cell):
    y, x = cell
    neighbors = [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    return [(ny, nx) for ny, nx in neighbors if 0 <= ny < GRID_HEIGHT and 0 <= nx < GRID_WIDTH]

# Heuristic (Manhattan distance)
def heuristic(a, b):
    y1, x1 = a
    y2, x2 = b
    return abs(y1 - y2) + abs(x1 - x2)

# A* search with max points constraint
def a_star_max_points(start, target, max_steps):
    pq = PriorityQueue()
    pq.put((0, start, [start], 0, 0))  # (priority, current cell, path, steps taken, score)
    visited = set()
    best_path, best_score = [], float('-inf')

    while not pq.empty():
        _, current, path, steps, score = pq.get()
        
        if current == target or steps == max_steps:
            if score > best_score:
                best_path, best_score = path, score
            continue
        
        if current in visited:
            continue
        visited.add(current)
        
        for neighbor in get_neighbors(current):
            y, x = neighbor
            obj = grid[y][x]
            points = obj['points'] if obj else -5  # Get points of the object in the cell
            
            points = 200 if neighbor == target else points

            new_path = path + [neighbor]
            new_score = score + points
            
            # Prioritize paths that reach the target or have high scores
            priority = -(new_score + heuristic(neighbor, target))  # Negate for PriorityQueue
            
            pq.put((priority, neighbor, new_path, steps + 1, new_score))
    
    return best_path, visited, best_score

# Render the grid with objects and score
def render_grid(path=None, visited=None, score=0):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = WHITE
            cell = grid[y][x]
            
            if visited and (y, x) in visited:
                color = VISITED_COLOR
            if path and (y, x) in path:
                color = PATH_COLOR
            if cell:  # Object present
                color = cell['color']
            
            if (y, x) == start:
                color = START_COLOR
            elif (y, x) == target:
                color = TARGET_COLOR
            
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, BLACK, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
    
    # Display legend for object points
    display_legend()
    
    # Display score
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, HEIGHT - 30))

# Display legend on the side
def display_legend():
    font = pygame.font.Font(None, 24)
    legend_x = WIDTH - 200
    for i, obj in enumerate(OBJECT_POOL):
        color = obj['color']
        points_text = f"Points: {obj['points']}"
        pygame.draw.rect(screen, color, (legend_x, 20 + i * 30, 20, 20))
        text = font.render(points_text, True, BLACK)
        screen.blit(text, (legend_x + 30, 20 + i * 30))

# Main loop
OBJECT_POOL = [
    {'color': (255, 0, 0), 'points': 10},
    {'color': (0, 0, 0), 'points': -1000},

]

# Generate grid with random objects
grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
start, target = None, None

running = True
place_objects()
path, visited_cells = [], set()
animation_in_progress = False
setting_start = True  # Track if setting start or target
score = 0  # Total score for the collected path

while running:
    screen.fill(WHITE)
    render_grid(path, visited_cells, score)
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            grid_x, grid_y = x // CELL_SIZE, y // CELL_SIZE
            if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                if setting_start:
                    start = (grid_y, grid_x)
                    setting_start = False
                else:
                    target = (grid_y, grid_x)
                    setting_start = True
                    path, visited_cells = [], set()  # Reset path on new target selection
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s and start and target:
                # Start A* search for maximum points
                path, visited_cells, score = a_star_max_points(start, target, maxnSteps)
                animation_in_progress = True
    clock.tick(FPS)  # Control FPS

pygame.quit()
