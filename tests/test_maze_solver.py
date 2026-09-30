import unittest

from maze_solver.astar import astar_search
from maze_solver.maze import Maze, MazeFormatError


class MazeSolverTests(unittest.TestCase):
    def test_finds_shortest_path(self):
        maze = Maze.from_text("""\
#######
#S...E#
#######
""")
        result = astar_search(maze)
        self.assertTrue(result.found)
        self.assertEqual(result.cost, 4)
        self.assertEqual(result.path[0], maze.start)
        self.assertEqual(result.path[-1], maze.goal)

    def test_routes_around_walls(self):
        maze = Maze.from_text("""\
#######
#S#..E#
#.#.#.#
#...#.#
#######
""")
        result = astar_search(maze)
        self.assertTrue(result.found)
        self.assertEqual(result.cost, 8)

    def test_reports_unreachable_goal(self):
        maze = Maze.from_text("""\
#####
#S#E#
#####
""")
        result = astar_search(maze)
        self.assertFalse(result.found)
        self.assertIsNone(result.cost)

    def test_rejects_invalid_maze(self):
        with self.assertRaises(MazeFormatError):
            Maze.from_text("S..\n..E#")

    def test_requires_one_start_and_goal(self):
        with self.assertRaises(MazeFormatError):
            Maze.from_text("S.E\n..E")


if __name__ == "__main__":
    unittest.main()
