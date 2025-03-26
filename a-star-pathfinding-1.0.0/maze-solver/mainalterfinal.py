import pygame
import time
from graph import Graph
from maze import generate_maze
from constants import WIDTH, HEIGHT, ROWS, COLUMNS, PADDING, NODE_SIZE
from a_star import a_star
from d_star import d_star
from d_star_lite import d_star_lite
from dijkstra import dijkstra
from buttons import Button

pygame.init()

# Set up window
BACKGROUND = (0x00, 0x17, 0x1F)
TEXT_COLOR = (255, 255, 255)
FONT = pygame.font.Font(None, 30)
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Solver")
WINDOW.fill(BACKGROUND)

def get_clicked_pos(pos):
    """Returns the (row, col) pair on the graph from the specified (x, y) on the screen."""
    x, y = pos
    row = (y - PADDING) // NODE_SIZE
    col = (x - PADDING) // NODE_SIZE
    return row, col

def run_search(graph, algorithm):
    global active_algorithm, traversal_time
    active_algorithm = algorithm  # Store the active algorithm
    graph.clear_path()  # Clear previous path before running a new search
    
    start_time = time.time()
    if algorithm == 'A*':
        a_star(graph, graph.get_start_node(), graph.get_end_node())
    elif algorithm == 'D*':
        d_star(graph, graph.get_start_node(), graph.get_end_node())
    elif algorithm == 'D* Lite':
        d_star_lite(graph, graph.get_start_node(), graph.get_end_node())
    elif algorithm == 'Dijkstra':
        dijkstra(graph, graph.get_start_node(), graph.get_end_node())
    end_time = time.time()
    
    traversal_time = round((end_time - start_time) * 1000, 2)  # Time in milliseconds

def display_info():
    """Displays the selected algorithm, traversal time, and optimal choice."""
    info_text = f"Algorithm: {active_algorithm if active_algorithm else 'None'} | Time: {traversal_time} ms"
    optimal_choice = "Optimal Choice: A* (Fastest)" if active_algorithm in ['A*', 'Dijkstra'] else "Optimal Choice: D* (Dynamic)"
    
    text_surface = FONT.render(info_text, True, TEXT_COLOR)
    optimal_surface = FONT.render(optimal_choice, True, TEXT_COLOR)
    WINDOW.blit(text_surface, (PADDING, HEIGHT - 40))
    WINDOW.blit(optimal_surface, (PADDING, HEIGHT - 20))

def main():
    global active_algorithm, traversal_time
    active_algorithm = None  # No algorithm selected initially
    traversal_time = 0
    
    graph = Graph(ROWS, COLUMNS)  # Start with an empty grid containing source & destination only
    
    # Buttons
    btn_size = (NODE_SIZE * 3, NODE_SIZE)
    reset_btn = Button((0xFF, 0x28, 0x00), PADDING, NODE_SIZE * 0.5, btn_size, lambda: graph.clear_path())  # Reset grid
    maze_btn = Button((0x00, 0xC0, 0x41), WIDTH - NODE_SIZE * 5, NODE_SIZE * 0.5, btn_size, lambda: generate_maze(graph, lambda: graph.draw(WINDOW)))  # Maze generation
    a_star_btn = Button((0x00, 0xA8, 0xE8), PADDING * 4, NODE_SIZE * 0.5, btn_size, lambda: run_search(graph, 'A*'))  # A*
    d_star_btn = Button((0x28, 0xF4, 0x8B), PADDING * 7, NODE_SIZE * 0.5, btn_size, lambda: run_search(graph, 'D*'))  # D*
    d_star_lite_btn = Button((0xFF, 0xA8, 0x00), PADDING * 10, NODE_SIZE * 0.5, btn_size, lambda: run_search(graph, 'D* Lite'))  # D* Lite
    dijkstra_btn = Button((0x64, 0x64, 0x64), PADDING * 13, NODE_SIZE * 0.5, btn_size, lambda: run_search(graph, 'Dijkstra'))  # Dijkstra
    
    buttons = [reset_btn, maze_btn, a_star_btn, d_star_btn, d_star_lite_btn, dijkstra_btn]
    
    running = True
    start_clicked = end_clicked = False
    
    while running:
        WINDOW.fill(BACKGROUND)  # Clear screen before drawing
        graph.draw(WINDOW)
        
        # Draw buttons once per loop without flickering
        for button in buttons:
            button.draw(WINDOW)
        
        # Display algorithm info and optimal choice
        display_info()
        pygame.display.update()  # Update only once per frame
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                
                # Check if any button is clicked
                button_clicked = False
                for button in buttons:
                    if button.handle_event(event):
                        button_clicked = True
                        break  # Prevent further processing if a button was clicked
                
                if not button_clicked:
                    row, col = get_clicked_pos(pos)
                    
                    if graph.is_start((row, col)):
                        start_clicked = True
                    elif graph.is_end((row, col)):
                        end_clicked = True
                    else:
                        graph.toggle_wall((row, col))
                        graph.clear_path()  # Remove previous path
                        if active_algorithm:
                            run_search(graph, active_algorithm)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                start_clicked = False
                end_clicked = False

            elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
                pos = get_clicked_pos(event.pos)
                
                if start_clicked and not graph.is_wall(pos) and not graph.is_end(pos):
                    graph.update_start(pos)
                    graph.clear_path()
                    if active_algorithm:
                        run_search(graph, active_algorithm)
                elif end_clicked and not graph.is_wall(pos) and not graph.is_start(pos):
                    graph.update_end(pos)
                    graph.clear_path()
                    if active_algorithm:
                        run_search(graph, active_algorithm)
                else:
                    graph.make_wall(pos)
                    graph.clear_path()
                    if active_algorithm:
                        run_search(graph, active_algorithm)
    
    pygame.quit()

main()
