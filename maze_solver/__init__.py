"""A command-line maze solver based on the A* search algorithm."""

from .astar import SearchResult, astar_search
from .maze import Maze, MazeFormatError, Position

__all__ = ["Maze", "MazeFormatError", "Position", "SearchResult", "astar_search"]
