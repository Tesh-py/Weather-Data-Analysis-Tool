"""
The below uses an API website to retrieve weather information.
It will retrieve current weather for the chosen city, as well as historical
statistics.

"""
#requests: allows HTTP requests
#json: data transfer on the web
#datetime: allows date conversions
#pandas/numpy: mathematical calculations
import json
from datetime import datetime, timedelta
import requests
import pandas as pd
import numpy as np

print ("You will be prompted to input your city name.")
print ("To exit the city input prompt, please input:\033[1m Done! \033[0m")

#user city input
#if empty,prompted to input again
#Done! exits the request
while True:
    city_input = input("Please input your city name: ").strip()
    if len(city_input) < 1 :
        print("City name cannot be empty, please try again.")
        continue
    if city_input == "Done!":
        exit()
    break


#7 day history statistics
city = city_input.capitalize() #capitalize for neat output
current = datetime.now() #time as at input
current2 = current.strftime("%Y-%m-%d %H:%M:%S")
#date conversions, to ensure format used on API
current3 = current.strftime("%Y-%m-%d")
N = 7 #number of days for history statistics/calcs
hist7 = current - timedelta(days=N) #7 day range calculation
hist7b = hist7.strftime("%Y-%m-%d")

URL1 = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
#no API code required
#first link is used to retrieve longitude/latitude
info = requests.get(URL1, timeout=10) #timeout within 10seconds
#if status code is 200, then the request was successful
#if successful, then the below will retrieve the latitude and longitude
#if not successful, error message
#exceptions for website errors too

try:
    if info.status_code == 200:
        data = info.json()
        if data.get('results'):
            latitude = data['results'][0]['latitude']
            longitude = data['results'][0]['longitude']
            print("City Selected:", city)
            print(f"Latitude: {latitude}, Longitude: {longitude}")
            print("Current Date and Time:", current2)
            print ("Seven Day Date Range:", "from", hist7b, "to", current3)
        else:
            print("City not found. Please ensure correct city has been captured.")
            exit()
    else:
        print(f"Error: {info.status_code}")
        exit()
except (requests.exceptions.RequestException, ValueError, KeyError) as e:
    print(f"An error occurred: {e}")
    exit()

#open-meteo date format of ISO6801, which is yyyy-mm-dd.
#"Start date" is the date 7 days ago and "End date" is now current date
start_date = hist7.strftime("%Y-%m-%d")
end_date = current.strftime("%Y-%m-%d")
URL2 = "https://historical-forecast-api.open-meteo.com/v1/forecast"
#second link is used to retrieve actual weather detail
params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
	        "end_date": end_date,
            "hourly": "temperature_2m",  
            "current_weather": True,          
        }
#the get function will use the parameters above to retrieve the information required
data = requests.get(URL2, params=params, timeout=10) #timeout within 10seconds
#this prompt is to pull current weather temperature in degrees celsius
#temperature unit used in South Africa
#error message if there is no current weather temperature available
#except for website errors too

try:
    if data.status_code == 200:
        weather = data.json()
        print("Current Temperature:", weather["current_weather"]["temperature"], "°C")
    else:
        print("Error: No data available")
        exit()
except (ValueError, KeyError) as ee:
    print(f"An error occurred: {ee}")
    exit()

#create list to store the historical temperatures (only)
#first have to get the hourly info, as to then pull the temperatures
hist_weather = [] #to avoid "possibly used before assignment" error under arr,
#create an empty list for a reference point
try:
    if data.status_code == 200:
        weather = data.json()
        hist_hourly = weather.get("hourly",{})
        hist_weather = hist_hourly.get("temperature_2m",[])
    else:
        print("Error:No history data available")
        exit()
except (ValueError, KeyError) as ee:
    print(f"An error occurred: {ee}")
    exit()

arr = np.array(hist_weather) #create history weather array
ave1 = np.average(arr) #average weather calculation
ave2 = round(ave1, 1)
med1 = np.median(arr) #median weather calculation
med2 = round(med1, 1)
mod1 = pd.Series(arr).mode()
mod_con = mod1.tolist()
#panda series cannot be read in json format,list conversion

print("Seven Day Average Temperature:", ave2,"°C")
print("Seven Day Median Temperature:", med2,"°C")
#ensure no string type info pulling through if there is only one value
if len(mod1) ==1:
    print("Seven Day Mode Temperature/s:", mod1.iloc[0],"°C")
else:
    MOD2 = ", ".join([f"{temp}°C" for temp in mod1])
    print(f"Seven Day Mode Temperatures: {MOD2}")

#output info to save as a JSON document
#saves to folder where you saved .py

output_data = {
     "City Selected": city,
     "Latitude": latitude,
     "Longitude": longitude,
     "Current Date and Time": current2,
     "Seven Day Date Range: Start Date":hist7b, 
     "Seven Day Date Range: End Date":current3,
     "Current Temperature(°C)": weather["current_weather"]["temperature"], 
     "Seven Day Average Temperature(°C)": ave2,
     "Seven Day Median Temperature(°C)": med2,
     "Seven Day Mode Temperature/s(°C)": mod_con,
     }
#ensures json is encoded in UTF-8, else degree symbol does not reflect on text editors
DOC = f"{city}_{current3}_weather.json"
with open(DOC, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=4, ensure_ascii= False)
#ascii=false ensure the degrees celcius does not pull through as \u00b0C on the json document
print(f"Thank you, your JSON document has been saved: {DOC}")
