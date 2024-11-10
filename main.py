import pygame
import random
from queue import Queue, LifoQueue, PriorityQueue
import heapq

# Screen and grid dimensions
WIDTH, HEIGHT = 800, 700
GRID_WIDTH, GRID_HEIGHT = 15, 10
CELL_SIZE = WIDTH // GRID_WIDTH
BUTTONS_START_MARGIN = 160

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
LIGHT_GRAY = (200,200,200)

# Different search algorithms
SEARCH_ALGORITHMS = ['Breadth-First', 'Depth-First', 'Uniform-Cost', 'Greedy', 'A*']

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()  # Initialize clock for FPS control
FPS = 24  # Set desired frames per second
pygame.display.set_caption("Search Snake Game")

font = pygame.font.Font(None, 36)

# Define grid and initial state
grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
visited = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
start, target = None, None
algorithm = SEARCH_ALGORITHMS[0]

# Create obstacles
def place_obstacles(nObjects=25):
    # obstacles = [(random.choice([RED, BLUE, GREEN])) for _ in range(9)]
    obstacles = [BLACK for _ in range(9)]

    for _ in range(nObjects):
        x, y = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
        while grid[y][x]:  # Avoid placing on the same spot
            x, y = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
        grid[y][x] = random.choice(obstacles)

# Implementing BFS with animation support
def bfs(start, target):
    queue = Queue()
    queue.put((start, [start]))
    visited = set()
    visited.add(start)
    
    while not queue.empty():
        (current, path) = queue.get()
        
        # Yield for visualization at each step
        yield (path, visited)
        
        if current == target:
            return path, visited  # Return final path and visited cells
        
        for neighbor in get_neighbors(current):
            if neighbor not in visited and is_free_cell(neighbor):
                visited.add(neighbor)
                queue.put((neighbor, path + [neighbor]))
    
    return [], visited  # Return an empty path if no path is found

def dfs(start, target):
    stack = LifoQueue()
    stack.put((start, [start]))
    visited = set()
    visited.add(start)
    
    while not stack.empty():
        (current, path) = stack.get()
        
        # Yield for visualization at each step
        yield (path, visited)
        
        if current == target:
            return path, visited  # Return final path and visited cells
        
        for neighbor in get_neighbors(current):
            if neighbor not in visited and is_free_cell(neighbor):
                visited.add(neighbor)
                stack.put((neighbor, path + [neighbor]))
    
    return [], visited  # Return an empty path if no path is found

# Implementing Uniform-Cost Search
def uniform_cost_search(start, target):
    priority_queue = PriorityQueue()
    priority_queue.put((0, start, [start]))  # Cost, current node, path
    visited = {}
    visited[start] = 0
    
    while not priority_queue.empty():
        (cost, current, path) = priority_queue.get()
        
        # Yield the current state for animation
        yield path, visited.keys()
        
        if current == target:
            yield path, visited.keys()  # Final path and visited cells
            return
        
        for neighbor in get_neighbors(current):
            new_cost = cost + 1  # Assume all moves have cost 1
            if is_free_cell(neighbor) and (neighbor not in visited or new_cost < visited[neighbor]):
                visited[neighbor] = new_cost
                priority_queue.put((new_cost, neighbor, path + [neighbor]))
    
    yield [], visited.keys()  # Return an empty path if no path is found

# Implementing Greedy Best-First Search
def greedy_search(start, target):
    priority_queue = PriorityQueue()
    priority_queue.put((heuristic(start, target), start, [start]))  # Heuristic, current node, path
    visited = set()
    visited.add(start)
    
    while not priority_queue.empty():
        (_, current, path) = priority_queue.get()
        
        # Yield the current state for animation
        yield path, visited
        
        if current == target:
            yield path, visited  # Final path and visited cells
            return
        
        for neighbor in get_neighbors(current):
            if neighbor not in visited and is_free_cell(neighbor):
                visited.add(neighbor)
                priority_queue.put((heuristic(neighbor, target), neighbor, path + [neighbor]))
    
    yield [], visited  # Return an empty path if no path is found

# Implementing A* Search
def a_star(start, target):
    priority_queue = PriorityQueue()
    priority_queue.put((0 + heuristic(start, target), 0, start, [start]))  # f-score, g-score, current node, path
    visited = {}
    visited[start] = 0
    
    while not priority_queue.empty():
        (_, g, current, path) = priority_queue.get()
        
        # Yield the current state for animation
        yield path, visited.keys()
        
        if current == target:
            yield path, visited.keys()  # Final path and visited cells
            return
        
        for neighbor in get_neighbors(current):
            new_g = g + 1  # Assume all moves have cost 1
            f = new_g + heuristic(neighbor, target)
            
            if is_free_cell(neighbor) and (neighbor not in visited or new_g < visited[neighbor]):
                visited[neighbor] = new_g
                priority_queue.put((f, new_g, neighbor, path + [neighbor]))
    
    yield [], visited.keys()  # Return an empty path if no path is found

# Helper functions
def get_neighbors(cell):
    """Returns the neighboring cells in 4 directions (up, down, left, right)."""
    y, x = cell
    neighbors = [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    return [(ny, nx) for ny, nx in neighbors if 0 <= ny < GRID_HEIGHT and 0 <= nx < GRID_WIDTH]

def is_free_cell(cell):
    """Returns True if the cell is not an obstacle."""
    y, x = cell
    return grid[y][x] is None

def heuristic(a, b):
    """Heuristic function for A* and Greedy. Using Manhattan distance."""
    (y1, x1) = a
    (y2, x2) = b
    return abs(y1 - y2) + abs(x1 - x2)

# Execute the selected search algorithm
def start_search():
    if algorithm == "Breadth-First":
        return bfs(start, target)
    elif algorithm == "Depth-First":
        return dfs(start, target)
    elif algorithm == "Uniform-Cost":
        return uniform_cost_search(start, target)
    elif algorithm == "Greedy":
        return greedy_search(start, target)
    elif algorithm == "A*":
        return a_star(start, target)
    
# Render grid with obstacles, start, target, visited cells, and path
def render_grid(path=None, visited=None):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = WHITE
            if grid[y][x]:  # Obstacles
                color = grid[y][x]
            if visited and (y, x) in visited:
                color = LIGHT_GRAY  # Visited cells
            if path and (y, x) in path:
                color = YELLOW  # Solution path
            if start == (y, x):
                color = ORANGE  # Start
            if target == (y, x):
                color = PURPLE  # Target
            
            pygame.draw.rect(
                screen, color,
                (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            )
            pygame.draw.rect(
                screen, BLACK,
                (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1
            )
    
# Draw the buttons for selecting search algorithms
def draw_buttons():
    for i, algo in enumerate(SEARCH_ALGORITHMS):
        color = GREEN if algo == algorithm else WHITE
        pygame.draw.rect(screen, color, (10, HEIGHT - BUTTONS_START_MARGIN + i * 30, 150, 25))
        text = font.render(algo, True, BLACK)
        screen.blit(text, (15, HEIGHT - BUTTONS_START_MARGIN + i * 30))

# Main loop
running = True
search_generator = None  # Initialize generator for search steps
place_obstacles()
render_grid()
path = []; visited_cells = []

while running:
    screen.fill(WHITE)
    render_grid(path, visited_cells)
    draw_buttons()
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos[0] // CELL_SIZE, event.pos[1] // CELL_SIZE
            if y < GRID_HEIGHT:
                if not start:
                    start = (y, x)
                elif not target and (y, x) != start:
                    target = (y, x)
                else:
                    start, target = (y, x), None
                path = []; visited_cells = []
                search_generator = None  # Reset generator

            else:
                for i, algo in enumerate(SEARCH_ALGORITHMS):
                    if 10 <= event.pos[0] <= 160 and HEIGHT - BUTTONS_START_MARGIN + i * 30 <= event.pos[1] <= HEIGHT - BUTTONS_START_MARGIN + i * 30 + 25:
                        algorithm = algo
        
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            if start and target:
                search_generator = start_search()

    # If a search is running, take the next step
    if search_generator:
        try:
            path, visited_cells = next(search_generator)
        except StopIteration:
            search_generator = None  # Stop when done

    clock.tick(FPS)  

pygame.quit()
