class Fraction:
    def __init__(self, nr, dr=1):
        if dr < 0:
            self.nr = nr*-1
            self.dr = dr*-1
        else:
            self.nr = nr
            self.dr = dr
            
        self._reduce()
        
    def show(self):
        print(f'{self.nr}/{self.dr}')
        
    def multiply(self, fraction):
        if isinstance(fraction, int):
            fraction = Fraction(fraction)
        f = Fraction(self.nr * fraction.nr, self.dr * fraction.dr)
        f._reduce()
        return f
    
    def add(self, fraction):
        if isinstance(fraction, int):
            fraction = Fraction(fraction)
        f = Fraction(self.nr*fraction.dr + self.dr*fraction.nr, self.dr*fraction.dr)
        f._reduce()
        return f
    
    
    def _reduce(self):
        factor = Fraction.hcf(self.nr, self.dr)
        
        self.nr //= factor
        self.dr //= factor
        

    @staticmethod
    def hcf(x,y):
        x=abs(x)
        y=abs(y)
        smaller = y if x>y else x
        s = smaller
        while s>0:
            if x%s==0 and y%s==0:
                break
            s-=1
        return s
    
    
f1 = Fraction(2,3)
f1.show()
f2 = Fraction(3,4)
f2.show()
f3 = f1.multiply(f2)
f3.show()
f3 = f1.add(f2)
f3.show()
f3 = f1.add(5) 
f3.show()
f3 = f1.multiply(5) 
f3.show()