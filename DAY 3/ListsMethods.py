numbers = [10, 5, 8, 12, 22, 5]
numbers.append(15)
print(numbers)  # Output: [10, 5, 8, 12, 22, 5, 15]

numbers.insert(3,99)
print(numbers)  # Output: [10, 5, 8, 99, 12, 22, 5, 15]

numbers.remove(5)
print(numbers)

numbers.pop()
print(numbers)  # Output: [10, 8, 99, 12, 22, 5]

print(numbers.index(99))

print(8 in numbers)  # Output: True

print(numbers.count(10))

print(numbers.sort())
numbers.sort()
print(numbers)

numbers.sort()
numbers.reverse()
print(numbers)

numbers2 = numbers.copy()
print(numbers2)


numbers.clear()

#exercise for remove duplicate numbers
numbers = [10, 5, 8, 12, 22, 5, 15,5,8,10,5,8,12,22,5,15,5,8]
unique_num = []
for num in numbers:
    if num not in unique_num:
        unique_num.append(num)
        
print(unique_num)
        

#exercise for show duplicate numbers
numbers = [10, 5, 8, 12, 22, 5, 15,5,8,10,5,8,12,22,5,15,5,8]
s = []
duplicate_num = []
for num in numbers:
    if num in s and num not in duplicate_num:
        duplicate_num.append(num)
    else:
        s.append(num)
        
print(duplicate_num)  