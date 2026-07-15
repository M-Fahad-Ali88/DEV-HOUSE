class point:
    def __init__(self,x,y):
        self.x=x
        self.y=y

    def move (self):
        print("Move this object!")
    def draw (self):
        print("Draw the Circle!")

#x and y axis
point1 = point(10,100)
point1.move()
print(point1.x)
print(point1.y)


#exercise
class Person:
    def __init__(self,name):
        self.name = name
    
    def talk(self):
        print("is talking")

#exercise 2
person = Person("Fahad")
print(person.name,end=" ") 
person.talk()

class Person:
    def __init__(self,name):
        self.name = name
    
    def talk(self):
        print(f"Hi, I am {self.name}!")

person = Person("Fahad")
person.talk()

person1 = Person("Anas")
person1.talk()
 
 