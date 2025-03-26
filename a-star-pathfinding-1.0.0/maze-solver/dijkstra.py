import heapq
from node_type import NodeType

def dijkstra(graph, start_node, end_node, draw=None):
    open_set = []
    heapq.heappush(open_set, (0, start_node))  # Priority queue, starting with the start node
    came_from = {}
    g_score = {node: float("inf") for row in graph.get_grid() for node in row}
    g_score[start_node] = 0
    visited_nodes = set()
    
    # Flag to track if the search has been completed
    path_found = False

    while open_set:
        current_cost, current_node = heapq.heappop(open_set)

        # Skip visited nodes to avoid redundant processing
        if current_node in visited_nodes:
            continue

        visited_nodes.add(current_node)

        # When we reach the end node, we stop searching and reconstruct the path
        if current_node == end_node:
            path_found = True
            break

        for neighbor in graph.get_neighbors(current_node):
            if neighbor.is_wall() or neighbor in visited_nodes:
                continue

            tentative_g_score = g_score[current_node] + 1

            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current_node
                g_score[neighbor] = tentative_g_score
                heapq.heappush(open_set, (g_score[neighbor], neighbor))

        # Redraw only if something meaningful changes
        if draw:
            draw()

    if path_found:
        return reconstruct_path(came_from, start_node, end_node, draw)
    else:
        return []

def reconstruct_path(came_from, start, end, draw):
    current = end
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.reverse()

    for node in path:
        node.update_type(NodeType.PATH)
        if draw:
            draw()

    return path
