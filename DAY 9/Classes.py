class Point:
    def move (self):
        print("Move this object!")
    def draw (self):
        print("Draw the Circle!")
    
point = Point()
point.x = 100
point.y = 200
point.draw()
point.move()
print(point.x)
print(point.y)

point1 = Point()
point1.x = 400
point1.y = 800
point1.draw()
point1.move()
print(point1.x)
print(point1.y)
