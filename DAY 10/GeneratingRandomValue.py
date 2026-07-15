import random
print(random.random())

#in a range
for i in range(4):
    print(random.random())

#in a specific range
for i in range(8):
    print(random.randint(20,100))

#random choice from a list
numbers = [1,2,3,4,5]
var = random.choice(numbers)
print(var)

members = ['fahad','anas','ali','hamza']
mem = random.choice(members)
print(mem)

#exercise
for i in range(1):
    print("(", random.randint(1,8) , "," , random.randint(1,8),")")

#exercise for roll dice
class Dice:
    def roll(self):
        first = random.randint(1,6)
        second = random.randint(1,6)
        return(first,second)
dice = Dice()
print(dice.roll())