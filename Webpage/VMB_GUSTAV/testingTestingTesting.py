import os
import pandas
from pathlib import Path



# Global variables -----
"""
Get current active directory because we need a static directory to save data from the server
"""
# Get the current working directory (cwd)
cwd = os.getcwd()

# Get the MAIN directory
rootDir = Path(cwd).parent

# Get the data directory
dataDir = f"{rootDir}/Databehandling/Data/" 

# Get data
df = pandas.read_csv(dataDir + "Readings.csv", sep="\\t")


controlState1 = int(df["ESP_control1"][len(df) - 1])

print(controlState1)

x = 49

if x > 49:
    print("JAZZZ")
else:
    print("NOOO!")

