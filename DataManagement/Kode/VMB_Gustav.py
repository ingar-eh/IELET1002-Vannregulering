"""
VMB_Gustav Simulation
"""

import VMB_Classes as VMB
import pandas as pd
import os
from time import time
import serial
from random import randint

df_temp = 0   # Global varibale that allows data to be temporarily stores whilst waiting for file access

            
dam1 = VMB.Dam(id = 'Dam 1',          # Creating the dam objects
               base_area = 1964,                   
               outflow = 3,
               lvl_low = 50,
               lvl_high = 375,
               lvl_max = 420,
               lvl = 0,
               ESP_control_signal = 0,
               internet_control_signal = VMB.get_SCADA_data()[0],
               ESP_command_signal = 0,
               internet_command_signal = VMB.get_SCADA_data()[1])

dam2 = VMB.Dam(id = 'Dam 2',
               base_area = 1964,
               outflow = 2,
               lvl_low = 50,
               lvl_high = 335,
               lvl_max = 390,
               lvl = 0,
               ESP_control_signal = 0,
               internet_control_signal = VMB.get_SCADA_data()[0],
               ESP_command_signal = 0,
               internet_command_signal = VMB.get_SCADA_data()[2])

dam3 = VMB.Dam(id = 'Dam 3',
               base_area = 1964,
               outflow = 1,
               lvl_low = 50,
               lvl_high = 345,
               lvl_max = 400,
               lvl = 0,
               ESP_control_signal = 0,
               internet_control_signal = VMB.get_SCADA_data()[0],
               ESP_command_signal = 0,
               internet_command_signal = VMB.get_SCADA_data()[3])



# --- DEFINITIONS THAT DEPEND UPON THERE ALREADY EXISTING 3 DAM INSTANCES ---

def drain(from_dam, to_dam, iterations):            # Simulating water transfer between dams
    for i in range(iterations):
        from_dam - from_dam.outflow
        to_dam + from_dam.outflow

def update_recommendations():                  # Simulation recommendation algorithm
    dam1.recommendation, dam2.recommendation, dam3.recommendation \
        = VMB.get_recommendation(dam1, dam2, dam3)


def update_SCADA_readings():  # Updating signals sent from SCADA system
    
    # Updating internet command signals
    dam1.internet_command_signal, dam2.internet_command_signal, dam3.internet_command_signal \
        =  VMB.get_SCADA_data()[1:]
    
    # Updating internet control signals
    for dam in [dam1, dam2, dam3]:
        dam.internet_control_signal = VMB.get_SCADA_data()[0]
        
    
ser = serial.Serial('/dev/ttyUSB0', 115200)
def update_ESP_readings():
    for i in range(10):
        try:
            waiting = ser.in_waiting
            if(waiting > 0):
                data = str(ser.readline())
                
                # Ensures that incoming signal is of expected format:
                try:
                    if data[7] in ['0','1']:
                        
                        # Checks which ESP the signal is coming from:
                        ESPid = data[5]
                        
                        if ESPid == '1':
                            dam = dam1
                        elif ESPid == '2':
                            dam = dam2
                        elif ESPid == '3':
                            dam = dam3
                        else:
                            print(f'ESPid not found when collecting data. Current ESPid: {ESPid}')
                            
                        try:
                            dam.lvl = int(data[11:-2])
                        except ValueError:
                            dam.lvl = int(data[11:-3])
                        
                        try:
                            dam.ESP_control_signal = int(data[9])
                            dam.ESP_command_signal = int(data[7])
                        except ValueError:
                            dam.ESP_control_signal = 0
                            dam.ESP_command_signal = 0
                            print('WARNING: Unexpected ESP signal values')
                        
                except IndexError:
                    print('WARNING: Unexpected ESP signal format')

                
        except FileNotFoundError:
            print('File not found')
        except serial.SerialException:
            print('Serial port in use')

    

    
def take_reading():
    
    # Ensures recommendations and signals are up-to-date
    update_SCADA_readings()
    update_ESP_readings()
    update_recommendations()
    
    new_reading = {'Date' : VMB.get_date(),
                    'Time' : VMB.get_time(),
                    'Price' : VMB.get_price_now(),
                    'Level1' : dam1.lvl,
                    'Level2' : dam2.lvl,
                    'Level3' : dam3.lvl,
                    'ValveState1' : dam1.command,
                    'ValveState2' : dam2.command,
                    'ValveState3' : dam3.command,
                    'ESP_control1' : dam1.ESP_control_signal,
                    'ESP_control2' : dam2.ESP_control_signal,
                    'ESP_control3' : dam3.ESP_control_signal,
                    'ESP_command1' : dam1.ESP_command_signal,
                    'ESP_command2' : dam2.ESP_command_signal,
                    'ESP_command3' : dam3.ESP_command_signal,
                    'Nett_control' : dam1.internet_control_signal,
                    'Nett_command1' : dam1.internet_command_signal,
                    'Nett_command2' : dam2.internet_command_signal,
                    'Nett_command3' : dam3.internet_command_signal,
                    'Recommendation1' : dam1.recommendation,
                    'Recommendation2' : dam2.recommendation,
                    'Recommendation3' : dam3.recommendation}
    
    return new_reading



def publish_commands():
    ser.flush()
    
    besp1_command = chr(dam1.command)
    besp2_command = chr(dam2.command)
    besp3_command = chr(dam3.command)

    ser.write((besp1_command + besp2_command + besp3_command + "\n").encode('utf-8'))


def publish_readings(df_temp):

    new_reading = take_reading()
    
    waiting = ser.in_waiting
    print('Waiting in buffer:', waiting)
    publish_commands()

    
    if isinstance(df_temp, pd.core.frame.DataFrame):    # If there is previous data waiting to be published
        df = df_temp
        df = df.append(new_reading, ignore_index=True)
    
    elif os.path.isfile('/home/pi/VMB_Gustav/DataBehandling/Data/Readings.csv') == False: # If there is no existing data
        df = pd.DataFrame(new_reading, index=[0])
        print('\nNew database created with name Readings.csv')
    
    else:
        df = pd.read_csv('/home/pi/VMB_Gustav/DataBehandling/Data/Readings.csv', delimiter='\t', index_col=[0])
        df = df.append(new_reading, ignore_index=True)
    
    print(f'\nMeasurement taken at time {VMB.get_time()}')
    
    try:
        df.to_csv('/home/pi/VMB_Gustav/DataBehandling/Data/Readings.csv', sep='\t')
        df_temp = 0     # If the reading is successfully uploaded, the 'df-cache' is emptied
        
    except PermissionError:
        print('Currently unable to publish data due to PermissionError')
        df_temp = df    # The data frame is stored temporarily until file permission is gained
        
        
    return df_temp


millis = lambda: int(round(time() * 1000))




"""MAIN PROGRAM"""

# INITIAL READINGS:
   
previous_reading_millis = millis()
previous_prices_millis = millis()


VMB.publish_prices('hourly')
df_temp = publish_readings(df_temp)


from time import sleep
# PROGRAM LOOP

while True:
    
    # Updates and publishes readings every 5 seconds:
    if millis() > previous_reading_millis + 5000:
        previous_reading_millis = millis()
        
        df_temp = publish_readings(df_temp)
        
#         print(f'Dam1 lvl: {dam1.lvl}')
#         print(f'Dam1 control signal: {dam1.internet_control_signal}')
#         print(f'Dam1 command signal: {dam1.internet_command_signal}\n')
#         
#         print(f'Dam2 lvl: {dam2.lvl}')
#         print(f'Dam2 control signal: {dam2.internet_control_signal}')
#         print(f'Dam2 command signal: {dam2.internet_command_signal}\n')
#         
#         print(f'Dam3 lvl: {dam3.lvl}')
#         print(f'Dam3 control signal: {dam3.internet_control_signal}')
#         print(f'Dam3 command signal: {dam3.internet_command_signal}\n')
        
    # Updates and published prices every 30 minutes:
    if millis() > previous_prices_millis + 18000000:
        previous_prices_millis = millis()        
        
        VMB.publish_prices('hourly')          