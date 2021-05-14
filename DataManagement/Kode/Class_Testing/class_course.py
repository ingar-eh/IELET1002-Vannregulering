class Course:
    
    def __init__(self, title, instructor, price):
        self.title = title
        self.instructor = instructor
        self.price = price
        self.lectures = []
        self.users = []
        self.ratings = []
        
    def __str__(self):
        return self.title
    
    def new_user_enrolled(self, new_user):
        self.users.append(new_user)
    
    def recieved_a_rating(self, new_rating):
        if isinstance(new_rating, int):
            self.ratings.append(new_rating)
        else:
            raise ValueError('Invalid rating')
            
            
    @property
    def avg_rating(self):
        if len(self.ratings) == 0:
            return 0
        return (sum(self.ratings) / len(self.ratings))
        
    def show_details(self):
        print(f'Title = {self.title}')
        print(f'Instructor = {self.instructor}')
        print(f'Price = {self.price}')
        print(f'Lectures = {self.lectures}')
        print(f'Users = {self.users}')
        print(f'Ratings = {self.ratings}')
        print(f'Average rating = {self.avg_rating}')
    
    
    
m1 = Course('Mechanics 1', 'Mr. Baxter', 200)
s2 = Course('Statistics 2', 'Mr Critchley', 150)