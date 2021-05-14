"""
VMB_Gustav Simulation
"""

import VMB_Classes as VMB
import pandas as pd
import os
from time import time
from random import randint

df_temp = 0   # Global varibale that allows data to be temporarily stores whilst waiting for file access




def get_ESP_readings(): # Updating signals sent from ESP
    
    signal_list = []

    for number in [1,2,3]:
    
    
        with open(f'/home/pi/VMB_Gustav/Kommunikasjon/ESP{number}.txt') as file:
            lines = file.read()
            split = lines.split(';')
            
            if split[1] != ' Transmission failed':
                signal_list.append(split[1:])
            
            else:
                signal_list.append('no data')
                
    return signal_list
            
            
            
            
            
dam1 = VMB.Dam(id = 'Dam 1',          # Creating the dam objects
               base_area = 1964,                   
               outflow = 3,
               lvl_low = 20,
               lvl_high = 380,
               lvl_max = 400,
               lvl = 0,
               ESP_control_signal = 0,
               internet_control_signal = VMB.get_SCADA_data()[0],
               ESP_command_signal = 0,
               internet_command_signal = VMB.get_SCADA_data()[1])

dam2 = VMB.Dam(id = 'Dam 2',
               base_area = 1964,
               outflow = 2,
               lvl_low = 15,
               lvl_high = 185,
               lvl_max = 400,
               lvl = 0,
               ESP_control_signal = 0,
               internet_control_signal = VMB.get_SCADA_data()[0],
               ESP_command_signal = 0,
               internet_command_signal = VMB.get_SCADA_data()[2])

dam3 = VMB.Dam(id = 'Dam 3',
               base_area = 1964,
               outflow = 1,
               lvl_low = 10,
               lvl_high = 90,
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
        
    
def update_ESP_readings():
    
    signals = get_ESP_readings()
    
    if isinstance(signals[0], list):
        dam1.ESP_control_signal = int(signals[0][1])
        dam1.ESP_command_signal = int(signals[0][0])
        dam1.lvl = int(signals[0][2])
        
    if isinstance(signals[1], list):
        dam2.ESP_control_signal = int(signals[1][1])
        dam2.ESP_command_signal = int(signals[1][0])
        dam2.lvl = int(signals[1][2])
        
    if isinstance(signals[2], list):
        dam3.ESP_control_signal = int(signals[2][1])
        dam3.ESP_command_signal = int(signals[2][0])
        dam3.lvl = int(signals[2][2])
    
    
def take_reading():
    
    # Ensures recommendations and signals are up-to-date
    update_recommendations()
    update_SCADA_readings()
    
    
    update_ESP_readings()
    
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
    
    with open('/home/pi/VMB_Gustav/Kommunikasjon/Commands.txt', 'w') as file:
        file.write(str(dam1.command) + str(dam2.command) + str(dam3.command))



def publish_readings(df_temp):

    new_reading = take_reading()
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
   
previous_millis = millis()

df_temp = publish_readings(df_temp)



# PROGRAM LOOP

while True:
    
    # Updates and publishes readings every 30 seconds:
    
    if millis() > previous_millis + 5000:
        previous_millis = millis()
        
        df_temp = publish_readings(df_temp)
