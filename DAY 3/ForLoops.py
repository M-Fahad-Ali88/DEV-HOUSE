for students in ["ali","fahad","anas"]:
    print(students)


for fruits in ["apple","banana","mango"]:
    print(fruits)


for numbers in range(11,30,5):
    print(numbers)

prices = [10,20,30,40,50]
sum = 0
mul =1
div = 1
for price in prices:
    sum += price
print("Total Price is: ", sum)


for price in prices:
    mul *= price
print("Multiplication of all prices is: ", mul)

for price in prices:
    div /= price
print("Division of all prices is: ", div)