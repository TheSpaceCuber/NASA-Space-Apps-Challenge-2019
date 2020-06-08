import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("Delhi.csv") # read csv file
print(df)

# amend date column to pandas datetime format
df['date'] = df.date.str[37:-7]
df['date'] = pd.to_datetime(df['date'])

df = df.sort_values(by='date',ascending=True) # sort by date

# create dataframes for each pollutant from the main df
df_pm25 = df[df.parameter == 'pm25'] 
df_o3 = df[df.parameter == 'o3'] 
df_co = df[df.parameter == 'co'] 
df_so2 = df[df.parameter == 'so2'] 
df_no2 = df[df.parameter == 'no2'] 
df_pm10 = df[df.parameter == 'pm10'] 

def plot_and_save(df, name):
    # generates and saves a graph from matplot lib
    fig = plt.figure(figsize=(18,7)) # create a figure object and input figure size of 12x8
    plt.plot(df['date'], df['value']) 
    # plt.plot(df_o3['date'], df_o3['value']) 
    # plt.plot(df_co['date'], df_co['value']) 
    # plt.plot(df_so2['date'], df_so2['value']) 
    plt.ylabel("Value (µg/m³)")
    plt.xlabel("Date")
    plt.title(name)
    plt.savefig(name + ".png")
    # plt.show() # removes text on top

# create graphs for each pollutant
plot_and_save(df_pm25, "pm25")
plot_and_save(df_o3, "o3")
plot_and_save(df_co, "co")
plot_and_save(df_so2, "so2")
plot_and_save(df_no2, "no2")
plot_and_save(df_pm10, "pm10")


