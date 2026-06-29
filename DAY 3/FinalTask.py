print("===== Shopping Cart Program =====")

inventory = ("apple", "banana" , "milk")

cart = []
print("Welcome to the shopping cart program!")

print(inventory)
while True:
    print(f"1.Add item\n2.View Cart\n3.Checkout")
    choice = input("Enter your choice (1-3): ")
    if choice == "1":
        item_name = input("Enter Item Name: ").lower()         
        if item_name in inventory:
            cart.append(item_name)
            print("Item has been added successfully!")
        else:
            print("Error: Item not found in inventory!")
    elif choice == "2":
        if len(cart) == 0:
            print("Your cart is empty!")
        else:
            print("Your items in the cart are: ")
            for item in cart:
                print(item)
    elif choice == "3":
        print("Final Cart: ", cart)
        print("Length of Final Cart: " , len(cart))
        print("Thank you for your shopping!")
        break

    else:
        print("Invalid Choice!")
              

