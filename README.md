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

From the repository root:

```bash
python -m maze_solver mazes/example.txt
```

Useful options:

```bash
python -m maze_solver mazes/example.txt --show-explored --stats
```

The solver prints `*` for the final route, and optionally `,` for cells explored while searching.

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

## Suggested extensions for the assignment

- Add a `--heuristic` option and compare A* with Dijkstra's algorithm.
- Add generated mazes and measure path length, explored cells, and runtime.
- Support weighted terrain such as water or mud.
- Add a step-by-step mode for the video walkthrough.
- Explain the frontier, `g` scores, `came_from`, and heuristic in the report.
