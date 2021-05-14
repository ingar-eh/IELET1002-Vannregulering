"""Water level testing"""

from random import randint
from time import sleep
import matplotlib.pyplot as plt
import pandas as pd

my_index = 1

water_lvl = 500

water_lvl_lowlow = 250
water_lvl_low = 350
water_lvl_high = 650
water_lvl_highhigh = 750

def fill(water_lvl):
    water_lvl += 1
    return water_lvl
    
def empty(water_lvl):
    water_lvl -= 1
    return water_lvl

df = pd.DataFrame({'Level':water_lvl,
                    'Low':water_lvl_low,
                    'High':water_lvl_high,
                    'Min':water_lvl_lowlow,
                    'Max':water_lvl_highhigh},
                    index=[0])

while my_index < 5000:
    water_lvl += randint(-8, 8)
    # print('Water level 1 is:', water_lvl_1)
    
    if water_lvl < water_lvl_low:
        water_lvl = fill(water_lvl)
        print('Filling due to low level.')
        if water_lvl < water_lvl_lowlow:
            print('WARNING - Dangerously low level')
    
    elif water_lvl > water_lvl_high:
        water_lvl = empty(water_lvl)
        print('Emptying due to high level')
        if water_lvl > water_lvl_highhigh:
            print('WARNING - Dangerously high level')
            
    print('Water level is:', water_lvl)
    
    df = df.append({'Level':water_lvl,
                    'Low':water_lvl_low,
                    'High':water_lvl_high,
                    'Min':water_lvl_lowlow,
                    'Max':water_lvl_highhigh},
                    ignore_index=True)
    
    my_index += 1
    
    
plt.title('Historic Water Level', fontsize=20)
plt.plot(df['Level'],'b-', linewidth=2)
plt.plot(df['Low'],'r-', linewidth=1)
plt.plot(df['High'],'r-', linewidth=1)
plt.plot(df['Min'],'r-', linewidth=2)
plt.plot(df['Max'],'r-', linewidth=2)
plt.xlabel('Reading', fontsize=15)
plt.ylabel('Level [m]', fontsize=15)
plt.grid()
    
    
    