class Tank:
    def __init__(self, level, minimum, low, high, maximum):
        self.level = level
        self.minimum = minimum
        self.low = low
        self.high = high
        self.maximum = maximum
        
    def description(self):
        print('Level =', self.level)
        print('Minimum =', self.minimum)
        print('Low =', self.low)
        print('High =', self.high)
        print('Maximum =', self.maximum)
        
        
    @property
    def level(self):
        return self._level
    
    @level.setter
    def level(self, new_level):
        if 0 <= new_level <= 100:
            self._level = new_level
        else:
            raise ValueError('The level is outside the valid parameters.')
        
tank1 = Tank(50, 0, 20, 80, 100)