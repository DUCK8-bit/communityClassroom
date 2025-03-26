from queue import PriorityQueue
from node_type import NodeType

FAILURE = []

# Helper function to calculate heuristic (Manhattan distance)
def h(n, end_node):
    return abs(end_node.row - n.row) + abs(end_node.col - n.col)

def d_star(graph, start_node, end_node, draw=None):
    if draw is None:
        def draw():
            return None

    graph.clear_path()

    # Initialize priority queue (open set)
    open_set = PriorityQueue()

    # Came_from stores the predecessors of each node
    came_from = {}

    # g_score: The cost from the start to a given node
    g_score = {node: float("inf") for row in graph.get_grid() for node in row}

    # rhs_score: The shortest cost to the goal
    rhs_score = {node: float("inf") for row in graph.get_grid() for node in row}

    # Initialize the start and end nodes
    g_score[start_node] = 0
    rhs_score[start_node] = h(start_node, end_node)

    # Add the start node to open set (priority queue)
    open_set.put((rhs_score[start_node], start_node))

    def update_rhs(node):
        """Update the rhs_score of the node based on its neighbors."""
        if node == start_node:
            return

        min_rhs = float("inf")
        for neighbor in graph.get_neighbors(node):
            if not neighbor.is_wall():
                cost = g_score[neighbor] + 1  # Assume uniform cost between adjacent nodes
                min_rhs = min(min_rhs, cost)

        rhs_score[node] = min_rhs

    def replan():
        """Main loop of the D* algorithm to process and plan the path."""
        while not open_set.empty():
            # Get the node with the lowest cost (priority)
            _, current = open_set.get()

            # Draw the current state of the grid
            current.visits()
            draw()

            # If we have reached the goal node, reconstruct the path
            if current == end_node:
                return reconstruct_path(came_from, start_node, end_node, draw)

            # Update cost and rhs for each neighbor of the current node
            for neighbor in graph.get_neighbors(current):
                if not neighbor.is_wall():
                    tentative_g_score = g_score[current] + 1  # Assume uniform cost
                    if tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        open_set.put((g_score[neighbor], neighbor))

                    update_rhs(neighbor)

    def propagate_changes():
        """If obstacles appear, propagate the changes from the goal backward."""
        # Re-plan by propagating changes backward through the graph
        for node in graph.get_grid():
            update_rhs(node)
        
        replan()

    # Start the process
    replan()

    return FAILURE

def reconstruct_path(came_from, start, end, draw):
    """Reconstruct and return the path from start to end node."""
    current = came_from[end]
    total_path = []

    while current != start:
        total_path.insert(0, current)
        current = came_from[current]

    # Mark the nodes in the path and update the visual grid
    for path in total_path:
        path.update_type(NodeType.PATH)
        draw()

    return total_path
