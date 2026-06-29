#Student Information System
print("===== Student Information System =====")
student_name = input("\nEnter Student Name: ")
student_age = int(input("Enter Student Age: "))
university_name = input("Enter University Name: ")
gpa = float(input("Enter Student GPA: "))

print("\n\n----- Student Report -----")
print("Name: ", student_name)
print("Age: " , student_age)
print("Age After 5 Yrs: " , (student_age)+5)
print("University Name: " , university_name)
print("GPA: " , gpa)
print("Name Length: " , len(student_name))

print(f"\n\n----- Student Report -----\nName: {student_name.upper()}\nAge: {student_age}\nAge After 5 Yrs: {student_age + 5}\nUniversity: {university_name.lower()}\nGPA: {gpa}\nName Length: {len(student_name)}")