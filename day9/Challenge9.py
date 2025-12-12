from pathlib import Path
from itertools import combinations
import numpy as np
import sys
import time

input_file = Path(".") / "input.txt"

def print_matrix(matrix: list, title: str="Matrix"):
    if title:
        print(title.title())
    print(np.array(matrix), "\n")

def calculate_area(x1, y1, x2, y2: int) -> int:
    a = abs(x1-x2) + 1
    b = abs(y1-y2) + 1
    return a * b

# given a list of points (2D coordinates), find the greatest area of a rectangle
# were opposite corners are two point from the list
def find_greatest_area(points: list) -> int:
    max_area = 0
    for point1, point2 in list(combinations(points, 2)):
        x1, y1 = point1
        x2, y2 = point2
        area = calculate_area(x1, y1, x2, y2)
        if area > max_area:
            max_area = area
    return max_area

# given a list of points, find the greatest area of a rectangle
# were opposite corners are two point from the list
# if any diagonal of such rectangle crosses an excluded coordinate, then ignore that solution
def find_greatest_area_avoiding_exclusions(points: list, exclusions: QuadTree) -> int:
    '''
    Args:
        points (list): list of 2D coordinates represented by a list of 2 integers
        exclusions (QuadTree): key is a 2D point represented by tuple of 2 integers, the value is a boolean, where True means that point is excluded to be covered
    
    Returns:
        int: the greatest area of a rectangle which includes points allowed by the exclusion_map argument
    '''
    max_area = 0
    for point1, point2 in list(combinations(points, 2)):
        x1, y1 = point1
        x2, y2 = point2
        diagonal1 = (x1, y1, x2, y2)
        diagonal2 = (x1, y2, x2, y1)
        allowed = True

        def gen_coordinates_to_check():
            yield from enumerate_line_coordinates(*diagonal1)
            yield from enumerate_line_coordinates(*diagonal2)
        
        for x, y in gen_coordinates_to_check():
            if exclusions.search(Point(x, y)) == None:
                allowed = False
                break

        if not allowed:
            continue
        
        area = calculate_area(x1, y1, x2, y2)
        if area > max_area:
            max_area = area

    return max_area

def generate_inclusions(red_points: list) -> QuadTree:
    '''Build a 2D map of allowed and excluded points
    Args:
        points (list): list of 2D coordinates represented by a list of 2 integers
    
    Returns:
        QuadTree: points which can be included inside a rectangle
    '''
    RED_TILE = 1
    GREEN_TILE = 2
    LIGHT_GREEN_TILE = 3
    
    # find out the dimensions of the map
    max_x, max_y = 0, 0
    min_x, min_y = sys.maxsize, sys.maxsize
    for x, y in red_points:
        if x > max_x:
            max_x = x
        if y > max_y:
            max_y = y
        if x < min_x:
            min_x = x
        if y < min_y:
            min_y = y
    tile_map = QuadTree(Point(min_x, min_y), Point(max_x, max_y))

    print(f"adding red tiles ({len(red_points)})...")
    # mark input points as red
    for x, y in red_points:
        tile_map.insert(Node(Point(x, y), RED_TILE))
    print("done")

    # mark lines between red tiles as green
    green_points = []
    print("adding green horizontal tiles...")
    start = time.time()
    green_points += fill_horizontal_line(tile_map, GREEN_TILE, red_points)
    print(f"done in {time.time()-start}sec")

    print("adding green vertical tiles...")
    start = time.time()
    green_points += fill_vertical_line(tile_map, GREEN_TILE, red_points)
    print(f"done in {time.time()-start}sec")
    
    # mark lines between green tiles as light green
    print(f"adding light green horizontal tiles ({len(green_points)})...")
    fill_horizontal_line(tile_map, LIGHT_GREEN_TILE, green_points)    
    print("done")

    print("adding light green vertical tiles...")
    fill_vertical_line(tile_map, LIGHT_GREEN_TILE, green_points)
    print("done")
    
    #print(f"all points added: {tile_map}")

    return tile_map

def fill_vertical_line(tile_map: QuadTree, fill_color: int, points: list) -> list:
    X_INDEX = 0
    Y_INDEX = 1
    filled_points = []
    sorted_points = sorted(points, key=lambda point: point[Y_INDEX])
    previous = sorted_points[0]
    for point in sorted_points[1:]:
        if previous[Y_INDEX] == point[Y_INDEX]:
            start = min(previous[X_INDEX], point[X_INDEX]) + 1
            end = max(previous[X_INDEX], point[X_INDEX])
            for x in range(start, end):
                tile_map.insert(Node(Point(x, point[Y_INDEX]), fill_color))
                if fill_color != 3:
                    filled_points.append([x, point[Y_INDEX]])
        previous = point

    #fill_row(tile_map, filled_points, fill_color)
    return filled_points

def fill_horizontal_line(tile_map: list, fill_color: int, points: list) -> list:
    X_INDEX = 0
    Y_INDEX = 1
    filled_points = []
    s = time.time()
    sorted_points = sorted(points, key=lambda point: point[X_INDEX])
    print(f"points sorted after {time.time()-s}sec")
    
    s = time.time()
    previous = sorted_points[0]
    for point in sorted_points[1:]:
        if previous[X_INDEX] == point[X_INDEX]:
            start = min(previous[Y_INDEX], point[Y_INDEX]) + 1
            end = max(previous[Y_INDEX], point[Y_INDEX])
            for y in range(start, end):
                tile_map.insert(Node(Point(point[X_INDEX], y), fill_color))
                if fill_color != 3:
                    filled_points.append([point[X_INDEX], y])
        previous = point

    print(f"new points generated after {time.time()-s}sec")

    s = time.time()
    #fill_row(tile_map, filled_points, fill_color)
    print(f"points added to map after {time.time()-s}sec")
    return filled_points

def fill_row(tile_map: QuadTree, points: list, color: int) -> None:
    X_INDEX = 0
    Y_INDEX = 1
    for point in points:
        tile_map.insert(Node(Point(point[X_INDEX], point[Y_INDEX]), color))

# compute the approximate coordinates of a straight line between coordinates (x1,y1) and (x2,y2)
def enumerate_line_coordinates(x1, y1, x2, y2: int) -> tuple:
    if x1 == x2 and y1 == y2:
        raise ValueError(f"Two distinct points required, but one given")

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    sx = 1 if x1 < x2 else -1 # step in x direction
    sy = 1 if y1 < y2 else -1 # step in y direction

    error = dx - dy
    x, y = x1, y1

    while True:
        current_error = error * 2
        if current_error > -dy:
            error -= dy
            x += sx
        if current_error < dx:
            error += dx
            y += sy
        if x == x2 and y == y2:
            break
        yield (x, y)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self) -> str:
        return f"Point({self.x},{self.y})"
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Node:
    def __init__(self, pos, data):
        self.pos = pos
        self.data = data
    def __repr__(self) -> str:
        return f"Node({self.pos}, data={self.data})"

class QuadTree:
    def __init__(self, topL, botR):
        self.topLeft = topL
        self.botRight = botR
        self.n = None
        self.topLeftTree = None
        self.topRightTree = None
        self.botLeftTree = None
        self.botRightTree = None

    def __repr__(self) -> str:
        return f"QuadTree(area=({self.topLeft},{self.botRight}) totalPointsCount={self._totalPointsCount()})"

    def _totalPointsCount(self) -> int:
        count = 0 if self.n == None else 1
        count += self.topLeftTree._totalPointsCount() if self.topLeftTree != None else 0
        count += self.topRightTree._totalPointsCount() if self.topRightTree != None else 0
        count += self.botLeftTree._totalPointsCount() if self.botLeftTree != None else 0
        count += self.botRightTree._totalPointsCount() if self.botRightTree != None else 0
        return count

    # Insert a node into the quadtree
    def insert(self, node):
        if node is None:
            return

        # Current quad cannot contain it
        if not self.inBoundary(node.pos):
            return

        # We are at a quad of unit area
        # We cannot subdivide this quad further
        if abs(self.topLeft.x - self.botRight.x) <= 1 and abs(self.topLeft.y - self.botRight.y) <= 1:
            if self.n is None or self.n.pos == node.pos:
                self.n = node
            return

        if (self.topLeft.x + self.botRight.x) / 2 >= node.pos.x:
            # Indicates topLeftTree
            if (self.topLeft.y + self.botRight.y) / 2 >= node.pos.y:
                if self.topLeftTree is None:
                    self.topLeftTree = QuadTree(self.topLeft, Point((self.topLeft.x + self.botRight.x) / 2, (self.topLeft.y + self.botRight.y) / 2))
                self.topLeftTree.insert(node)
            # Indicates botLeftTree
            else:
                if self.botLeftTree is None:
                    self.botLeftTree = QuadTree(Point(self.topLeft.x, (self.topLeft.y + self.botRight.y) / 2), Point((self.topLeft.x + self.botRight.x) / 2, self.botRight.y))
                self.botLeftTree.insert(node)
        else:
            # Indicates topRightTree
            if (self.topLeft.y + self.botRight.y) / 2 >= node.pos.y:
                if self.topRightTree is None:
                    self.topRightTree = QuadTree(Point((self.topLeft.x + self.botRight.x) / 2, self.topLeft.y), Point(self.botRight.x, (self.topLeft.y + self.botRight.y) / 2))
                self.topRightTree.insert(node)
            # Indicates botRightTree
            else:
                if self.botRightTree is None:
                    self.botRightTree = QuadTree(Point((self.topLeft.x + self.botRight.x) / 2, (self.topLeft.y + self.botRight.y) / 2), self.botRight)
                self.botRightTree.insert(node)

    # Find a node in a quadtree
    def search(self, p):
        # Current quad cannot contain it
        if not self.inBoundary(p):
            return None  # Return None if point is not found

        # We are at a quad of unit length
        # We cannot subdivide this quad further
        if self.n is not None:
            return self.n

        if (self.topLeft.x + self.botRight.x) / 2 >= p.x:
            # Indicates topLeftTree
            if (self.topLeft.y + self.botRight.y) / 2 >= p.y:
                if self.topLeftTree is None:
                    return None
                return self.topLeftTree.search(p)
            # Indicates botLeftTree
            else:
                if self.botLeftTree is None:
                    return None
                return self.botLeftTree.search(p)
        else:
            # Indicates topRightTree
            if (self.topLeft.y + self.botRight.y) / 2 >= p.y:
                if self.topRightTree is None:
                    return None
                return self.topRightTree.search(p)
            # Indicates botRightTree
            else:
                if self.botRightTree is None:
                    return None
                return self.botRightTree.search(p)

    # Check if current quadtree contains the point
    def inBoundary(self, p):
        return p.x >= self.topLeft.x and p.x <= self.botRight.x and p.y >= self.topLeft.y and p.y <= self.botRight.y

points = []
with input_file.open(mode="r", encoding="utf-8") as file:
    for line in file:
        points.append(list(map(int, reversed(line.strip().split(",")) )))

print(f"Part1 answer: {find_greatest_area(points)}")
print(f"Part2 answer: {find_greatest_area_avoiding_exclusions(points, generate_inclusions(points))}")

