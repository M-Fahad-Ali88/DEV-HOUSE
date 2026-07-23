from dataclasses import dataclass



def get_student_dictionary() -> dict[str, str | int | float]:
    return {
        "name": "Fahad",
        "age": 22,
        "cgpa": 3.85
    }



@dataclass
class Student:
    name: str
    age: int
    cgpa: float


def get_student() -> Student:
    return Student(
        name="Fahad",
        age=22,
        cgpa=3.85
    )


def display_dictionary(student: dict[str, str | int | float]) -> None:
    print("Dictionary Data")
    print("Name:", student["name"])
    print("Age:", student["age"])
    print("CGPA:", student["cgpa"])



def display_student(student: Student) -> None:
    print("Typed Structure Data")
    print("Name:", student.name)
    print("Age:", student.age)
    print("CGPA:", student.cgpa)


def main() -> None:

    student_dict = get_student_dictionary()
    display_dictionary(student_dict)

    print()

    student = get_student()
    display_student(student)


if __name__ == "__main__":
    main()