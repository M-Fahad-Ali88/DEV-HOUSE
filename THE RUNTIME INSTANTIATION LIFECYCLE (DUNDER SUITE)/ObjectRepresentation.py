class Student:
    def __init__(self, name, age, cgpa):
        self.name = name
        self.age = age
        self.cgpa = cgpa

    def __repr__(self):
        return f"Student(name='{self.name}', age={self.age}, cgpa={self.cgpa})"

    def __str__(self):
        return f"{self.name} | Age: {self.age} | CGPA: {self.cgpa}"


student = Student("Fahad", 21, 3.75)

print(repr(student))
print(str(student))
print(student)