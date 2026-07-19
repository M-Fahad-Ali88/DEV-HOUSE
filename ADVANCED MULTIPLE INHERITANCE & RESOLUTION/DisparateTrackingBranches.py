

class A:
    def show(slef):
        print("A")

class B(A):
    def show(slef):
        print("B")
        super().show()


class C(A):
    def show(slef):
        print("C")
        super().show()

class D(C,B):
    pass

d = D()
d.show()

