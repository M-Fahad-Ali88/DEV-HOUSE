price=1000000
is_good_credit=True

if is_good_credit:
    down_payment=price*0.1
else:
    down_payment=price*0.2
print(f"Down payment: ${down_payment}")