from collections import deque
import heapq
from game_world.racetrack import RaceTrack
import random

Point = tuple[int, int]

class best_bot:
    """
    class for the bot\n
    use in game.py:\n
        from best_bot import best_bot
        PLAYER = best_bot()
    """
    def __init__(self) -> None:
        self.current_target: Point | None = None
        self.current_path: deque[Point] = deque()

    # makes instance of class callable and provides move when called
    # this makes it possible to store variables across multiple calls of best_move
    def __call__(self, location: Point, map: RaceTrack) -> Point:
        return self.best_move(location, map)


    def astar(self, starting_point: Point, target: Point, map: RaceTrack) -> deque[Point]:
        """
        finds shortest path between two points on the map
        
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
        path = deque()
        found = False

        # add first cell to frontier
        # tuple is f-score, g-score, cell:point
        heapq.heappush(frontier, (dist(starting_point, target), 0, starting_point))
        camefrom[starting_point] = None

        # expand frontier until all cells explored or shortest path found
        while len(frontier) > 0:
            # unpack tuple
            (current_f, current_g, current_position) = frontier[0]

            if current_position == target:
                found = True
                break

            heapq.heappop(frontier)

            for loc in neighbors(current_position):
                if loc not in camefrom:
                    camefrom[loc] = current_position
                    heapq.heappush(frontier, (dist(loc, target) + current_g + 1, current_g + 1, loc))

        # return empty path if no possible path to target
        if found == False:
            return deque()

        # creating path
        current_position = target
        while current_position != starting_point:
            path.appendleft(current_position)
            current_position = camefrom[current_position]
        path.appendleft(starting_point)

        return path
    
    def getVector(self, a: Point, b: Point) -> tuple[int, int]:
        """
        takes points a and b, returns vector from a to b
        
        :return: vector ab
        :rtype: tuple[int, int]
        """
        # only returns unit vectors if a and b are neighbors
        return (b[0] - a[0], b[1] - a[1])

    def best_move(self, location: Point, map: RaceTrack) -> Point:
        # on first move
        if self.current_target == None:
            traversable = map.find_traversable_cells()
            cells: list[Point] = []
            for cell in traversable:
                cells.append(cell)
            self.current_target = random.choice(cells)
            self.current_path = self.astar(location, self.current_target, map)
        
        return self.getVector(location, self.current_path.popleft())