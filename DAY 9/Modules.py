import ModulesConverter
from ModulesConverter import lbs_to_Kgs
print(lbs_to_Kgs(80))
from ModulesConverter import kgs_to_lbs
print(kgs_to_lbs(90))
print(ModulesConverter.lbs_to_Kgs(100))
print(ModulesConverter.kgs_to_lbs(100))

from ModulesConverter import find_max
numbers = [10,20,30,40,5000]
print("Maximum number is: ",find_max(numbers))