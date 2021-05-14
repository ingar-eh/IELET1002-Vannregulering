import serial
from time import sleep
print('hi')

ser = serial.Serial('/dev/ttyUSB0', 115200)
while True:
    waiting = ser.in_waiting
    print(waiting)
    if(waiting > 0):
        data = str(ser.readline())
        if data[7] in ['0','1']:
            ESPid = data[5]
            print(f'Fra ESP{str(ESPid)}: {data}')
            with open(f'/home/pi/VMB_Gustav/Kommunikasjon/ESP{ESPid}.txt','w') as file:
                file.write(str(data)[2:-3])
    else:
        ser.write(b'Hei')
        
    
    sleep(0.2)