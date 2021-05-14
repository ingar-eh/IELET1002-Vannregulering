# Code
import json
import os
import pandas
from pathlib import Path
from asyncio import sleep

# Import default websocket conection instance
from channels.generic.websocket import AsyncJsonWebsocketConsumer


# Global variable ----------
timeout = 0.5
# Get curent working directory
cwd = os.getcwd() # Get the current working directory (cwd)
# Get the MAIN directory
rootDir = Path(cwd).parent
# Get the data directory
dataDir = f"{rootDir}/DataBehandling/Data/" 


"""
Make a object that is used to store menu state
"""
class menu:
    nr = ""

menu1 = menu()
menu2 = menu()
menu1.nr = "10min"
menu2.nr = "24h"


"""
Create a instance that inherits from AsyncJsonWebsocketConsumer
This creates a websocket conection betwene server and clinet that can handle loads of information transferr simultaniously
"""
class graphLevel(AsyncJsonWebsocketConsumer):
    """
    This method will define wat will happen when you get a conection to a user passed down
    self is just itself object, the class gets a user conection as a object
    When the user is conected acept the conection
    "async def connect" is a inbuilt method in AsyncJsonWebsocketConsumer object
    We change the method in AsyncJsonWebsocketConsumer, and overide it to modify what is inside the method

    We await for a respons from the user conection to syncronise the conection
    We need to wait before the signal is acepted and cunfirmed
    If the conection confirmation takes to long cut the conection and move on 
    """
    async def connect(self):
        # Wait and accept the inncoming connection
        await self.accept()

        # Endless loop
        while True:
            # Variables -----
            level1 = {
                "height": [],
                "time": []
            }
            level2 = {
                "height": [],
                "time": []
            }
            level3 = {
                "height": [],
                "time": []
            }
            prices = {
                "prices": [],
                "time": []
            }

            # Get data frame
            df = pandas.read_csv(dataDir + "Readings.csv", sep="\\t")

            # Function -----
            async def getTime(menuObject):
                # Get latest time
                time0 = list(map(int, df["Time"][len(df) - 1].split(":")))
                date0 = list(map(int, df["Date"][len(df) - 1].split("-")))

                # Get time
                timeListLocal = []

                for i in range(len(df) - 1, 0, -1):
                    # Get data
                    timeNow = list(map(int, df["Time"][i].split(":")))
                    dateNow = list(map(int, df["Date"][i].split("-")))
                    #print(date0, dateNow)

                    # Calculate in unit hh/mm/ss
                    year = date0[0] - dateNow[0]
                    month = date0[1] - dateNow[1]
                    day = date0[2] - dateNow[2]

                    h = time0[0] - timeNow[0] + (year * 9125 + month * 730 + day * 24)
                    m = time0[1] - timeNow[1]
                    s = time0[2] - timeNow[2]
                    #print("Date: ", year, month, day)
                    #print("Time: ", h, m, s)

                    # Calculate in seconds
                    if menuObject.nr == "1min":
                        timeDelta = h * 3600 + m * 60 + s

                        # Check if time fits in
                        if timeDelta <= 60.0:
                            timeListLocal += [str(round(timeDelta, 2)) + " s"]
                    # Calculate in minutes
                    elif menuObject.nr == "10min":
                        timeDelta = h * 60 + m + s/60

                        # Check if time fits in
                        if timeDelta <= 10.0:
                            timeListLocal += [str(round(timeDelta, 2)) + " min"]
                    # Calculate in minutes
                    elif menuObject.nr == "1h":
                        timeDelta = h * 60 + m + s/60

                        # Check if time fits in
                        if timeDelta <= 60.0:
                            timeListLocal += [str(round(timeDelta, 2)) + " min"]
                    # Calculate in hours
                    elif menuObject.nr == "24h":
                        timeDelta = h + m/60 + s/3600

                        # Check if time fits in
                        if timeDelta <= 24.0:
                            timeListLocal += [str(round(timeDelta, 2)) + " h"]
                    # Calculate in hours
                    elif menuObject.nr == "ALL":
                        timeListLocal += [str(round((h + m/60 + s/3600), 2)) + " h"]

                return timeListLocal

            # Wait til you get time
            timeList1 = await getTime(menu1)
            timeList2 = await getTime(menu2)

            # Sort data for level height
            for i in range(len(df) - len(timeList1), len(df)):
                # Level 1
                level1["height"] += [str(df["Level1"][i])]
                                
                # Level 2
                level2["height"] += [str(df["Level2"][i])]

                # Level 3
                level3["height"] += [str(df["Level3"][i])]
                
            """
            Give time data for level graphs
            We use reversed for loop because we calculated values backwards
            """
            for t in reversed(timeList1):
                level1["time"] += [t]
                level2["time"] += [t]
                level3["time"] += [t]


            # Sost data for prices
            for i in range(len(df) - len(timeList2), len(df)):
                prices["prices"] += [str(df["Price"][i])]

            # Give time data for price graph
            for t in reversed(timeList2):
                prices["time"] += [t]

            """
            Send data back to the other side of the conection as string
            package it as json file
            Wait for response
            """
            data = {
                "level1": level1,
                "level2": level2,
                "level3": level3,
                "prices": prices
            }
            await self.send(json.dumps(data))

            # Wait and sleep for 1 second
            await sleep(timeout)


# Recomendation graph websocket insatnce
class recomend(AsyncJsonWebsocketConsumer):
    # On first conect
    async def connect(self):
        # Wait and accept the inncoming connection
        await self.accept()

        # Endless loop
        while True:
            # Get data frame
            df = pandas.read_csv(dataDir + "Readings.csv", sep="\\t")

            # Get latest recomendations Re1 Re2 Re3"
            recommendation1 = float(df["Recommendation1"][len(df) - 1])
            recommendation2 = float(df["Recommendation2"][len(df) - 1])
            recommendation3 = float(df["Recommendation3"][len(df) - 1]) # DELETE The last value is special because it was saved as a string with extra " at the end, and so we need to get rid of the " BASICALY: A smal bug XD

            # Set values inside data
            data = {
                "recommend1": recommendation1,
                "recommend2": recommendation2,
                "recommend3": recommendation3
            }

            # send data to client
            await self.send(json.dumps(data))

            # Wait and sleep for 1 second
            await sleep(timeout)


# Send control state (manual[1]/auto[0]) mode
class controlState(AsyncJsonWebsocketConsumer):
    # Send iformation
    async def connect(self):
        # Acept the client conection
        await self.accept()

        # Endless lopp
        while True:
            # Get data frame
            df = pandas.read_csv(dataDir + "Readings.csv", sep="\\t")

            # Get latest state of controll
            controlState1 = str(df["ESP_control1"][len(df) - 1])
            controlState2 = str(df["ESP_control2"][len(df) - 1])
            controlState3 = str(df["ESP_control3"][len(df) - 1])

            # Set values inside data
            data = {
                "controlState1": controlState1,
                "controlState2": controlState2,
                "controlState3": controlState3
            }

            # send data to client
            await self.send(json.dumps(data))

            # Wait and sleep for 1 second
            await sleep(timeout)



    pass


"""
Receive data from user
Receive button states and alocate signal comands to the right place in data "SCADA.txt" file
"""
class receiveButtonState(AsyncJsonWebsocketConsumer):
    """
    Inbuilt method in AsyncJsonWebsocketConsumer
    Alows to receive data from the client side
    """
    async def receive(self, text_data):
        # Variables
        dataOld = ""
        dataNew = "1" # Have 1 at the start to indicate that client is conected and asking for controll
        buttonName = text_data[1:-2]
        buttonNumber = int(text_data[-2])

        # Get data
        with open(cwd + "/VMB_GUSTAV/data/SCADA.txt", "+r") as file:
            dataOld = str(file.readline())

        """
        Rewrite data acordingly to mesage gottten from client
        If pressed button ON  => 1
        If pressed button OFF => 0
        """
        if buttonName == "buttonON":
            for i in range(1, len(dataOld)):
                if i == buttonNumber:
                    dataNew += "1"
                else:
                    dataNew += dataOld[i]
        else:
            for i in range(1, len(dataOld)):
                if i == buttonNumber:
                    dataNew += "0"
                else:
                    dataNew += dataOld[i]

        # Save new data
        with open(cwd + "/VMB_GUSTAV/data/SCADA.txt", "+w") as file:
           file.write(dataNew)
        
    
    """
    When client disconects from websocket
    Rewrite the control file to everything off including conection value (THe first value)
    """
    async def disconnect(self, code):
        # Rewrite data
        with open(cwd + "/VMB_GUSTAV/data/SCADA.txt", "+w") as file:
           file.write("0000")


# Instance for websocket that handles timeline menu selections for level graphs
class receiveMenuTimeline1(AsyncJsonWebsocketConsumer):
    # Receive a signal and edit menu variable to be that signal
    async def receive(self, text_data):
        menu1.nr = text_data[1:-1].split("-")[1]


# Instance for websocket that handles timeline menu selections for price graphs
class receiveMenuTimeline2(AsyncJsonWebsocketConsumer):
    # Receive a signal and edit menu variable to be that signal
    async def receive(self, text_data):
        menu2.nr = text_data[1:-1].split("-")[1]

