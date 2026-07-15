#number comparison

def max_num(num1, num2):
    

    if num1 > num2:
        print(f"{num1} is greater than {num2}" )
    elif num1 < num2:
        print(f"{num2} is greater than {num1}" )
    elif num1 == num2:
        [print(f"{num1} is equal to {num2}" )]
    else:
        print("Enter a valid number" )

num1 = int(input("Enter First Number: "))
num2 = int(input("Enter Second Number: "))

max_num(num1, num2)