import numpy as np

array_1d = np.array([10, 20, 30, 40, 50])

array_2d = np.array([
    [10, 20, 30],
    [40, 50, 60],
    [70, 80, 90]
])

array_3d = np.array([
    [[1, 2, 3], [4, 5, 6]],
    [[7, 8, 9], [10, 11, 12]]
])

arrays = [array_1d, array_2d, array_3d]

for i, array in enumerate(arrays, start=1):
    print(f"\n{array.ndim}D ARRAY")
    print("Array:\n", array)
    print("Dimensions:", array.ndim)
    print("Shape:", array.shape)
    print("Total Elements:", array.size)
    print("Data Type:", array.dtype)
    print("Memory Size:", array.nbytes, "bytes")

print("\nARRAY INDEXING")
print("1D Element:", array_1d[2])
print("2D Element:", array_2d[1, 2])
print("3D Element:", array_3d[1, 0, 2])

print("\nARRAY SLICING")
print("1D Slice:", array_1d[1:4])
print("2D First Row:", array_2d[0, :])
print("3D First Matrix:\n", array_3d[0])

print("\nARRAY RESHAPING")
reshaped_array = np.arange(12).reshape(3, 4)

print("Original Array:\n", np.arange(12))
print("Reshaped Array:\n", reshaped_array)
print("New Shape:", reshaped_array.shape)
