customer = {
    "name": "Fahad Ali",
    "age": 30,
    "email": "fahad@example.com",
    "phone": "123-456-7890"
}
print(customer["name"])
print(customer.get("age"))  
print(customer["email"])
print(customer.get("phone"))
print(customer.get("Phone" , "0300-1234567"))
customer["name"] = "Zain Ali"
print(customer["name"])     
print(customer.get("age" , "45"))
print(customer.get("name" , "Anas"))