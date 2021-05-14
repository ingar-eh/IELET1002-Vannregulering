class Time:
    def __init__(self,h,m,s):
        self._h = h 
        self._m = m
        self._s = h
 
    #Read-only field accessors
    @property
    def hours(self):
        return self._h
 
    @property
    def minutes(self):
        return self._m
 
    @property
    def seconds(self):
        return self._s
 
    
    @staticmethod
    def _cmp(time1,time2):
        if time1._h < time2._h:
            return 1
        if time1._h > time2._h:
            return -1
        if time1._m < time2._m:
            return 1
        if time1._m > time2._m:
            return -1
        if time1._s < time2._s:
            return 1
        if time1._s > time2._s:
            return -1
        return 0
    
    def __eq__(self, other):
        return True if Time._cmp(self, other) == 0 else False

    def __lt__(self, other):
        return True if Time._cmp(self, other) == 1 else False
        
    def __le__(self, other):
        return True if Time._cmp(self, other) != -1 else False
       
t1 = Time(13, 10, 5)
t2 = Time(5, 15, 30)
t3 = Time(5, 15, 30)
t4 = Time(15, 2, 3)
print(t1 < t2)
print(t1 > t2)
print(t2 > t3)
print(t2 >= t3)
print(t1 == t4)


# In the following class, write code for the methods __eq__, __lt__, __le__.