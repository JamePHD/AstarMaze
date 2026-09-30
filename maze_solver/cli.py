"""Command-line interface for the maze solver."""

import argparse
from pathlib import Path
import sys

from .astar import astar_search
from .maze import Maze, MazeFormatError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Solve a text maze using the A* algorithm.")
    parser.add_argument("maze", type=Path, nargs="?", help="Path to a maze text file")
    parser.add_argument("--show-explored", action="store_true", help="Mark explored cells with commas")
    parser.add_argument("--stats", action="store_true", help="Print search statistics")
    parser.add_argument("--debug", action="store_true", help="Print extra search details")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.maze is None:
        interactive_menu()
        return
    solve_file(args.maze, args.show_explored, args.stats, args.debug)


def solve_file(path: Path, show_explored: bool = False, stats: bool = False, debug: bool = False) -> None:
    try:
        maze = Maze.from_file(path)
    except (OSError, MazeFormatError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(2)

    result = astar_search(maze)
    print(maze.render(result.path, result.explored if show_explored else None))
    if result.found:
        print(f"\nPath found: {result.cost} moves")
    else:
        print("\nNo path found.")
    if stats:
        print(f"Cells explored: {len(result.explored)}")
    if debug:
        print(f"Start: {maze.start}")
        print(f"Goal: {maze.goal}")
        print("Heuristic: Manhattan distance")
        print(f"Search result: {'success' if result.found else 'failure'}")


def _maze_files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.glob("*.txt") if path.is_file())


def interactive_menu(maze_directory: Path | None = None) -> None:
    maze_directory = maze_directory or Path("mazes")
    show_explored, show_stats, debug = False, True, False
    while True:
        print("\n================================")
        print("          A* MAZE SOLVER")
        print("================================")
        print("1. Solve a maze")
        print("2. List available mazes")
        print("3. Settings")
        print("4. Exit")
        choice = input("\nSelect an option: ").strip()
        if choice == "1":
            files = _maze_files(maze_directory)
            if not files:
                print(f"No .txt maze files found in {maze_directory.resolve()}")
                continue
            print("\nAvailable mazes:")
            for index, path in enumerate(files, start=1):
                print(f"{index}. {path.name}")
            selected = input("Choose a maze (or B to go back): ").strip().lower()
            if selected == "b":
                continue
            try:
                path = files[int(selected) - 1]
            except (ValueError, IndexError):
                print("Invalid maze selection.")
                continue
            print(f"\nSolving {path.name}...\n")
            solve_file(path, show_explored, show_stats, debug)
            input("\nPress Enter to return to the menu...")
        elif choice == "2":
            files = _maze_files(maze_directory)
            print("\n" + ("\n".join(f"- {path.name}" for path in files) if files else "No maze files found."))
        elif choice == "3":
            show_explored = _ask_yes_no("Show explored cells", show_explored)
            show_stats = _ask_yes_no("Show statistics", show_stats)
            debug = _ask_yes_no("Enable debug details", debug)
        elif choice == "4":
            print("Goodbye!")
            return
        else:
            print("Please choose an option from 1 to 4.")


def _ask_yes_no(label: str, current: bool) -> bool:
    default = "Y/n" if current else "y/N"
    answer = input(f"{label}? [{default}]: ").strip().lower()
    return current if not answer else answer in {"y", "yes"}


if __name__ == "__main__":
    main()
