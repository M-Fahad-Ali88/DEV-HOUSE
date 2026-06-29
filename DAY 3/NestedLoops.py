for x in range(4):
    for y in range(3):
        print(f"({x},{y})")

#practice
for x in [5,2,5,2,2]:
    print("x" * x)

#with inner loop
numbers = [5,2,5,2,2]
for x in numbers:
    output = ""
    for y in range(x):
        output += "x"
    print(output)

#for L
numberss = [1,1,1,1,1,1,5]
for x in numberss:
    output = ""
    for  y in range(x):
        output += "x"
    print(output)