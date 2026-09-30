"""Command-line interface for the maze solver."""

import argparse
from pathlib import Path
import sys

from .astar import astar_search
from .maze import Maze, MazeFormatError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Solve a text maze using the A* algorithm.")
    parser.add_argument("maze", type=Path, help="Path to a maze text file")
    parser.add_argument("--show-explored", action="store_true", help="Mark explored cells with commas")
    parser.add_argument("--stats", action="store_true", help="Print search statistics")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        maze = Maze.from_file(args.maze)
    except (OSError, MazeFormatError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(2)

    result = astar_search(maze)
    print(maze.render(result.path, result.explored if args.show_explored else None))
    if result.found:
        print(f"\nPath found: {result.cost} moves")
    else:
        print("\nNo path found.")
    if args.stats:
        print(f"Cells explored: {len(result.explored)}")


if __name__ == "__main__":
    main()
