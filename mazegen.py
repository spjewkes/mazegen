#!/usr/bin/env python
import sys
import argparse
import random
import traceback
from PIL import Image

class Coord:
    def __init__(self, x=0, y=0):
        self.coord = (x, y)

    def __str__(self):
        return "(x={}, y={})".format(self.coord[0], self.coord[1])

    def __add__(self, other):
        if isinstance(other, tuple) and len(other) is 2:
            return Coord(self.coord[0] + other[0], self.coord[1] + other[1])
        elif isinstance(other, Coord):
            return self.__add__(other.coord)
        else:
            raise ValueError("A list of length 2 is required")

    def __radd__(self, other):
        return self.__add__(other)

    def x(self):
        return self.coord[0]

    def y(self):
        return self.coord[1]

    def conv_1d(self, width):
        return self.y() * width + self.x()

class MazeGen:
    NORTH = 0x1
    SOUTH = 0x2
    EAST = 0x4
    WEST = 0x8
    VISITED = 0x10

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [0] * (width * height)

        self.visited = []
        self.visited.append(Coord(0,0))
        self.visited_count = width * height
        self.update_state(self.visited[-1], MazeGen.VISITED)

    def __str__(self):
        str = "Width: {}\nHeight: {}\n".format(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                str += "{:02x} ".format(self.get(Coord(x,y)))
            str += "\n"
        return str

    def get(self, coord):
        return self.maze[coord.conv_1d(self.width)]

    def update_state(self, coord, state):
        self.maze[coord.conv_1d(self.width)] |= state

    def get_free_exits(self, coord):
        tmp_exits = []
        state = self.get(coord)

        if state & MazeGen.NORTH is 0 and coord.y() > 0:
            tmp_exits.append((MazeGen.NORTH, MazeGen.SOUTH, Coord(0, -1)))
        if state & MazeGen.SOUTH is 0 and coord.y() < (self.height - 1):
            tmp_exits.append((MazeGen.SOUTH, MazeGen.NORTH, Coord(0, 1)))
        if state & MazeGen.WEST is 0 and coord.x() > 0:
            tmp_exits.append((MazeGen.WEST, MazeGen.EAST, Coord(-1, 0)))
        if state & MazeGen.EAST is 0 and coord.x() < (self.width - 1):
            tmp_exits.append((MazeGen.EAST, MazeGen.WEST, Coord(1, 0)))

        exits = []
        for exit in tmp_exits:
            if self.get(coord + exit[2]) & MazeGen.VISITED is 0:
                exits.append(exit)

        return exits

    def generate(self):
        # Build maze whilst there are still unvisited cells
        while self.visited and self.visited_count > 0:
            # Get available exits from the currently visited cell
            curr_coord = self.visited[-1]
            exits = self.get_free_exits(curr_coord)
            if exits:
                # If there are still untried exits then randomly choose one and
                # add it to top of currently visited cells
                choice = random.choice(exits)
                self.update_state(curr_coord, choice[0])

                choice_coord = curr_coord + choice[2]
                self.visited.append(choice_coord)
                self.update_state(self.visited[-1], choice[1])

                if self.get(choice_coord) & MazeGen.VISITED is 0:
                    # If this new cell has not been visited before then
                    # mark it as such
                    self.update_state(choice_coord, MazeGen.VISITED)
                    self.visited_count -= 1
            else:
                # No available exits, so don't visit this cell in future
                self.visited.pop()

    def render(self, cell_width, cell_height):
        image = Image.new('RGB', (self.width * 2, self.height *2), (0,0,0))
        for y in range(self.height):
            for x in range(self.width):
                state = self.get(Coord(x, y))
                if state & MazeGen.EAST is 0:
                    image.putpixel(((x*2) + 1, y*2), (255, 255, 255))
                if state & MazeGen.SOUTH is 0:
                    image.putpixel((x*2, (y*2) + 1), (255, 255, 255))
                image.putpixel(((x*2)+1, (y*2)+1), (255, 255, 255))
        image.save("maze.png", "PNG")

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
        maze.generate()
        if args.verbose:
            print(maze)
        maze.render(args.cellw, args.cellh)

    except Exception as e:
        if args.verbose:
            traceback.print_exc()
        print("Failed with error:\n{}".format(e))

if __name__ == "__main__":
    main()
