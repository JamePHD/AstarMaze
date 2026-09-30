"""Maze representation and text-file parsing."""

from dataclasses import dataclass
from pathlib import Path

Position = tuple[int, int]


class MazeFormatError(ValueError):
    """Raised when a maze file does not follow the expected format."""


@dataclass(frozen=True)
class Maze:
    """A rectangular grid maze.

    ``#`` represents a wall, ``.`` an open cell, ``S`` the start, and ``E``
    the goal.  Coordinates are represented as ``(row, column)`` pairs.
    """

    rows: tuple[str, ...]
    start: Position
    goal: Position

    @classmethod
    def from_text(cls, text: str) -> "Maze":
        rows = tuple(line.rstrip("\r") for line in text.splitlines())
        if not rows or any(not row for row in rows):
            raise MazeFormatError("The maze must contain only non-empty rows.")
        width = len(rows[0])
        if any(len(row) != width for row in rows):
            raise MazeFormatError("The maze must be rectangular.")

        allowed = {"#", ".", "S", "E"}
        invalid = sorted({cell for row in rows for cell in row if cell not in allowed})
        if invalid:
            raise MazeFormatError(f"Unsupported maze character(s): {', '.join(invalid)}")

        starts = [(r, c) for r, row in enumerate(rows) for c, cell in enumerate(row) if cell == "S"]
        goals = [(r, c) for r, row in enumerate(rows) for c, cell in enumerate(row) if cell == "E"]
        if len(starts) != 1 or len(goals) != 1:
            raise MazeFormatError("The maze must contain exactly one S and exactly one E.")
        return cls(rows=rows, start=starts[0], goal=goals[0])

    @classmethod
    def from_file(cls, path: str | Path) -> "Maze":
        return cls.from_text(Path(path).read_text(encoding="utf-8"))

    @property
    def height(self) -> int:
        return len(self.rows)

    @property
    def width(self) -> int:
        return len(self.rows[0])

    def is_open(self, position: Position) -> bool:
        row, column = position
        return (
            0 <= row < self.height
            and 0 <= column < self.width
            and self.rows[row][column] != "#"
        )

    def neighbours(self, position: Position) -> list[Position]:
        row, column = position
        candidates = (
            (row - 1, column),
            (row + 1, column),
            (row, column - 1),
            (row, column + 1),
        )
        return [candidate for candidate in candidates if self.is_open(candidate)]

    def render(self, path: list[Position] | None = None, explored: set[Position] | None = None) -> str:
        """Return a display version of the maze.

        Internally, ``.`` continues to represent a walkable cell.  For
        readability, unexplored walkable cells are rendered as whitespace.
        """
        output = [list(row) for row in self.rows]
        if explored:
            for row, column in explored:
                if output[row][column] == ".":
                    output[row][column] = ","
        if path:
            for row, column in path:
                if output[row][column] in {".", ","}:
                    output[row][column] = "o"
        for row in output:
            for column, cell in enumerate(row):
                if cell == ".":
                    row[column] = " "
        return "\n".join("".join(row) for row in output)
