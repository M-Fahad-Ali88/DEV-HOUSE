from abc import ABC,abstractmethod

class DataProcessor(ABC):
    @abstractmethod
    def load_data(self):
        pass

    @abstractmethod
    def process_data(self):
        pass

    @abstractmethod
    def save_data(self):
        pass

class CSVProcessor(DataProcessor):
    def load_data(self):
        print("laod CSV Data")
    def process_data(self):
        print("processing CSV Data")
   

csv  = CSVProcessor()
csv.load_data()
csv.process_data()
csv.save_data()


print(DataProcessor.__abstractmethods__)
print(CSVProcessor.__abstractmethods__)


obj = DataProcessor()

