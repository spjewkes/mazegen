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

    def render_rect(self, image, x, y, width, height, colour):
        for off_y in range(height):
            for off_x in range(width):
                image.putpixel((x + off_x, y + off_y), colour)

    def render(self, cell_width, cell_height, wall_width, wall_height):
        wall_col = (255, 255, 255)
        cell_col = (0, 0, 0)
        total_width = cell_width + wall_width
        total_height = cell_height + wall_height

        image = Image.new('RGB', (self.width * total_width + wall_width,
                                  self.height * total_height + wall_height), cell_col)
        for cy in range(self.height):
            for cx in range(self.width):
                x = cx * total_width + wall_width
                y = cy * total_height + wall_height

                if cy is 0 and cx is 0:
                    self.render_rect(image, 0, 0, wall_width, wall_height, wall_col)
                if cy is 0:
                    self.render_rect(image, x, 0, total_width, wall_height, wall_col)
                if cx is 0:
                    self.render_rect(image, 0, y, wall_width, total_height, wall_col)

                self.render_rect(image, x, y, cell_width, cell_height, cell_col)
                    
                state = self.get(Coord(cx, cy))
                if state & MazeGen.EAST is 0:
                    self.render_rect(image, x + cell_width, y, wall_width, cell_height, wall_col)
                else:
                    self.render_rect(image, x + cell_width, y, wall_width, cell_height, cell_col)

                if state & MazeGen.SOUTH is 0:
                    self.render_rect(image, x, y + cell_height, cell_width, wall_height, wall_col)
                else:
                    self.render_rect(image, x, y + cell_height, cell_width, wall_height, cell_col)
                
                self.render_rect(image, x + cell_width, y + cell_height, wall_width, wall_height, wall_col)
        image.save("maze.png", "PNG")

def main():
    parser = argparse.ArgumentParser(description="Generates random mazes as PNG images.")

    parser.add_argument('--width', help="Width of maze", dest='width', type=int, default=100)
    parser.add_argument('--height', help="Height of maze", dest='height', type=int, default=75)
    parser.add_argument('--cellw', help="Width of each maze cell", dest='cellw', type=int, default=1)
    parser.add_argument('--cellh', help="Height of each maze cell", dest='cellh', type=int, default=1)
    parser.add_argument('--wallw', help="Width of each maze cell wall", dest='wallw', type=int, default=1)
    parser.add_argument('--wallh', help="Height of each maze cell wall", dest='wallh', type=int, default=1)
    parser.add_argument('--verbose', help="Enable verbose output whilst generating the maze", action='store_true')
    args = parser.parse_args()

    try:
        if args.cellw < 1:
            raise Exception("Cell width must be greater than 0")
        if args.cellh < 1:
            raise Exception("Cell height must be greater than 0")

        if args.wallw < 1:
            raise Exception("Cell wall width must be greater than 0")
        if args.wallh < 1:
            raise Exception("Cell wall height must be greater than 0")

        maze = MazeGen(args.width, args.height)
        maze.generate()
        if args.verbose:
            print(maze)
        maze.render(args.cellw, args.cellh, args.wallw, args.wallh)

    except Exception as e:
        if args.verbose:
            traceback.print_exc()
        print("Failed with error:\n{}".format(e))

if __name__ == "__main__":
    main()
