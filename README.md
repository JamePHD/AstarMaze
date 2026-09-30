# A* Maze Solver

A command-line maze solver using the A* pathfinding algorithm. This is the foundation for Programming Assignment 1, Track B.

## Requirements

- Python 3.10 or newer

No external packages are required.

## Maze format

Maze files are rectangular text grids using:

- `#` for a wall
- `.` for an open cell
- `S` for the start
- `E` for the goal

Each maze must contain exactly one `S` and one `E`.

## Run it

Start the interactive menu:

```bash
python -m maze_solver
```

The menu lets you choose a maze, list available maze files, and change display,
statistics, and debugging settings.

It also includes a maze creator and a maze browser. The creator accepts both
square and rectangular dimensions, validates the rows and required maze symbols,
checks that `S` can reach `E`, and saves valid mazes in the `mazes` folder. The
browser displays dimensions, wall and walkable-cell counts, route information,
and a text preview.

The maze creator accepts dimensions from 1 to 100 in each direction. This limit
applies only to newly created mazes; larger rectangular maze files can still be
imported and solved.

When solving interactively, the user can choose Manhattan distance, Euclidean
distance, zero heuristic (Dijkstra's algorithm), or compare all three. The
comparison reports path length, explored cells, and runtime.

For scripted use, provide a maze path directly:

From the repository root:

```bash
python -m maze_solver mazes/example.txt
```

Useful options:

```bash
python -m maze_solver mazes/example.txt --show-explored --stats
```

Add `--debug` to display the start and goal coordinates, heuristic, and search result.

The solver prints `o` for the final route, and optionally `,` for cells explored while searching.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Algorithm summary

Each open cell is a graph vertex, and edges connect horizontally or vertically adjacent cells. Every move costs one. A* prioritises a cell using:

```text
f(n) = g(n) + h(n)
```

where `g(n)` is the cost from the start and `h(n)` is Manhattan distance to the goal. Manhattan distance is admissible for this maze because diagonal movement is forbidden and every move costs one, so A* returns a shortest path when one exists.
