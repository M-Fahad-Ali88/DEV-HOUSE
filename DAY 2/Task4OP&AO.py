#Q1
import math
x=25 + 3*4**2 - 6%4
print(math.sqrt(x))

#Q2
y=100- 5*3**2 + 12%5
print(math.sqrt(y))

#Q3
z=50 + 2*3**3
print(math.ceil(math.sqrt(z)))

#Q4
a=81+ 4*2**3 - 7%3
print(math.floor(math.sqrt(a)))

#Q5
b=64 + 16/4*2**2 - 9%2
print(math.sqrt(b))

#Q6
c=120 - 3*5**2 + 18%7
print(math.ceil(math.sqrt(c)))

#Q7
d=144/3**2 + 6*2**3 - 10%3
print(math.sqrt(d))

#Q8
e=200-4*5**3+25%6
print(math.sqrt(abs(e)))



#Area of distance
x1=7
x2=12
y1=2
y2=5

area_of_distance=math.sqrt((x2-x1)**2+(y2-y1)**2)
print("Area of Distance: ", round(area_of_distance))
print("Area of Distance: ", math.ceil(area_of_distance))
print("Area of Distance: ", math.floor(area_of_distance))
print("Area of Distance: ", (area_of_distance))