#!/usr/bin/env python
import sys
import argparse
import random
from PIL import Image

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
        self.visited.append((0,0))
        self.visited_count = width * height
        self.add_dir(self.visited[-1], MazeGen.VISITED)

    def __str__(self):
        str = "Width: {}\nHeight: {}\n".format(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                str += "{:02x} ".format(self.get((x,y)))
            str += "\n"
        return str

    def get(self, coords):
        return self.maze[coords[1] * self.width + coords[0]]

    def add_dir(self, coords, dir):
        self.maze[coords[1] * self.width + coords[0]] |= dir

    def get_free_exits(self, coords):
        tmp_exits = []
        state = self.get(coords)

        if state & MazeGen.NORTH is 0 and coords[1] > 0:
            tmp_exits.append((MazeGen.NORTH, MazeGen.SOUTH, 0, -1))
        if state & MazeGen.SOUTH is 0 and coords[1] < (self.height - 1):
            tmp_exits.append((MazeGen.SOUTH, MazeGen.NORTH, 0, 1))
        if state & MazeGen.WEST is 0 and coords[0] > 0:
            tmp_exits.append((MazeGen.WEST, MazeGen.EAST, -1, 0))
        if state & MazeGen.EAST is 0 and coords[0] < (self.width - 1):
            tmp_exits.append((MazeGen.EAST, MazeGen.WEST, 1, 0))

        exits = []
        for exit in tmp_exits:
            if self.get((coords[0] + exit[2], coords[1] + exit[3])) & MazeGen.VISITED is 0:
                exits.append(exit)

        return exits

    def generate(self):
        while self.visited and self.visited_count > 0:
            curr_coords = self.visited[-1]
            exits = self.get_free_exits(curr_coords)
            if exits:
                choice = random.choice(exits)
                self.add_dir(curr_coords, choice[0])

                choice_coords = (curr_coords[0] + choice[2], curr_coords[1] + choice[3])
                self.visited.append(choice_coords)
                self.add_dir(self.visited[-1], choice[1])
                if self.get(choice_coords) & MazeGen.VISITED is 0:
                    self.add_dir(choice_coords, MazeGen.VISITED)
                    self.visited_count -= 1
            else:
                self.visited.pop()

    def render(self, cell_width, cell_height):
        image = Image.new('RGB', (self.width * 2, self.height *2), (0,0,0))
        for y in range(self.height):
            for x in range(self.width):
                coords = (x,y)
                state = self.get(coords)
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
        print("Failed with error:\n{}".format(e))

if __name__ == "__main__":
    main()
