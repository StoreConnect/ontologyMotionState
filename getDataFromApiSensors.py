import requests
from requests.auth import HTTPDigestAuth
import json

from datetime import datetime

dataDict = {}

def getData(date, startTime, endTime) :
    
    url = "http://apicapteur.westeurope.cloudapp.azure.com:8080/SensorThingsService/v1.0/Observations"
    fil = "?$filter=phenomenonTime ge "+date+"T"+startTime+":00.000Z and phenomenonTime le "+date+"T"+endTime+":00.000Z"
    #2018-06-20T08:41:00.000Z and phenomenonTime le 2018-06-20T08:44:00.000Z "
    url += fil
    
    #myResponse = requests.get(url,auth=HTTPDigestAuth(raw_input("username: "), raw_input("Password: ")), verify=True)
    print url
    myResponse = requests.get(url)
    
    hasNext = True
    
    # For successful API call, response code will be 200 (OK)
    while(hasNext) :
        if (myResponse.ok) :
            jData = json.loads(myResponse.content)
            
            for key in jData["value"]:
                observationId = key["result"]["subject"]["id"]
                time = key["phenomenonTime"]
                gps = key["result"]["location"]["geometry"]["coordinates"]
                
                if observationId not in dataDict.keys() :
                    
                    myResponseSensor = requests.get(key["Datastream@iot.navigationLink"])
                    jDataSensor = json.loads(myResponseSensor.content)
                    sensor = jDataSensor["name"]
                    
                    dataDict[observationId] = {}
                    dataDict[observationId]["sensor"] = sensor
                    dataDict[observationId]["trajectory"] = []
                    
                dataDict[observationId]["trajectory"].append( [datetime.strptime(time,"%Y-%m-%dT%H:%M:%S.%fZ" ), [gps[0], gps[1]] ])
                
            if "@iot.nextLink" in jData :
                myResponse = requests.get(jData["@iot.nextLink" ])
            else :
                hasNext = False
                
                    
        else:
          # If response code is not ok (200), print the resulting http error code with description
            myResponse.raise_for_status()

    return dataDict

def main():
    dataDict = getData()
    return dataDict
    

if __name__ == "__main__":
	# Someone is launching this directly
	main()
