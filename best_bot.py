from collections import deque
import heapq
from game_world.racetrack import RaceTrack
from copy import deepcopy

Point = tuple[int, int]


class best_bot:
    """
    class for the bot\n
    use in game.py:\n
        from best_bot import best_bot
        PLAYER = best_bot()
    """

    def __init__(self) -> None:
        self.map_target: Point | None = None
        self.current_path: deque[Point] = deque()

    def __call__(self, location: Point, map: RaceTrack) -> Point:
        return self.best_move(location, map)
        # return self.test_move(location, map)


    def dist(self, p1: Point, p2: Point) -> int:
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def getVector(self, a: Point, b: Point) -> tuple[int, int]:
        """
        takes points a and b, returns vector from a to b

        :return: vector ab
        :rtype: tuple[int, int]
        """
        # only returns unit vectors if a and b are neighbors
        return (b[0] - a[0], b[1] - a[1])

    def searialize(self, map: RaceTrack) -> bytes:
        return map.active.tobytes()

    def tvrs_neighbors(
        self,
        cell: Point,
        map: RaceTrack,
    ) -> set[Point]:
        """
        Takes a cell as input and returns its traversable neighbors

        :return: set of neighbors, up to 4
        :rtype: set[Point]
        """
        neighbors: set[Point] = set()
        traversable = map.find_traversable_cells()
        moves = [(1, 0), (0, 1), (-1, 0), (0, -1)]

        for move in moves:
            new_cell = (cell[0] + move[0], cell[1] + move[1])
            if new_cell in traversable:
                neighbors.add(new_cell)
        return neighbors

    def simulate_move(self, move: Point, map: RaceTrack) -> RaceTrack:
        # move is location after move, not vector
        if move in map.find_buttons():
            color = map.button_colors[move]
            new_map = deepcopy(map)
            new_map.toggle(color)
            return new_map
        else:
            return map

    def astar(
        self,
        starting_point: Point,
        target: Point,
        map: RaceTrack,
    ) -> deque[Point]:
        """
        finds shortest path between two points on the map

        :return: sequence of cells from starting point to ending point
        :rtype: list[Point]
        """

        frontier = list()
        camefrom = dict()
        path = deque()
        found = False

        # add first cell to frontier
        # tuple is f-score, g-score, cell:point
        heapq.heappush(frontier, (self.dist(starting_point, target), 0, starting_point))
        camefrom[starting_point] = None

        # expand frontier until all cells explored or shortest path found
        while len(frontier) > 0:
            # unpack tuple
            (current_f, current_g, current_position) = frontier[0]

            if current_position == target:
                found = True
                break

            heapq.heappop(frontier)

            for loc in self.tvrs_neighbors(current_position, map):
                if loc not in camefrom:
                    camefrom[loc] = current_position
                    heapq.heappush(
                        frontier,
                        (self.dist(loc, target) + current_g + 1, current_g + 1, loc),
                    )

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

    def astar2(
        self,
        starting_point: Point,
        target: Point,
        starting_map: RaceTrack,
    ) -> deque[Point]:
        """
        finds shortest path between two points on the map

        :type buttonless: bool
        :return: sequence of cells from starting point to ending point
        :rtype: list[Point]
        """

        frontier: list[tuple] = list()
        g_scores: dict[tuple[Point, bytes], int] = dict()
        camefrom: dict[tuple[Point, bytes], tuple]= dict()
        path: deque[Point] = deque()
        end_state: bytes | None = None
        tiebreaker: int = 0

        # add first cell to frontier
        # tuple is f-score, g-score, cell:point, map at that point
        s_map_bytes = self.searialize(starting_map)
        camefrom[(starting_point, s_map_bytes)] = (None, None)
        g_scores[(starting_point, s_map_bytes)] = 0
        frontier.append(
            (self.dist(starting_point, target), 0, starting_point, tiebreaker, starting_map)
        )

        # expand frontier until all cells explored or shortest path found
        while frontier:
            # unpack tuple
            (
                current_f,
                current_g,
                current_position,
                _,
                current_map
            ) = heapq.heappop(frontier)

            if current_position == target:
                end_state = self.searialize(current_map) 
                break

            for loc in self.tvrs_neighbors(current_position, current_map):
                c_map_bytes = self.searialize(current_map)
                new_map = self.simulate_move(loc, current_map)
                n_map_bytes = self.searialize(new_map)
                if (
                    (loc, n_map_bytes) not in camefrom or
                    current_g + 1 < g_scores[(loc, n_map_bytes)]
                ):
                    camefrom[(loc, n_map_bytes)] = (current_position, c_map_bytes)
                    g_scores[(loc, n_map_bytes)] = current_g + 1
                    heapq.heappush(
                        frontier,
                        (
                            self.dist(loc, target) + current_g + 1,
                            current_g + 1,
                            loc,
                            tiebreaker,
                            new_map,
                        ),
                    )
                    tiebreaker += 1

        # return empty path if no possible path to target
        # use end_state instead of a found flag to avoid linter error
        if end_state == None:
            return deque()

        # creating path
        current_position = target  # should already be the case but just in case
        current_map = end_state  # should already be the case but just in case
        while (current_position, current_map) != (None, None):
            path.appendleft(current_position)
            (
                current_position, current_map
            ) = camefrom[(current_position, current_map)]
        path.popleft()
        return path

    def best_move(self, location: Point, map: RaceTrack) -> Point:
        # on first move
        if self.map_target == None:
            self.map_target = map.target

            # self.current_path = self.astar(
            #     location,
            #     self.map_target,
            #     map,
            #     True
            # )

            self.current_path = self.astar2(
                location,
                self.map_target,
                map,
            )

        if len(self.current_path) > 0:
            vec = self.getVector(location, self.current_path.popleft())
            return vec
            # return self.getVector(location, self.current_path.popleft())
        else:
            raise ZeroDivisionError("no move")