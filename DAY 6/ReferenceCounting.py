a=[1,2,3] #count 1
b=a  #2
del a #1

#0when b goes out of scope, the reference count for the list will be 0 and it will be garbage collected.