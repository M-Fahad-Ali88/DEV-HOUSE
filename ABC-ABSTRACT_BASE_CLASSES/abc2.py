from abc import ABC,abstractmethod

class Payment(ABC):
    
    @abstractmethod
    def pay(self,amount):
        pass
    @abstractmethod
    def refund(self,amount):
        pass

class CreditCard(Payment):

    def pay(self,amount):   
        print("Paid " , amount , "via Credit Card.")
    
    def refund(self,amount):
        print("Refund " , amount , "via Credit Card.")

class Paypal(Payment):

    def pay(self,amount):   
        print("Paid " , amount , "via PayPal.")
    
    def refund(self,amount):
        print("Refund " , amount , "via PayPal.")
        
c = CreditCard()
p = Paypal()

c.pay(1000)
c.refund(500)

print()

p.pay(6000)
p.refund(10000)