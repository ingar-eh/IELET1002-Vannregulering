import pandas as pd

path_hourly = '/home/pi/VMB_Gustav/DataBehandling/Data/HourlyPrices.csv'

df_hourly = pd.read_csv(path_hourly, delimiter='\t', index_col=0)

print(df_hourly)