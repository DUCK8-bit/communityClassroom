from queue import PriorityQueue
from node_type import NodeType

FAILURE = []

def d_star_lite(graph, start_node, end_node, draw=None, h=None):
    if h is None:
        def h(n):
            return abs(end_node.row - n.row) + abs(end_node.col - n.col)

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

    # rhs_score: The shortest cost to the goal (in D* Lite, this value is used for node re-planning)
    rhs_score = {node: float("inf") for row in graph.get_grid() for node in row}

    # Initialize the start and end nodes
    g_score[start_node] = 0
    rhs_score[start_node] = h(start_node)

    # Initialize the open_set with the start node
    open_set.put((rhs_score[start_node], start_node))

    def update_node_costs(node):
        if node == start_node:
            return

        min_rhs = float("inf")
        for neighbor in graph.get_neighbors(node):
            if not neighbor.is_wall():
                cost = g_score[neighbor] + 1  # Cost between adjacent nodes is 1
                min_rhs = min(min_rhs, cost)

        rhs_score[node] = min_rhs

    def get_min_rhs():
        return open_set.get() if not open_set.empty() else None

    while not open_set.empty():
        # Get the node with the lowest cost (priority)
        _, current = open_set.get()

        # Draw the current state
        current.visits()
        draw()

        if current == end_node:
            return reconstruct_path(came_from, start_node, end_node, draw)

        # Update cost and rhs for each neighbor
        for neighbor in graph.get_neighbors(current):
            if not neighbor.is_wall():
                tentative_g_score = g_score[current] + 1  # assuming uniform cost for movement
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    open_set.put((g_score[neighbor], neighbor))

                update_node_costs(neighbor)

    return FAILURE


def reconstruct_path(came_from, start, end, draw):
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
