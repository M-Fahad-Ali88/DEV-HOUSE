class NumberIterator:
    def __init__(self, start, end):
        self.current = start
        self.end = end

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > self.end:
            raise StopIteration

        number = self.current
        self.current += 1
        return number


numbers = NumberIterator(1, 5)

for num in numbers:
    print(num)