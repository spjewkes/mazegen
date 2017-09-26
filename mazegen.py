#!/usr/bin/env python
import sys
import argparse
import random

class MazeGen:
    VISITED = 0x1
    NORTH = 0x2
    SOUTH = 0x4
    EAST = 0x8
    WEST = 0x10

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [0] * (width * height)

        self.visited = []
        self.visited.append((0,0))
        self.set(self.visited[-1], MazeGen.VISITED)

    def __str__(self):
        str = "Width: {}\nHeight: {}\n".format(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                str += "{:02x} ".format(self.get((x,y)))
            str += "\n"
        return str

    def get(self, coords):
        return self.maze[coords[1] * self.width + coords[0]]

    def set(self, coords, val):
        self.maze[coords[1] * self.width + coords[0]] = val

    def is_visited(self, coords):
        return (self.get(coords) & MazeGen.VISITED) != 0

    def generate(self):
        None

    def render(self, cell_width, cell_height):
        None
    
def main():
    parser = argparse.ArgumentParser(description="Generates random mazes as PNG images.")

    parser.add_argument('--width', help="Width of maze", dest='width', type=int, default=100)
    parser.add_argument('--height', help="Height of maze", dest='height', type=int, default=75)
    parser.add_argument('--cellw', help="Width of each maze cell", dest='cellw', type=int, default=8)
    parser.add_argument('--cellh', help="Height of each maze cell", dest='cellh', type=int, default=8)
    parser.add_argument('--verbose', help="Enable verbose output whilst generating the maze", action='store_true')
    args = parser.parse_args()

    try:
        if args.cellw < 2:
            raise Exception("Cell width must be greater than 1")
        if args.cellh < 2:
            raise Exception("Cell height must be greater than 1")

        maze = MazeGen(args.width, args.height)
        print(maze)

    except Exception as e:
        print("Failed with error:\n{}".format(e))

if __name__ == "__main__":
    main()
