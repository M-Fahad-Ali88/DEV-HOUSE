import math

weight = int(input("Enter your Weight: "))
unit = input("(L)bs or (K)g: ")

if unit.upper() == "L":
    result = weight*0.45
    print(f"You are {result} kilos.")
elif unit.upper() == "K":
    result = weight/0.45
    print(f"You are {result} pounds.")
else:
    print("Valid Unit is required!")