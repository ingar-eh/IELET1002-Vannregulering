class Account:
    
    def __init__(self, name, balance=0):
        self.name = name
        self.balance = balance
        
    def display(self):
        print('Name:', self.name)
        print('Balance:', self.balance)
        
    def withdraw(self, amount):
        self.balance -= amount
        
    def deposit(self, amount):
        self.balance += amount
        
a1 = Account()
a2 = Account()        
        
a1.set_details('Sim', 5)
a2.set_details('Lena', 10)