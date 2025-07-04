import requests
import json
from datetime import datetime
from datetime import timedelta
import pytz
import math
import os
from dotenv import load_dotenv

load_dotenv('variables.env')

url = "https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival"

API_KEY = os.getenv('DATAMALL_API_KEY')

params = {
    "BusStopCode": "50199"
}

headers = {
    "AccountKey": API_KEY
}

response = requests.get(url, headers=headers, params=params)

if (response.status_code == 200):
    data = response.json()
    # print(json.dumps(data, indent=2))
    print("I am in sgarrival.py")
    for service in data["Services"]:
        if (service["ServiceNo"] == "21"):
            # print(service)
            nextBus = service["NextBus"]
            eta_iso = datetime.fromisoformat(nextBus["EstimatedArrival"])
            
            # print(f"now = {datetime.now()}")
            current_time = datetime.now(pytz.timezone('Asia/Singapore'))
            # five_minutes_later = current_time + timedelta(seconds=360)
            # print(five_minutes_later)
            arriving_in = eta_iso - current_time
            seconds_to_arrive = arriving_in.total_seconds()
            mins_to_arrive = math.floor(seconds_to_arrive / 60)
            if (mins_to_arrive < 1):
                print("Bus is Arriving")
            else:
                print(f"Bus is arriving in {mins_to_arrive} mins")

            # if (timeDeltaFirstBus < 360):

            eta_human_readable = datetime.strftime(eta_iso, '%I:%M%p')
            if (eta_human_readable.startswith('0')):
                eta_human_readable = eta_human_readable.replace('0','',1)
            print(eta_human_readable)
else: 
    print(f"Error: {response.status_code}")
