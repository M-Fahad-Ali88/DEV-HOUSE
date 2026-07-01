#Variable Scoping (LEGB RULE)

#Local(L)
#name is local to the function greet()
def greet():
    name = "Fahad"
    print(name)
greet()

#Enclosing(E)
def outer():
    #outer function scope will be enclosing scope for inner function
    x=10
    y=9
    def inner():
        print(x+y)
    inner()
outer()  

#Global(G)
#x is global variable
x=10
def num():
    print(x*10)
num()

#Built-in(B)
#len is built-in function
name  = "Anas"
print(len(name))
