names = ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
print(names)
print(names[0])  # Output: Alice
print(names[1])  # Output: Bob  
print(names[2:])
names[0] = 'John'
print(names)  # Output: ['John', 'Bob', 'Charlie', 'David', 'Eve']

#largest number in the list
numbers = [10, 5, 8, 12, 22]
largest = numbers[0]
for num in numbers:
    if num > largest:
        largest = num
print("largest numbers is: ", largest)

#smallest number in the list
numbers = [10, 5, 8, 12, 22,  5]
smallest = numbers[0]
for num in numbers:
    if num < smallest:
        smallest = num
print("smallest numbers is: ", smallest)