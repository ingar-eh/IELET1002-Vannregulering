import serial
import time
from random import randint

millis = lambda: int(round(time.time() * 1000))
previous_reading_millis = millis()

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout = 1)
ser.flush()

while True:
    if millis() > previous_reading_millis + 5000:
        previous_reading_millis = millis()
    
    
        print(f'Serial in waiting: {ser.in_waiting}')
    
        esp1 = randint(0, 5)
        esp2 = randint(0, 7)
        esp3 = randint(0, 9)


        besp1 = chr(esp1)
        besp2 = chr(esp2)
        besp3 = chr(esp3)
        print(f'besp1: {esp1}')
        print(f'besp2: {esp2}')
        print(f'besp3: {esp3}')

        ser.write((besp1 + besp2 + besp3 + "\n").encode('utf-8'))
    
