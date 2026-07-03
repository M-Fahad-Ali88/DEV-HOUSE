#University Course Registration System

def register_student(first_name,last_name,student_id,department,course_name,semester):
    print(f"========== University Course Registration ==========")
    print(f"Student Name: {first_name} {last_name}")
    print(f"Stident_ID: {student_id}")
    print(f"Department: {department}")
    print(f"Course: {course_name}")
    print(f"Semester: {semester}")
    print("Registration Successful")
    print(f"=====================================================")

    print("Welcome ",first_name,last_name, "!")
    print("You have successfully enrolled in " , course_name)
    print("Good Luck in Semester ",semester)

print("Using Positional Arguments")
register_student(
    "Fahad" , 
    "Ali",
    19,
    "BSCS",
    "DSA",
    4
)

print("Using Keyword Arguments")
register_student(
    first_name = "Anas",
    last_name = "Ali",
    student_id = 30,
    department = "BSFT",
    course_name = "Milk Testing",
    semester = 7
)