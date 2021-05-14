class Book():
    def __init__(self, isbn, title, author, publisher, pages, price, copies):
        self._isbn = isbn
        self._title = title
        self._author = author
        self._publisher = publisher
        self._pages = pages
        self._price = price
        self._copies = copies
        
    def display(self):
        print(f'ISBN = {self._isbn}')
        print(f'Title = {self._title}')
        print(f'Price = {self._price}')
        print(f'Copies = {self._copies}')
        
    def in_stock(self):
        return (self._copies > 0)
    
    def sell(self):
        if self.in_stock():
            self._copies -= 1
            print(f'Copies = {self._copies}')
            
    @property
    def price(self):
        return self._price
        
        
    @price.setter
    def price(self, new_price):
        if (50 <= new_price <= 1000):
            self._price = new_price
        else:
            raise ValueError('Price out of valid range.')



        
book1 = Book('957-4-36-547417-1', 'Learn Physics','Stephen', 'CBC', 350, 250,10)
book2 = Book('652-6-86-748413-3', 'Learn Chemistry','Jack', 'CBC', 400, 220,20)
book3 = Book('957-7-39-347216-2', 'Learn Maths','John', 'XYZ', 500, 300,5)
book4 = Book('957-7-39-347216-2', 'Learn Biology','Jack', 'XYZ', 400, 200,6)

books = [book1, book2, book3, book4]
for book in books:
    book.display()
    print('\n')
    
jacks_books = []
for book in books:
    if book._author == 'Jack':
        jacks_books.append(book)
        
print("\nJack's books are:\n")
for book in jacks_books:
    book.display()
    print('\n')