import requests
import json
from datetime import datetime
from datetime import timedelta
import pytz
import math
import os
from dotenv import load_dotenv

# i need a bus code first
# after i get a bus code, then i need the buses
# after the buses, the i can return a 5 minute timerr 

load_dotenv('variables.env')

API_KEY = os.getenv('DATAMALL_API_KEY')

url = "https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival"


def getBusArrivalResponse(busStopCode, busServiceNo, API_KEY):
    # returns the response from the call request
    headers = {
        "AccountKey": API_KEY
    }
    params = {
        "BusStopCode": busStopCode,
        "ServiceNo": busServiceNo
    }
    response = requests.get(url, headers=headers, params=params)
    if (response.status_code == 200):
        return response # returns the raw response
    else:
        print(f"Error in status code: {response.status_code}")
        return None

def getMinutesToArrival(eta_iso):
    current_time = datetime.now(pytz.timezone('Asia/Singapore'))
    arriving_in = eta_iso - current_time
    
    seconds_to_arrive = arriving_in.total_seconds()
    mins_to_arrive = math.floor(seconds_to_arrive / 60)

    return mins_to_arrive
    

def getBusTiming(response, busStopCode, busServiceNo):
    # response = getBusArrivalResponse(busStopCode, busServiceNo, API_KEY)
    if (response == None):
        print("response was none (from busArrival.py in getBusTiming)")
        return

    data = response.json()

    services = data["Services"]
    if (services == []):
        return f"Bus number {busServiceNo} does not serve this bus stop.\n"

    for service in services:
        if (service["ServiceNo"] == busServiceNo):
            nextBus = service["NextBus"]
            nextBus2 = service["NextBus2"]
            # if (nextBus == "" or nextBus == None):
            #     return "No bus information available"

            eta_iso = datetime.fromisoformat(nextBus["EstimatedArrival"])
            nextBusArrivalTime = getMinutesToArrival(eta_iso)
            eta_iso2 = datetime.fromisoformat(nextBus2["EstimatedArrival"])
            nextBus2ArrivalTime = getMinutesToArrival(eta_iso2) 

            if (nextBusArrivalTime < 1):
                return f"Bus {busServiceNo} is arriving\nNext bus is coming in {nextBus2ArrivalTime} mins.\n"
            else: 
                return f"Bus {busServiceNo} is reaching in {nextBusArrivalTime} mins\nThe next bus is reaching in {nextBus2ArrivalTime} mins.\n"

    return "No bus information available"

def main():
    # print("Im so confused, so the data is being returned in this format?")
    response = getBusArrivalResponse("08079", "129", API_KEY)
    data = response.json()
    if (data != None):
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print("data is none")
    if (data["Services"] == []):
        print("No services indeed")

if __name__ == "__main__":
    main()
