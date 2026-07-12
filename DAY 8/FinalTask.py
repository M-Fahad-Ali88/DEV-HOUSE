#Student Examination Result Management System
#receive input
first_name = input("Enter First Name: ")
last_name = input("Enter Last Name: ")
roll_no = input("Roll Number: ")
department = input("Department: ")
subject_1 = input("Subject 1 Marks: ")
subject_2 = input("Subject 2 Marks: ")
subject_3 = input("Subject 3 Marks: ")

#type conversion
roll_no = int(roll_no)
subject_1 = int(subject_1)
subject_2 = int(subject_2)
subject_3 = int(subject_3)

#string methods
first_name = first_name.strip()
last_name = last_name.strip()
department = department.upper()

#arithmetic operations
total_marks = subject_1 + subject_2 + subject_3
percentage = (total_marks/300)*100

#if statement and logical operators
if percentage >= 80:
    print("Grade: A, Student has promoted to next semester")
elif percentage >= 70:
    print("Grade: B, Student has promoted to next semester")
elif percentage >= 60:
    print("Grade: C, Student has promoted to next semester")
elif percentage >= 50:      
    print("Grade: D, Student has promoted to next semester")
else:
    print("Grade: F, Student has not been promoted to next semester")

#function
def student_report(first_name, last_name, roll_no, department, total_marks, percentage, grade, status):
    print(f"Student Name: {first_name} {last_name}")
    print(f"Roll Number: {roll_no}")
    print(f"Department: {department}")
    print(f"Total Marks: {total_marks}")
    print(f"Percentage: {percentage}%")
    print(f"Grade: {grade}")
    print(f"Status: {status}")

def calculate_result(subject_1, subject_2, subject_3):
    total_marks = subject_1 + subject_2 + subject_3
    percentage = (total_marks/300)*100
    return total_marks, percentage
totalMarks = total_marks
percentage_per = percentage

#keyword arguments
student_report("Fahad","Ali", roll_no=roll_no, department=department, total_marks=totalMarks, percentage=percentage_per, grade="C", status="Promoted")
            
#list
subjects = ["Subject 1", "Subject 2", "Subject 3"]
print("Subjects: ", subjects)

#dictionary
student_info = {
    "name" : f"{first_name} {last_name}",
    "roll_no" : roll_no,
    "department" : department,
    "grade" : "C",
}
print(f"Student Information: {student_info}")

print("===== Student Result Management System =====")

student_report(first_name, last_name, roll_no, department, totalMarks, percentage_per, "C", "Promoted")
print(subjects , end = " ")

