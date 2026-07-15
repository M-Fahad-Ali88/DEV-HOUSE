from pathlib import Path
path = Path("DAY 10")
for files in path.glob('*.*'):
    print(files)

path = Path("DAY 7")
for files in path.glob('*'):
    print(files)

path = Path("DAY 4")
for files in path.glob('*.py'):
    print(files)

path = Path("DAY 11")
print(path.rmdir())

path = Path("DAY 11")
print(path.mkdir())

path = Path("DAY 11")
print(path.exists())


path = Path("DAY 14")
print(path.exists())
