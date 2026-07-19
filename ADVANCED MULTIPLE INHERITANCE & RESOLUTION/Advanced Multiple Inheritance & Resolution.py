class Base:
    def process(self):
        print("Base")


class LoggerMixin(Base):
    def process(self):
        print("Logger")
        super().process()


class ValidationMixin(Base):
    def process(self):
        print("Validation")
        super().process()


class SaveMixin(Base):
    def process(self):
        print("Save")
        super().process()



class User(LoggerMixin, ValidationMixin):
    def process(self):
        print("User")
        super().process()


class Admin(ValidationMixin, SaveMixin):
    def process(self):
        print("Admin")
        super().process()


class SuperAdmin(User, Admin):
    def process(self):
        print("SuperAdmin")
        super().process()


obj = SuperAdmin()

print("MRO:")
print(SuperAdmin.mro())

print("\nExecution:")
obj.process()