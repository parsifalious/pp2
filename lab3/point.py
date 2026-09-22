import math

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    def show(self):
        print(f"({self.x}, {self.y})")
    def move(self, x, y):
        self.x = x
        self.y = y
    def dist(self, other_point):
        distance = math.sqrt((self.x - other_point.x)**2 + (self.y - other_point.y)**2)
        print(distance)

p1 = Point(1, 2)
p2 = Point(4, 6)
p1.show()
p1.move(3, 3)
p1.show()
p1.dist(p2)