print("===== Shopping System =====")
customer_name = input("\nEnter Customer Name: ")
product_name = input("Enter Product Name: ")
price = float(input("Enter Price: "))
quantity = int(input("Enter Quantity: "))
total_bill = price*quantity
discount = total_bill*0.1
final_bill = total_bill-discount

print(f"\n\n------SHOPPING BILL------\nCustomer: {customer_name.upper()}\nProduct: {product_name.lower()}\nProduct Length: {len(product_name)}\nPrice: {price:.2f}\nQuantity: {quantity}\nTotal: {total_bill:.2f}\nDiscount: {discount:.2f}\nFinal Bill: {final_bill:.2f}")