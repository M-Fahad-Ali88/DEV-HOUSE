print("===== Welcome to the Health Planner =====")


while True:


    name = input("Enter your name: ").strip()
    age = int(input("Enter your age: "))
    weight = float(input("Enter your weight: "))
    w1 = input("Is this weight in (L)bs or (K)gs? ").lower().strip()
    height = float(input("Enter your height in centimeters: "))

    if w1.lower()== 'l':
        weight_in_kgs = weight * 0.453592
        weight_lbs=weight
        weight_kgs = weight_in_kgs
    elif w1.lower() == 'k':
        weight_in_lbs = weight * 2.20462
        weight_kgs=weight
        weight_lbs = weight_in_lbs
    else:
        print("Invalid input for weight unit. Please enter 'L' for pounds or 'K' for kilograms.")
        break

    BMI = weight_kgs / (height / 100) **2
    category = ""

    if BMI < 18.5:
        category = "Underweight"
    elif 18.5 <= BMI < 25.0:
        category = "Normal weight"
    elif 25 <= BMI < 30.0:
        category = "Overweight"
    else:
        category = "Obese"  
    
    if age < 18:
        print("Youth Alert: Please consult a healthcare professional for personalized advice.")
        
    print(f"User Profile: {name.title()} (Age: {age})")
    if w1.lower() == 'l':
        print(f"Weight in Lbs: {weight_lbs:.1f} Lbs matches approximately {weight_kgs:.1f} Kgs.")
    elif w1.lower() == 'k':
        print(f"Weight in Kgs: {weight_kgs:.1f} Kgs matches approximately {weight_lbs:.1f} Lbs.")
        
    print(f"Your calculated BMI is: {round(BMI, 1)}")
    print(f"Evaluation: Your BMI indicates that you are in the {category} category.\n")
    
    choice = input("Would you like to enter another profile? (y/n): ").lower().strip()
    if choice == 'y':
        continue
    elif choice == 'n':
        print("GoodBye!")
        break