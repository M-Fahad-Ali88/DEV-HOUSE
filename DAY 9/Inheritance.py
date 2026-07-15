class animal:

    def __init__(self,name):
        self.name = name

    def walk(self):
        print(f"{self.name} is wallking")

class Dog(animal):
    def bark(self):
        print("Dog is barking")
dog1 = Dog("Dog")
dog1.bark()
dog1.walk()

class Cat(animal):
    def meow(self):
        print("Cat is Mewoing")
cat1 = Cat("Cat")
cat1.meow()
cat1.walk()