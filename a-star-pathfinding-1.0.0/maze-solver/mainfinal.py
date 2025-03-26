import pygame
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
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze solver")
WINDOW.fill(BACKGROUND)

# Function to convert screen coordinates to graph coordinates
def get_clicked_pos(pos):
    """
    Returns the (row, col) pair on the graph from the specified (x, y) on the
    screen.
    """
    x, y = pos
    row = (y - PADDING) // NODE_SIZE
    col = (x - PADDING) // NODE_SIZE
    return row, col

# Function to set the active algorithm
def set_algorithm(algorithm):
    global active_algorithm
    active_algorithm = algorithm
    print(f"Algorithm set to: {algorithm}")  # Debugging message

# Function to run the selected algorithm's search
def run_search(graph, algorithm):
    if algorithm == 'A*':
        a_star(graph, graph.get_start_node(), graph.get_end_node())
    elif algorithm == 'D*':
        d_star(graph, graph.get_start_node(), graph.get_end_node())
    elif algorithm == 'D* Lite':
        d_star_lite(graph, graph.get_start_node(), graph.get_end_node())
    elif algorithm == 'Dijkstra':
        dijkstra(graph, graph.get_start_node(), graph.get_end_node())

# Main function
def main():
    btn_size = (NODE_SIZE * 3, NODE_SIZE)

    clear_btn_color = (0xFF, 0x28, 0x00)  # red color
    maze_btn_color = (0x00, 0xC0, 0x41)  # green color
    a_star_btn_color = (0x00, 0xA8, 0xE8)  # blue color
    d_star_btn_color = (0x28, 0xF4, 0x8B)  # yellow-green color
    d_star_lite_btn_color = (0xFF, 0xA8, 0x00)  # orange color
    dijkstra_btn_color = (0x64, 0x64, 0x64)  # grey color

    # Initialize the graph
    graph = Graph(ROWS, COLUMNS)

    # Create buttons
    clear_btn = Button(clear_btn_color, PADDING, NODE_SIZE * 0.5, btn_size, graph.clear)
    clear_btn.draw(WINDOW)

    maze_btn = Button(
        maze_btn_color,
        WIDTH - NODE_SIZE * 5,
        NODE_SIZE * 0.5,
        btn_size,
        lambda: generate_maze(graph, lambda: graph.draw(WINDOW)),
    )
    maze_btn.draw(WINDOW)

    # A* button
    a_star_btn = Button(
        a_star_btn_color,
        PADDING * 4,
        NODE_SIZE * 0.5,
        btn_size,
        lambda: set_algorithm('A*'),
    )
    a_star_btn.draw(WINDOW)

    # D* button
    d_star_btn = Button(
        d_star_btn_color,
        PADDING * 7,
        NODE_SIZE * 0.5,
        btn_size,
        lambda: set_algorithm('D*'),
    )
    d_star_btn.draw(WINDOW)

    # D* Lite button
    d_star_lite_btn = Button(
        d_star_lite_btn_color,
        PADDING * 10,
        NODE_SIZE * 0.5,
        btn_size,
        lambda: set_algorithm('D* Lite'),
    )
    d_star_lite_btn.draw(WINDOW)

    # Dijkstra button
    dijkstra_btn = Button(
        dijkstra_btn_color,
        PADDING * 13,
        NODE_SIZE * 0.5,
        btn_size,
        lambda: set_algorithm('Dijkstra'),
    )
    dijkstra_btn.draw(WINDOW)

    # Initialize active_algorithm variable
    global active_algorithm
    active_algorithm = None  # Initially no algorithm is selected

    running = True
    start_clicked = end_clicked = False
    global has_searched
    has_searched = False

    # Main event loop
    while running:
        graph.draw(WINDOW)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            alt_down = pygame.key.get_mods() & pygame.KMOD_ALT

            if event.type == pygame.MOUSEBUTTONDOWN:
                if clear_btn.handle_event(event):
                    has_searched = False
                    graph.clear()  # Clear the graph as well
                    graph.draw(WINDOW)

                if maze_btn.handle_event(event):
                    has_searched = False
                    graph.clear()  # Clear the graph and regenerate maze
                    generate_maze(graph, lambda: graph.draw(WINDOW))

                # Handle algorithm button clicks
                if a_star_btn.handle_event(event):
                    set_algorithm('A*')
                    has_searched = True
                    # Run search immediately after selecting algorithm
                    run_search(graph, 'A*')

                if d_star_btn.handle_event(event):
                    set_algorithm('D*')
                    has_searched = True
                    # Run search immediately after selecting algorithm
                    run_search(graph, 'D*')

                if d_star_lite_btn.handle_event(event):
                    set_algorithm('D* Lite')
                    has_searched = True
                    # Run search immediately after selecting algorithm
                    run_search(graph, 'D* Lite')

                if dijkstra_btn.handle_event(event):
                    set_algorithm('Dijkstra')
                    has_searched = True
                    # Run search immediately after selecting algorithm
                    run_search(graph, 'Dijkstra')

                left_mouse_clicked = event.button == 1

                if left_mouse_clicked:
                    pos = event.pos
                    graph_coordinate = get_clicked_pos(pos)

                    if graph.is_start(graph_coordinate):
                        start_clicked = True
                    elif graph.is_end(graph_coordinate):
                        end_clicked = True
                    else:
                        graph.toggle_wall(graph_coordinate)

            elif event.type == pygame.MOUSEBUTTONUP:
                start_clicked = False
                end_clicked = False

            # Left mouse down (event.buttons[0])
            elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
                current = event.pos
                pos = get_clicked_pos(current)

                if start_clicked and not graph.is_wall(pos) and not graph.is_end(pos):
                    graph.update_start(pos)

                    # Re-run the selected search algorithm immediately after moving start
                    if active_algorithm:
                        run_search(graph, active_algorithm)

                elif end_clicked and not graph.is_wall(pos) and not graph.is_start(pos):
                    graph.update_end(pos)

                    # Re-run the selected search algorithm immediately after moving end
                    if active_algorithm:
                        run_search(graph, active_algorithm)

                elif not graph.is_start(pos) and not graph.is_end(pos):
                    if alt_down:
                        graph.make_empty(pos)
                    else:
                        graph.make_wall(pos)

                    # Re-run the selected search algorithm immediately after modifying the grid
                    if active_algorithm:
                        run_search(graph, active_algorithm)

        pygame.display.update()  # Always update the display at the end of the loop

    pygame.quit()


# Run the main function
main()
