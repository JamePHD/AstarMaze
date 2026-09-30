"""Command-line interface for the maze solver."""

import argparse
from pathlib import Path
import sys
import time

from .astar import astar_search, euclidean_distance, manhattan_distance, zero_heuristic
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


def solve_file(path: Path, show_explored: bool = False, stats: bool = False, debug: bool = False, mode: str = "manhattan") -> bool:
    try:
        maze = Maze.from_file(path)
    except (OSError, MazeFormatError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return False

    heuristic, heuristic_name = _heuristic_for(mode)
    start_time = time.perf_counter()
    result = astar_search(maze, heuristic)
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    print(maze.render(result.path, result.explored if show_explored else None))
    if result.found:
        print(f"\nPath found: {result.cost} moves")
    else:
        print("\nNo path found.")
    if stats:
        print(f"Cells explored: {len(result.explored)}")
        print(f"Frontier nodes processed: {result.frontier_nodes_processed}")
        print(f"Runtime: {elapsed_ms:.3f} ms")
        print(f"Heuristic: {heuristic_name}")
    if debug:
        print(f"Start: {maze.start}")
        print(f"Goal: {maze.goal}")
        print(f"Heuristic: {heuristic_name}")
        print(f"Search result: {'success' if result.found else 'failure'}")
    return True


def _heuristic_for(mode: str):
    return {
        "manhattan": (manhattan_distance, "Manhattan distance"),
        "euclidean": (euclidean_distance, "Euclidean distance"),
        "dijkstra": (zero_heuristic, "Zero heuristic (Dijkstra)"),
    }[mode]


def _choose_solver_mode() -> str | None:
    options = {
        "1": "manhattan",
        "2": "euclidean",
        "3": "dijkstra",
        "4": "compare",
    }
    print("\nChoose solving method:")
    print("1. Manhattan distance (default)")
    print("2. Euclidean distance")
    print("3. Zero heuristic / Dijkstra")
    print("4. Compare all three")
    choice = input("Select an option [1], or B to go back: ").strip().lower() or "1"
    if choice == "b":
        print("Returning to the main menu.")
        return None
    if choice in options:
        return options[choice]
    print("Invalid choice. Returning to the main menu.")
    return None


def compare_heuristics(path: Path, show_explored: bool = False, show_comparison: bool = True) -> None:
    try:
        maze = Maze.from_file(path)
    except (OSError, MazeFormatError) as error:
        print(f"Error: {error}")
        return
    print("\nHeuristic comparison")
    print(f"{'Method':<30} {'Path':>8} {'Explored':>10} {'Time (ms)':>12}")
    print("-" * 66)
    for mode in ("manhattan", "euclidean", "dijkstra"):
        heuristic, name = _heuristic_for(mode)
        start_time = time.perf_counter()
        result = astar_search(maze, heuristic)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        path_length = str(result.cost) if result.found else "none"
        print(f"{name:<30} {path_length:>8} {len(result.explored):>10} {elapsed_ms:>12.3f}")
        if show_comparison and result.found:
            explored = result.explored if show_explored else None
            print(f"\n{name} route:\n{maze.render(result.path, explored)}\n")


def _maze_files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.glob("*.txt") if path.is_file())


def interactive_menu(maze_directory: Path | None = None) -> None:
    maze_directory = maze_directory or Path("mazes")
    show_explored, show_stats, debug, show_comparison = True, True, False, True
    while True:
        print("\n================================")
        print("          A* MAZE SOLVER")
        print("================================")
        print("1. Solve a maze")
        print("2. Create a maze")
        print("3. View available mazes")
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
            mode = _choose_solver_mode()
            if mode is None:
                continue
            if mode == "compare":
                compare_heuristics(path, show_explored, show_comparison)
                input("\nPress Enter to return to the menu...")
                continue
            print(f"\nSolving {path.name}...\n")
            try:
                solve_file(path, show_explored, show_stats, debug, mode)
            finally:
                input("\nPress Enter to return to the menu...")
        elif choice == "2":
            create_maze(maze_directory)
        elif choice == "3":
            view_available_mazes(maze_directory)
        elif choice == "4":
            show_explored, show_stats, debug, show_comparison = settings_menu(
                show_explored, show_stats, debug, show_comparison
            )
        elif choice == "5":
            print("Goodbye!")
            return
        else:
            print("Please choose an option from 1 to 5.")


def create_maze(maze_directory: Path) -> None:
    """Interactively collect, validate, and save a user-created maze."""
    print("\nCreate a maze")
    print("Use # for walls, . for open cells, S for start, and E for goal.")
    print("New maze dimensions have a maximum of 100; larger mazes can be imported instead.")
    try:
        height_input = input("Enter maze height, or B to go back: ").strip().lower()
        if height_input == "b":
            return
        height = int(height_input)
        width_input = input("Enter maze width, or B to go back: ").strip().lower()
        if width_input == "b":
            return
        width = int(width_input)
    except ValueError:
        print("Height and width must be whole numbers.")
        return
    if height < 1 or width < 1:
        print("Height and width must be positive.")
        return
    if height > 100 or width > 100:
        print("Height and width cannot be greater than 100.")
        return

    rows = []
    for row_number in range(1, height + 1):
        row = input(f"Enter row {row_number}/{height} ({width} characters), or B to go back: ").strip()
        if row.lower() == "b":
            return
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

    filename = input("Enter a name for the maze (without .txt), or B to go back: ").strip()
    if filename.lower() == "b":
        return
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


def view_available_mazes(maze_directory: Path) -> None:
    """List saved mazes, then show details and a preview for one selection."""
    files = _maze_files(maze_directory)
    if not files:
        print("\nNo maze files found.")
        return

    print("\nAvailable mazes")
    print("-" * 24)
    for index, path in enumerate(files, start=1):
        print(f"{index}. {path.name}")

    selected = input("\nEnter a maze number to view, or B to go back: ").strip().lower()
    if not selected or selected == "b":
        return
    try:
        path = files[int(selected) - 1]
    except (ValueError, IndexError):
        print("Invalid maze selection.")
        return
    try:
        maze = Maze.from_file(path)
        result = astar_search(maze)
        walls = sum(row.count("#") for row in maze.rows)
        walkable = maze.height * maze.width - walls
        route = f"yes ({result.cost} moves)" if result.found else "no"
        print(f"\nMaze details: {path.name}")
        print(f"Dimensions: {maze.width} x {maze.height}")
        print(f"Walls: {walls}")
        print(f"Walkable cells: {walkable}")
        print(f"Start: {maze.start}    Goal: {maze.goal}")
        print(f"Solvable: {route}\n")
    except (OSError, MazeFormatError) as error:
        print(f"\nStatus: invalid maze ({error})\n")
    try:
        print(f"Preview: {path.name}\n")
        print(path.read_text(encoding="utf-8"))
    except OSError as error:
        print(f"Error reading maze: {error}")
    input("\nPress Enter to return to the menu...")


def _ask_yes_no(label: str, current: bool) -> bool:
    default = "Y/n" if current else "y/N"
    answer = input(f"{label}? [{default}]: ").strip().lower()
    return current if not answer else answer in {"y", "yes"}


def settings_menu(show_explored: bool, show_stats: bool, debug: bool, show_comparison: bool) -> tuple[bool, bool, bool, bool]:
    """Display and optionally update interactive solver settings."""
    while True:
        print("\nCurrent settings:")
        print(f"1. Show explored cells: {'ON' if show_explored else 'OFF'}")
        print(f"2. Show statistics: {'ON' if show_stats else 'OFF'}")
        print(f"3. Debug details: {'ON' if debug else 'OFF'}")
        print(f"4. Show comparison maze results: {'ON' if show_comparison else 'OFF'}")
        setting = input("Enter setting number to change, or B to go back: ").strip().lower()
        if setting == "b":
            return show_explored, show_stats, debug, show_comparison
        if setting not in {"1", "2", "3", "4"}:
            print("Invalid setting. Returning to the main menu.")
            return show_explored, show_stats, debug, show_comparison

        labels = {"1": "Show explored cells", "2": "Show statistics", "3": "Debug details", "4": "Show comparison maze results"}
        values = {"1": show_explored, "2": show_stats, "3": debug, "4": show_comparison}
        result = _ask_setting_value(labels[setting], values[setting])
        if result is None:
            return show_explored, show_stats, debug, show_comparison
        if setting == "1":
            show_explored = result
        elif setting == "2":
            show_stats = result
        else:
            debug = result
        if setting == "4":
            show_comparison = result
        print("Setting updated.")


def _ask_setting_value(label: str, current: bool) -> bool | None:
    default = "Y/n" if current else "y/N"
    answer = input(f"{label}? [{default}], or B to go back: ").strip().lower()
    if answer == "b":
        return None
    if not answer:
        return current
    if answer in {"y", "yes"}:
        return True
    if answer in {"n", "no"}:
        return False
    print("Invalid choice. Returning to the main menu.")
    return None


if __name__ == "__main__":
    main()
