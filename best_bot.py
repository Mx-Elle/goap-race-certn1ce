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
        self.first_run: bool = True
        self.current_path: deque[Point] = deque()

    def __call__(self, location: Point, map: RaceTrack) -> Point:
        return self.best_move(location, map)


    def dist(self, p1: Point, p2: Point) -> int:
        """
        manhattan distance between points
        
        :return: absolute value distance
        :rtype: int
        """
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def getVector(self, a: Point, b: Point) -> tuple[int, int]:
        """
        vector between points ab

        :return: vector ab
        :rtype: tuple[int, int]
        """
        # only returns unit vectors if a and b are neighbors
        return (b[0] - a[0], b[1] - a[1])

    def searialize(self, map: RaceTrack) -> bytes:
        """
        hashable active array from map\n
        useful for comparing game states
        
        :return: bytes of active array
        :rtype: bytes
        """
        return map.active.tobytes()

    def tvrs_neighbors(
        self,
        cell: Point,
        map: RaceTrack,
    ) -> set[Point]:
        """
        takes a cell as input and returns its traversable neighbors

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

    def simulate_move(self, cell: Point, map: RaceTrack) -> RaceTrack:
        """
        returns map after a simulated move to cell on the map passed as argument
        \nif a button is located at cell, a new map is returned
        \notherwise the same map is returned
        
        :return: map after move
        :rtype: RaceTrack
        """
        # cell is location after move, not vector
        if cell in map.find_buttons():
            color = map.button_colors[cell]
            new_map = deepcopy(map)
            new_map.toggle(color)
            return new_map
        else:
            return map

    def astar(
        self,
        starting_point: Point,
        target: Point,
        starting_map: RaceTrack,
    ) -> deque[Point]:
        """
        finds shortest path between two points on the map

        :return: sequence of cells from starting point to target
        :rtype: list[Point]
        """

        frontier: list[tuple] = list()
        g_scores: dict[tuple[Point, bytes], int] = dict()
        camefrom: dict[tuple[Point, bytes], tuple]= dict()
        path: deque[Point] = deque()
        end_state: bytes | None = None
        tiebreaker: int = 0

        # add first cell to frontier
        # tuple is f-score, g-score, cell:point, tiebreaker, map at that point
        s_map_bytes = self.searialize(starting_map)
        camefrom[(starting_point, s_map_bytes)] = (None, None)
        g_scores[(starting_point, s_map_bytes)] = 0
        frontier.append(
            (
                self.dist(starting_point, target),
                0,
                starting_point,
                tiebreaker,
                starting_map
            )
        )

        # expand frontier until all cells explored or shortest path found
        while frontier:
            # unpack tuple
            (
                current_f,
                current_g,
                current_position,
                _, # unpack tiebreaker but never use it
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
                    camefrom[(loc, n_map_bytes)] = (
                        current_position,
                        c_map_bytes
                    )
                    g_scores[(loc, n_map_bytes)] = current_g + 1
                    tiebreaker += 1
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

        # return empty path if no possible path to target
        if end_state == None:
            return deque()

        # creating path
        current_position = target
        c_map_bytes = end_state
        while (current_position, c_map_bytes) != (None, None):
            path.appendleft(current_position)
            (
                current_position, c_map_bytes
            ) = camefrom[(current_position, c_map_bytes)]
        # pop the start cell because we are already there
        path.popleft()
        return path

    def best_move(self, location: Point, map: RaceTrack) -> Point:
        """
        return optimal move
        
        :return: orthogonal unit vector from current cell to next cell
        :rtype: Point
        """
        # on first move
        if self.first_run:
            self.current_path = self.astar(
                location,
                map.target,
                map,
            )
            self.first_run = False

        if self.current_path:
            vector = self.getVector(location, self.current_path.popleft())
            if vector != (0, 0):
                return vector
            else:
                raise BotWontMoveError("next move is (0, 0)")
        else:
            raise BotWontMoveError("no path found for bot to follow")


class BotWontMoveError(Exception):
    """
    Exception raised when bot will not make a legal move
    """
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message