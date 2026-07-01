#Deep Copy
import copy
a=[[2,4,6],[1,3,5]]
b=copy.deepcopy(a)
print(a)

#Shallow Copy
import copy
a=[[2,4,6],[1,3,5]]
b=copy.copy(a)
a[0][0]=10.67
print(a)