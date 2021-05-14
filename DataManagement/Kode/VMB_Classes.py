"""
VMB_Gustav Classes
"""

import pandas as pd
import os.path
from datetime import datetime
from nordpool import elspot
import math
import matplotlib.pyplot as plt
from numpy import linspace
import warnings
from requests.exceptions import ConnectionError


def get_time():
    return datetime.now().strftime('%Y-%m-%d  %H:%M:%S')[-8:]

def get_date():
    return datetime.now().strftime('%Y-%m-%d  %H:%M:%S')[:10]

def get_datetime():
    return datetime.now().strftime('%Y-%m-%d  %H:%M:%S')


class Dam:
    
    lvl_min = 0                         # [mm] - Minimum water level is 0 for all dams
    dams_list = []
    
    def __init__(self, id, base_area, outflow,
                 lvl_low, lvl_high, lvl_max, lvl,
                 ESP_control_signal, internet_control_signal,
                 ESP_command_signal, internet_command_signal,
                 recommendation=0):
        
        self._id = id
        self._base_area = base_area     # [cm^2]
        self.outflow = outflow          # [mL/s]
        self.lvl_low = lvl_low          # [mm]
        self.lvl_high = lvl_high        # [mm]
        self.lvl_max = lvl_max          # [mm]
        self.lvl = lvl                  # [mm]
        self.ESP_control_signal = ESP_control_signal
        self.internet_control_signal = internet_control_signal
        self.ESP_command_signal = ESP_command_signal
        self.internet_command_signal = internet_command_signal
        self.recommendation = recommendation
        
        Dam.dams_list.append(self)             # Adding the new dam to the list of dams
        
    def __add__(self, other):
        self._fill(other)
        return f'New water level = {self.lvl}'
        
    def __sub__(self, other):
        self._drain(other)
        return f'New water level = {self.lvl}'
    
    def __repr__(self):
        return self.id
        
   
    
    @property                                  # Creating immutable id property
    def id(self):
        return self._id
    
    @property                                  # Creating immutable base_area property
    def base_area(self):
        return self._base_area
   
    
    @property                                  # Creating immutable ESP_control_signal property
    def ESP_control_signal(self):
        return self._ESP_control_signal
    
    @ESP_control_signal.setter
    def ESP_control_signal(self, incoming_signal):
        Dam.is_valid_signal(incoming_signal)
        self._ESP_control_signal = incoming_signal
    
    
    @property                                  # Creating internet_command_signal property
    def internet_command_signal(self):
        return self._internet_command_signal
   
    @internet_command_signal.setter
    def internet_command_signal(self, incoming_signal):
        Dam.is_valid_signal(incoming_signal)
        self._internet_command_signal = incoming_signal
        
        
    @property                                  # Creating ESP_command_signal property
    def ESP_command_signal(self):
        return self._ESP_command_signal
    
    @ESP_command_signal.setter
    def ESP_command_signal(self, incoming_signal):
        Dam.is_valid_signal(incoming_signal)
        self._ESP_command_signal = incoming_signal
    
    
    @property                                  # Creating immutable internet_control_signal property
    def internet_control_signal(self):
        return self._internet_control_signal
   
    @internet_control_signal.setter
    def internet_control_signal(self, incoming_signal):
        Dam.is_valid_signal(incoming_signal)
        self._internet_control_signal = incoming_signal
        
        
    @property                                  # Creating recommendation property
    def recommendation(self):
        return self._recommendation
   
    @recommendation.setter
    def recommendation(self, new_recommendation):
        if 0 <= new_recommendation <= 1:
            self._recommendation = new_recommendation
        else:
            raise ValueError('Recommendation setter must be in range [0, 1]')
   
    
    @property                                   # Creating lvl_low property
    def lvl_low(self):
        return self._lvl_low
    
    @lvl_low.setter                            
    def lvl_low(self, new_lvl):
        self.is_valid_level(new_lvl)           # Validity checks on lvl_low
        self._lvl_low = new_lvl

        
    @property                                  # Creating lvl_high property
    def lvl_high(self):
        return self._lvl_high
    
    @lvl_high.setter                            
    def lvl_high(self, new_lvl):
        self.is_valid_level(new_lvl)           # Validity checks on lvl_high
        self._lvl_high = new_lvl


    @property                                  # Creating lvl_max property
    def lvl_max(self):
        return self._lvl_max
    
    @lvl_max.setter                            
    def lvl_max(self, new_lvl):
        self.is_valid_level(new_lvl)           # Validity checks on lvl_max
        self._lvl_max = new_lvl
        
        
    @property                                  # Creating lvl property
    def lvl(self):
        return self._lvl
        
    @lvl.setter
    def lvl(self, new_lvl):
        if  new_lvl <= self.lvl_min:
            self._lvl = self.lvl_min
        elif  new_lvl >= self.lvl_max:
            self._lvl = self.lvl_max
        elif self.lvl_min < new_lvl < self.lvl_max:
            self._lvl = new_lvl
        else:
            self._lvl = 0
            print(f'WARNING: level is invalid. Current signal = {new_lvl}')

        
    @property
    def lvl_status(self):
        if self.lvl == self.lvl_min:
            return 'empty'
        elif self.lvl_min < self.lvl < self.lvl_low:
            return 'low'
        elif self.lvl_low <= self.lvl < self.lvl_high:
            return 'ok'
        elif self.lvl_high <= self.lvl < self.lvl_max:
            return 'high'
        elif self.lvl == self.lvl_max:
            return 'full'
        else:
            raise ValueError(f'Error calculating level status. Current level = {self.lvl}')
        
    @property                                  # Creating control property
    def control(self):
        if self.ESP_control_signal == 1:            # Checks ESP first (as local control takes priority)
            return 'local'
        elif self.internet_control_signal == 1:
            return 'remote'                    # Then checks remote control
        elif (self.ESP_control_signal == 0) and (self.internet_control_signal == 0):
            return 'automatic'                 # Defaults to automatic if neither local or remote control are active
        else:
            raise RuntimeError('An error occurred with control signal inputs')
            
            
    @property                                  # Creating command property                        
    def command(self):
        if self.control == 'local':
            return self.ESP_command_signal
        elif self.control == 'remote':
            return self.internet_command_signal
        elif self.control == 'automatic':
            if self.recommendation >= 0.5:
                return 1
            else:
                return 0
        else:
            raise ValueError(f'Error getting command. Current control = {self.control}')
    
    
    
    @property                                  # Calculating the current volume - immutable
    def volume(self):
        return self.base_area * self.lvl / 10  # Volume [mL]
    
    @property                                  # Calculating the current volume - immutable
    def level_percent(self):
        return self.lvl * self.lvl_max  # Volume [mL]

    
    
    def display(self):                         # Method for displaying information about the dam object
        print('\n--- EXTERNAL ---\n')
        print(f'Date = {get_date()}')
        print(f'Time = {get_time()}')
        print(f'Energy price = {get_price_now()} EUR/MWh')
        print('\n--- STATIC DIMENSIONS ---\n')
        print(f'Dam ID = {self.id}')
        print(f'Minimum level = {self.lvl_min}')
        print(f'Low level = {self.lvl_low}')
        print(f'High level = {self.lvl_high}')
        print(f'Maximum level = {self.lvl_max}')
        print(f'Base area = {self.base_area}')
        print(f'Outflow rate = {self.outflow}')
        print('\n--- VARIABLE DIMENSIONS ---\n')
        print(f'Current level = {self.lvl}')
        print(f'Current level status = {self.lvl_status}')
        print(f'Current volume = {self.volume}')
        print('\n--- STATUS ---\n')
        print(f'ESP Control Signal = {self.ESP_control_signal}')
        print(f'Internet Control Signal = {self.internet_control_signal}')
        print(f'Current control = {self.control}')
        print(f'\nESP Command Signal = {self.ESP_command_signal}')
        print(f'Internet Command Signal = {self.internet_command_signal}')
        print(f'Recommended Command = {self.recommendation}')
        print(f"Turbine command = {self.command}")
        
        
    def _fill(self, amount):                    # Method for filling a dam (only used for simulations)
        if type(amount) != int:                 # Ensuring the amount increase is an integer
            raise TypeError(f'Amount must be of type integer, not {type(amount)}.')
        elif self.lvl + amount > self.lvl_max:          # Ensuring the water level remains below the max level
            self.lvl = self.lvl_max
            print(f'{self} is full.')
        else:
            self.lvl += amount
            
    def _drain(self, amount):                   # Method for draining a dam (only used for simulations)
        if type(amount) != int:                 # Ensuring the amount decrease is an integer
            raise TypeError(f'Amount must be of type integer, not {type(amount)}.')
        elif self.lvl - amount < self.lvl_min:          # Ensuring the water level remains above the min level
            self.lvl = self.lvl_min
            print(f'{self} is empty.')
        else:
            self.lvl -= amount


    @staticmethod                              # Method for checking that a given level is a valid input
    def is_valid_level(new_lvl):
        if isinstance(new_lvl, int) == False:           # Ensures level is an integer
            raise TypeError(f'Level must be of type integer, not {type(new_lvl)}.')
        elif (0 <= new_lvl <= 1000) == False:             # Ensures level is within valid range
            raise ValueError(f'Level must be between 0 to 1000 mm.\nYour input: {new_lvl}')
       
    @staticmethod
    def is_valid_signal(incoming_signal):
        if incoming_signal not in [0, 1]:
            raise TypeError(f"Signal must be '0' or '1', not {incoming_signal} of type {type(incoming_signal)}")
        
    @staticmethod                              # Method for deciding which operator has control
    def get_control_signal(ESP_control_signal, internet_control_signal):
        if ESP_control_signal == 1:            # Checks ESP first (as local control takes priority)
            return 'local'
        elif internet_control_signal == 1:
            return 'remote'                    # Then checks remote control
        elif (ESP_control_signal == 0) and (internet_control_signal == 0):
            return 'automatic'                 # Defaults to automatic if neither local or remote control are active
        else:
            raise RuntimeError('An error occurred with control signal inputs')
            



        
        
        
        
# IMPORTING PRICE DATA ETC.


# Initialize class for fetching Elspot prices
prices_spot = elspot.Prices()


def get_prices(period='hourly'): # Imports electricity price in Trondheim for the past month
    

    # Allows the user to chose whether to access hourly or daily price data
    if period == 'hourly':
        def get_trd_prices():
            try:
                hourly = prices_spot.hourly(areas=['Tr.heim'])
                return hourly
            except ConnectionError:
                warnings.warn('Was unable to connect to www.nordpoolgroup.com')
                return 0
        
    elif period == 'daily':
        def get_trd_prices():
            try:
                daily = prices_spot.daily(areas=['Tr.heim'])
                return daily
            except ConnectionError:
                warnings.warn('Was unable to connect to www.nordpoolgroup.com')
                return 0

    else:
        raise ValueError(f'Invalid price data period given, current input: {period}')

    # Imports Trondheim price data from the internet
    trd_prices = get_trd_prices()
    
    if trd_prices == 0:
        print('Price data currently unavailable due to lack of connection.')
        return
    
    # Function terminates if invalid data is recieved from elspot
    if trd_prices.get('areas').get('Tr.heim').get('values')[1].get('value') == math.inf:
        print('Price data currently unavailable.')
        return
        
        # Recalibrates price data if invalid
        trd_prices = get_trd_prices()

    # Extracts the relevant values from the imported data
    previous_prices = trd_prices.get('areas').get('Tr.heim').get('values')
    
    
    # Extracts the price and date from each reading, and adds them to an empty list
    prices = []
    date_times = []
    
    if period == 'hourly':
        for price in previous_prices:
            prices.append(price.get('value'))
            date_times.append(str(price.get('end'))[:16])
            
    # Insert must be use when collecting daily data, as it is downloaded in the
    # opposite chronology as to that of the hourly data.
    elif period == 'daily':
        for price in previous_prices:
            prices.insert(0, price.get('value'))
            date_times.insert(0, str(price.get('end'))[:16])
    
    
    # Creates a list of lists; each sublist containing a date and price
    data_list = []

    for i in range(len(date_times)):

        # Ensures infinite values are not added to the list
        if prices[i] != math.inf:
            data_list.append([date_times[i], prices[i]])

    return data_list



def publish_prices(period='hourly'): # Exports / updates the monthly price data to a .csv file

    # Allocated two different URL paths depending on the time period given
    if period == 'hourly':
        path = '/home/pi/VMB_Gustav/DataBehandling/Data/HourlyPrices.csv'

    elif period == 'daily':
        path = '/home/pi/VMB_Gustav/DataBehandling/Data/DailyPrices.csv'

    else:
        raise ValueError(f'Invalid publish price data period given, current input: {period}')


    # Imports this months price data
    data_list = get_prices(period)

    # Converts the data list into a dataframe
    new_df = pd.DataFrame(data_list,columns=['Time','Price'])

    # Checks for an existing price .csv file
    if os.path.isfile(path) == False:
        print('\nNew database created.')
        
    # If a .csv file already exits, the new dataframe is appended to the old dataframe    
    else:
        old_df = pd.read_csv(path, delimiter='\t', index_col=0)
        
        new_df = old_df.append(new_df)
        
    # The dataframe is 'washed', emitting duplicates and null values
    new_df.drop_duplicates(inplace=True)
    new_df.dropna(inplace=True)
    new_df.reset_index(inplace=True, drop=True)

    new_df.to_csv(path, sep='\t')

    print(f'{period} prices update run')


def display_prices(): # USED FOR DOUBLE CHECKING WEBSITE GRAPHS
    
    # Allocated two different URL paths depending on the time period given
    path_hourly = '/home/pi/VMB_Gustav/DataBehandling/Data/HourlyPrices.csv'

    path_daily = '/home/pi/VMB_Gustav/DataBehandling/Data/DailyPrices.csv'

    
    # Creating graph for hourly measurements
    # Imports price data as dataframe
    df_hourly = pd.read_csv(path_hourly, delimiter='\t', index_col=0)
    
    df_hourly.plot(linestyle='-', linewidth=4, color='blue', figsize=(20,8))
    plt.title("Hourly Energy Prices in Trondheim", fontsize=30)
    plt.xlabel('Time', fontsize=20)
    
    # Ensures 12 evenly spaced out xticks
    times = df_hourly['Time'].tolist()
    xticks_indexes = linspace(0, len(times)-1, 12, dtype=int)
    xticks_labels = df_hourly.iloc[xticks_indexes]['Time'].tolist()
    plt.xticks(xticks_indexes, xticks_labels, rotation=70)
    
    plt.ylabel('Price [EUR/MWh]', fontsize=20)
    plt.grid()
    


    # Creating graph for daily measurements
    # Imports price data as dataframe
    df_daily = pd.read_csv(path_daily, delimiter='\t', index_col=0)
    
    df_daily.plot(linestyle='-', linewidth=4, color='blue', figsize=(20,8))
    plt.title("Daily Energy Prices in Trondheim", fontsize=30)
    plt.xlabel('Date', fontsize=20)
    
    # Ensures 12 evenly spaced out xticks
    times = df_daily['Time'].tolist()
    xticks_indexes = linspace(0, len(times)-1, 12, dtype=int)
    xticks_labels_temp = df_daily.iloc[xticks_indexes]['Time'].tolist()
    # Shortens the tick labels to only include date
    xticks_labels = [tick[:10] for tick in xticks_labels_temp]
    plt.xticks(xticks_indexes, xticks_labels, rotation=70)
    
    plt.ylabel('Price [EUR/MWh]', fontsize=20)
    plt.grid()
    
    
    
def get_todays_averages(): # Gets the average electricity price for today in Trondheim
    
    # Imports current days price data
    hourly_data = pd.read_csv('/home/pi/VMB_Gustav/DataBehandling/Data/HourlyPrices.csv',
                delimiter='\t', index_col=0)
    
    # Imports the current date
    date_today = get_date()
    
    todays_prices = []
    
    # Iterates through the datafram to extract all the prices listed with today's date
    for index, row in hourly_data.iterrows():
        
        if row[0][:10] == date_today:
            todays_prices.append(row[1])
            
    if len(todays_prices) == 0:
        raise ValueError('No prices were found for today when getting daily average.')

    # Takes the average of the past weeks prices, and rounds to two dps.
    todays_mean = round(sum(todays_prices) / len(todays_prices) , 2)
    todays_range = round(max(todays_prices) - min(todays_prices) , 2)  
    
    return todays_mean, todays_range



def get_price_now(): # Gets the current hour electricity price in Trondheim
    
    # Imports current days price data
    hourly_data = pd.read_csv('/home/pi/VMB_Gustav/DataBehandling/Data/HourlyPrices.csv',
                delimiter='\t', index_col=0)
    
    # Imports the current date and hour in the same format as used in the .csv files
    hour_now = get_datetime()[:10] + get_datetime()[11:14]

    # Iterates through the datafram to extract all the prices listed with today's date
    for index, row in hourly_data.iterrows():
        
        if row[0][:13] == hour_now:
            
            # Returns the price data from the current date
            return row[1]
        
    warnings.warn("Was not able to find price data for the current hour.")
    return -1
    
    
def get_SCADA_data(): # Recieves data from the txt file generated by the SCADA interface
    with open('/home/pi/VMB_Gustav/Nettside/VMB_GUSTAV/data/SCADA.txt', 'r') as file:
        
        data_str = file.read(4) # The first 4 indexes of the txt file are the various command signals
        
        # Assigning a variable to each command signal
        internet_control_signal = int(data_str[0])
        internet1_command_signal = int(data_str[1])
        internet2_command_signal = int(data_str[2])
        internet3_command_signal = int(data_str[3])
        
        return internet_control_signal, internet1_command_signal, internet2_command_signal, internet3_command_signal


def percentage_recommendation():
    
    todays_mean, todays_range = get_todays_averages()
    price_now = get_price_now()


    # Calculates the recommendation by seeing how much the current price deviates from the mean
    try:
        recommendation = round((((price_now - todays_mean) / todays_range) + 0.5 ) , 2)
    except ZeroDivisionError:
        print("Recommendation set to 0.00 due to unavailable price data.")
        recommendation = 0.00
        

    # Ensures the recommendation is within the bounds [0, 1]
    if recommendation < 0:
        recommendation = 0.00
        
    elif recommendation > 1:
        recommendation = 1.00

    return recommendation




def get_recommendation(top_dam, middle_dam, bottom_dam): #Returns top- middle- then bottom-dam recommendation

    # If the recommendation is not nominal, it is dependant upon the percentage-
    # recommendation is decided by the percentage_recommendation() function.
    dependant = percentage_recommendation()

    # Refer to attatched 'algorithm' spreadsheet for explanation of cases

    if bottom_dam.lvl_status in ['empty', 'low']:
        
        if middle_dam.lvl_status in ['empty', 'low']:

            if top_dam.lvl_status in ['empty', 'low']:
                return 0, 0, 0                # Case 1
            
            elif top_dam.lvl_status == 'ok':
                return 1, 0, 0                # Case 2
            
            elif top_dam.lvl_status in ['high', 'full']:
                return 1, 0, 0                # Case 3
            
        elif middle_dam.lvl_status == 'ok':

            if top_dam.lvl_status in ['empty', 'low']:
                return 0, 1, 0                # Case 4
            
            elif top_dam.lvl_status == 'ok':
                return dependant, 1, 0        # Case 5
            
            elif top_dam.lvl_status in ['high', 'full']:
                return 1, 1, 0                # Case 6
            
        elif middle_dam.lvl_status in ['high', 'full']:

            if top_dam.lvl_status in ['empty', 'low']:
                return 0, 1, 0                # Case 7
            
            elif top_dam.lvl_status == 'ok':
                return 0, 1, 0                # Case 8
            
            elif top_dam.lvl_status in ['high', 'full']:
                return 0, 1, 0                # Case 9
            
    elif bottom_dam.lvl_status == 'ok':
        
        if middle_dam.lvl_status in ['empty', 'low']:

            if top_dam.lvl_status in ['empty', 'low']:
                return 0, 0, dependant                # Case 10
            
            elif top_dam.lvl_status == 'ok':
                return 1, 0, dependant                # Case 11
            
            elif top_dam.lvl_status in ['high', 'full']:
                return 1, 0, dependant                # Case 12
            
        elif middle_dam.lvl_status == 'ok':

            if top_dam.lvl_status in ['empty', 'low']:
                return 0, dependant, dependant        # Case 13
            
            elif top_dam.lvl_status == 'ok':
                return dependant, dependant, dependant# Case 14
            
            elif top_dam.lvl_status in ['high', 'full']:
                return 1, dependant, dependant        # Case 15
            
        elif middle_dam.lvl_status in ['high', 'full']:

            if top_dam.lvl_status in ['empty', 'low']:
                return 0, 1, dependant                # Case 16
            
            elif top_dam.lvl_status == 'ok':
                return 0, 1, dependant                # Case 17
            
            elif top_dam.lvl_status in ['high', 'full']:
                return 0, 1, dependant                # Case 18
            
    elif bottom_dam.lvl_status in ['high', 'full']:
        
        if middle_dam.lvl_status in ['empty', 'low']:

            if top_dam.lvl_status in ['empty', 'low']:
                return 0, 0, 1                # Case 19
            
            elif top_dam.lvl_status == 'ok':
                return 1, 0, 1                # Case 20
            
            elif top_dam.lvl_status in ['high', 'full']:
                return 1, 0, 1                # Case 21
            
        elif middle_dam.lvl_status == 'ok':

            if top_dam.lvl_status in ['empty', 'low']:
                return 0, 0, 1                # Case 22
            
            elif top_dam.lvl_status == 'ok':
                return dependant, 0, 1        # Case 23
            
            elif top_dam.lvl_status in ['high', 'full']:
                return 1, 0, 1                # Case 24
            
        elif middle_dam.lvl_status in ['high', 'full']:

            if top_dam.lvl_status in ['empty', 'low']:
                return 0, 0, 1                # Case 25
            
            elif top_dam.lvl_status == 'ok':
                return 0, 0, 1                # Case 26
            
            elif top_dam.lvl_status in ['high', 'full']:
                return 0, 0, 1                # Case 27
            
    else:
        warnings.warn('Algorithm not able to find valid case, all valves recommended 0.')
        return 0, 0, 0