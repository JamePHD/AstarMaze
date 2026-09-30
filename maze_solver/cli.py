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
    if not solve_file(args.maze, args.show_explored, args.stats, args.debug):
        raise SystemExit(2)


def solve_file(path: Path, show_explored: bool = False, stats: bool = False, debug: bool = False) -> bool:
    try:
        maze = Maze.from_file(path)
    except (OSError, MazeFormatError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return False

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
    return True


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
        print("2. Create a maze")
        print("3. List available mazes")
        print("4. Settings")
        print("5. Exit")
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
            print(f"\nSelected maze: {path.name}\n")
            try:
                print(path.read_text(encoding="utf-8"))
            except OSError as error:
                print(f"Error reading maze: {error}")
                input("\nPress Enter to return to the menu...")
                continue
            if not _ask_yes_no("Solve this maze", True):
                print("Maze was not solved.")
                continue
            print(f"\nSolving {path.name}...\n")
            try:
                solve_file(path, show_explored, show_stats, debug)
            finally:
                input("\nPress Enter to return to the menu...")
        elif choice == "2":
            create_maze(maze_directory)
        elif choice == "3":
            files = _maze_files(maze_directory)
            print("\n" + ("\n".join(f"- {path.name}" for path in files) if files else "No maze files found."))
        elif choice == "4":
            show_explored = _ask_yes_no("Show explored cells", show_explored)
            show_stats = _ask_yes_no("Show statistics", show_stats)
            debug = _ask_yes_no("Enable debug details", debug)
        elif choice == "5":
            print("Goodbye!")
            return
        else:
            print("Please choose an option from 1 to 5.")


def create_maze(maze_directory: Path) -> None:
    """Interactively collect, validate, and save a user-created maze."""
    print("\nCreate a maze")
    print("Use # for walls, . for open cells, S for start, and E for goal.")
    try:
        height = int(input("Enter maze height: ").strip())
        width = int(input("Enter maze width: ").strip())
    except ValueError:
        print("Height and width must be whole numbers.")
        return
    if height < 1 or width < 1:
        print("Height and width must be positive.")
        return

    rows = []
    for row_number in range(1, height + 1):
        row = input(f"Enter row {row_number}/{height} ({width} characters): ").strip()
        if len(row) != width:
            print(f"Error: row {row_number} must contain exactly {width} characters.")
            return
        rows.append(row)

    try:
        maze = Maze.from_text("\n".join(rows))
    except MazeFormatError as error:
        print(f"Error: {error}")
        return

    result = astar_search(maze)
    if not result.found:
        print("Error: this maze has no route from S to E and was not saved.")
        return

    filename = input("Enter a name for the maze (without .txt): ").strip()
    if not filename or any(character in filename for character in '/\\:*?"<>|'):
        print("Error: please use a valid filename without path separators or special characters.")
        return
    output_path = maze_directory / f"{filename}.txt"
    if output_path.exists():
        if not _ask_yes_no("That file already exists. Overwrite it", False):
            print("Maze was not saved.")
            return
    maze_directory.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(maze.rows) + "\n", encoding="utf-8")
    print(f"Maze saved to {output_path}")
    print(f"It contains a solvable route of {result.cost} moves.")


def _ask_yes_no(label: str, current: bool) -> bool:
    default = "Y/n" if current else "y/N"
    answer = input(f"{label}? [{default}]: ").strip().lower()
    return current if not answer else answer in {"y", "yes"}


if __name__ == "__main__":
    main()
