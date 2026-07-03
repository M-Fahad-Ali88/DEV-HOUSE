def city(name, population):
    print(f"City Name: {name}\nPopulation: {population}")
print("City Details")
#keyword arguments
city(name = "Faisalabad", population = 15000000)
print("City Details End")

#Positional arguments
city("Lahore" , 20000000)
print("City Details End")

#special case
city(population = 30000000, name = "Karachi")
print("City Details End")

city(name = "Islamabad", population = 10000000)

def user(first_name, last_name):
    print(f'Hello {first_name} {last_name}!')
print("Start")
user("Anas" , last_name = "Ali")
print("Finish")