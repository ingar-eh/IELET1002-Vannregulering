class Circle():
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14 * self.radius ** 2
        
    @property
    def diameter(self):
        return 2 * self.radius
    
    @property
    def circumference(self):
        return 2 * 3.14 * self.radius
    
c1 = Circle(5)    
        
        