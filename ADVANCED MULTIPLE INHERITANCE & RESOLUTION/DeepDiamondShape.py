class A:
    def show(self):
        print("A")
class B(A):
    def show(self):
        print("B")
        super().show()
class C(B):
    def show(self):
        print("C")
        super().show()
class D(C,A):
    def show(self):
        print("D")
        super().show()
    
d = D()
d.show()

print(D.mro())