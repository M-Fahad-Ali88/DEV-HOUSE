try:
    num1 = int(input("Enter First Number: "))
    num2 = int(input("Enter Second Number: "))
    div = num1//num2
    print("Division of two given numbers is: " , div)
except ZeroDivisionError:
    print("Number can't divide by 0")
except ValueError:
    print("Invalid Value")