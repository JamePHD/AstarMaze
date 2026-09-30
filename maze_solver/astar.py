"""A* search for four-directional grid mazes."""

from dataclasses import dataclass
import heapq
from itertools import count
import math
from collections.abc import Callable

from .maze import Maze, Position


@dataclass(frozen=True)
class SearchResult:
    """The outcome and useful statistics from one A* search."""

    path: list[Position] | None
    explored: set[Position]
    cost: int | None

    @property
    def found(self) -> bool:
        return self.path is not None


def manhattan_distance(first: Position, second: Position) -> int:
    return abs(first[0] - second[0]) + abs(first[1] - second[1])


def euclidean_distance(first: Position, second: Position) -> float:
    return math.hypot(first[0] - second[0], first[1] - second[1])


def zero_heuristic(first: Position, second: Position) -> int:
    return 0


def _reconstruct_path(came_from: dict[Position, Position], current: Position) -> list[Position]:
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def astar_search(maze: Maze, heuristic: Callable[[Position, Position], float] = manhattan_distance) -> SearchResult:
    """Find a shortest route from ``maze.start`` to ``maze.goal``.

    Every move costs one.  Manhattan distance is admissible here because
    movement is limited to horizontal and vertical steps with no diagonal moves.
    """
    start, goal = maze.start, maze.goal
    frontier: list[tuple[int, int, Position]] = []
    tie_breaker = count()
    heapq.heappush(frontier, (heuristic(start, goal), next(tie_breaker), start))

    came_from: dict[Position, Position] = {}
    cost_so_far = {start: 0}
    explored: set[Position] = set()

    while frontier:
        _, _, current = heapq.heappop(frontier)
        if current in explored:
            continue
        explored.add(current)

        if current == goal:
            path = _reconstruct_path(came_from, current)
            return SearchResult(path=path, explored=explored, cost=len(path) - 1)

        for neighbour in maze.neighbours(current):
            new_cost = cost_so_far[current] + 1
            if new_cost < cost_so_far.get(neighbour, float("inf")):
                cost_so_far[neighbour] = new_cost
                came_from[neighbour] = current
                priority = new_cost + heuristic(neighbour, goal)
                heapq.heappush(frontier, (priority, next(tie_breaker), neighbour))

    return SearchResult(path=None, explored=explored, cost=None)
