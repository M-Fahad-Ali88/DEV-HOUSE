import numpy as np

array = np.array([
    [10, 20, 30],
    [40, 50, 60]
], dtype=np.int64)

print("ORIGINAL ARRAY")
print(array)

print("\nARRAY INFORMATION")
print("Shape:", array.shape)
print("Dimensions:", array.ndim)
print("Data Type:", array.dtype)
print("Element Size:", array.itemsize, "bytes")
print("Total Memory:", array.nbytes, "bytes")

print("\nMEMORY STRIDES")
print("Strides:", array.strides)

print("\nMEMORY LAYOUT")
print("C Contiguous:", array.flags.c_contiguous)
print("Fortran Contiguous:", array.flags.f_contiguous)

print("\nTRANSPOSED ARRAY")
transposed = array.T
print(transposed)
print("Shape:", transposed.shape)
print("Strides:", transposed.strides)
print("C Contiguous:", transposed.flags.c_contiguous)
print("Fortran Contiguous:", transposed.flags.f_contiguous)

print("\nNON-CONTIGUOUS ARRAY")
non_contiguous = array[:, ::2]
print(non_contiguous)
print("Strides:", non_contiguous.strides)
print("C Contiguous:", non_contiguous.flags.c_contiguous)

print("\nVIEW VS COPY")
view_array = array.view()
copy_array = array.copy()

print("View Shares Memory:", np.shares_memory(array, view_array))
print("Copy Shares Memory:", np.shares_memory(array, copy_array))

print("\nFORTRAN ORDER")
fortran_array = np.asfortranarray(array)

print(fortran_array)
print("Strides:", fortran_array.strides)
print("C Contiguous:", fortran_array.flags.c_contiguous)
print("Fortran Contiguous:", fortran_array.flags.f_contiguous)
