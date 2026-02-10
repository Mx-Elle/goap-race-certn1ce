import heapq
from game_world.racetrack import RaceTrack

Point = tuple[int, int]



def astar(location: Point, target: Point, map: RaceTrack) -> list[Point]:
    """
    finds shortest path between two points on the map
    
    :param location: starting point
    :type location: Point
    :param target: ending point
    :type target: Point
    :param map: map containing the maze
    :type map: RaceTrack
    :return: sequence of cells from starting point to ending point
    :rtype: list[Point]
    """

    def dist(p1: Point, p2: Point) -> int:
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
    
    def neighbors(cell: Point) -> set[Point]:
        """
        Takes a cell as input and returns its traversable neighbors
        
        :param cell: cell to search for neighbors
        :type cell: Point
        :return: set of neighbors, up to 4
        :rtype: set[Point]
        """
        neighbors: set[Point]= set()
        traversable = map.find_traversable_cells()
        moves = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        for move in moves:
            move = (cell[0] + move[0], cell[1] + move[1])
            if move in traversable:
                neighbors.add(move)
        return neighbors

    frontier = list()
    camefrom = dict()
    path = list()
    found = False

    # add first cell to frontier
    # tuple is f-score, g-score, cell:point
    heapq.heappush(frontier, (dist(location, target), 0, location))
    camefrom[location] = None

    # expand frontier until all cells explored or shortest path found
    while len(frontier) > 0:
        # unpack tuple
        (current_f, current_g, current_loc) = frontier[0]

        if current_loc == target:
            found = True
            break

        heapq.heappop(frontier)

        for loc in neighbors(current_loc):
            if loc not in camefrom:
                camefrom[loc] = current_loc
                heapq.heappush(frontier, (dist(loc, target) + current_g + 1, current_g + 1, loc))

    # return empty path if no possible path to target
    if found == False:
        return []

    # creating path
    current_loc = target
    while current_loc != location:
        path.append(current_loc)
        current_loc = camefrom[current_loc]
    path.append(location)
    path.reverse()

    return path

def best_move(location: Point, map: RaceTrack) -> Point:
    return (0, 0)