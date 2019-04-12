# -*- coding: utf-8 -*-

import sparql
import sys
import datetime 
import time

### Live database ###

login = 'storeconnect'
password = '**************' #changeit

endpointQuery = 'http://apiontologie.westeurope.cloudapp.azure.com:8890/strabon/Query'
endpointUpdate = 'http://apiontologie.westeurope.cloudapp.azure.com:8890/strabon/Update'

### Local database ###

#login = 'update'
#password = 'changeit'

#endpointQuery = 'http://localhost:8890/strabon/Query'
#endpointUpdate = 'http://localhost:8890/strabon/Update'

serviceGet = sparql.Service(endpointQuery, "utf-8", "GET")
servicePost = sparql.Service(endpointUpdate, "utf-8", "POST") 

serviceGet.authenticate(login, password) 
servicePost.authenticate(login, password)   

queryHeaders = """
    PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
    PREFIX sosa: <http://www.w3.org/ns/sosa/>
    PREFIX time: <http://www.w3.org/2006/time#>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX sc: <http://storeconnect/>
    BASE <http://example.org/data/>
"""

#query = """
    #SELECT *
    #WHERE { 
        #?s ?p ?o   
    #}
    #"""

def deleteObject(idObj) :
    
    query = queryHeaders+ """
    DELETE {{ ?a ?b ?c }} WHERE {{
     ?a ?b ?c .
     filter contains(str(?a),"{idobj}")
    }};

    DELETE {{ ?a ?b ?c }} WHERE {{
     ?a ?b ?c .
     filter contains(str(?c),"{idobj}")
    }}
    """.format(idobj=idObj)
    
    result = servicePost.query(query)

def sendStore(store) :

    query = queryHeaders + """
    INSERT DATA {{
        <Store/{store}> rdf:type sc:Store ;
            rdfs:label "Tests in {store} Location" .
    }}
    """.format(store=store)
    
    result = servicePost.query(query)

def sendCameraSensor(idCam) :
    
    query = queryHeaders+ """
    INSERT DATA {{
        <Camera/Cam{idcam}> rdf:type sc:Camera ;
            rdfs:label "Camera {idcam}"@en ;
            rdfs:comment "Camera - @Id={idcam}"@en ;
            sosa:hosts <VideoTracker/Tracker{idcam}> .
        
        <VideoTracker/Tracker{idcam}> a sc:VideoTracker ;
            rdfs:label "Video Tracker {idcam}"@en ;
            sosa:observes sc:Motion .
    }}
    """.format(idcam=idCam)
    
    result = servicePost.query(query)
    
def sendBleSensor(idBle) :
    
    query = queryHeaders+ """
    INSERT DATA {{
        <BleBeacon/Beacon{idble}> rdf:type sc:BleBeacon ;
            rdfs:label "Beacon {idble}"@en ;
            rdfs:comment "Beacon - @Id={idble}"@en ;
            sosa:hosts <BleTracker/Tracker{idble}> .
        
        <BleTracker/Tracker{idble}> a sc:BleTracker ;
            rdfs:label "BLE Tracker {idble}"@en ;
            sosa:observes sc:Motion .
    }}
    """.format(idble=idBle)
    
    result = servicePost.query(query)    
    
def sendData(dataDict, store) :
    sendStore(store)
    
    for idObject in dataDict :
        
        idSensor = "UNKNOWN"
        
        if "cam" in dataDict[idObject]["sensor"].lower() :
            idSensor =  dataDict[idObject]["sensor"].lower().split("cam")[1]
            sendCameraSensor(idSensor)
        elif "geolys" in dataDict[idObject]["sensor"].lower() :
            idSensor =  dataDict[idObject]["sensor"].lower().split("geolys")[1]
            sendBleSensor(idSensor)
        
        
        query = queryHeaders+ """
        INSERT DATA {
        """
        
        query += """
                <MotionSubject/{subjectid}> rdf:type sc:MotionSubject .
            """.format(subjectid = idObject)
            
        ts = datetime.datetime.now()
        counter = int(time.mktime(ts.timetuple()))
        
        for point in dataDict[idObject]["trajectory"]:

            #print point
            
            query += """
            <Observation/{observationid}> rdf:type sosa:Observation ;
                sosa:observedProperty sc:Motion ;
                sosa:hasFeatureOfInterest  <Store/Ubudu> ;
                sosa:madeBySensor <VideoTracker/Tracker{trackerid}> ;
                sosa:hasResult [
                    rdf:type sc:MotionEvent ;
                    sc:hasMotionSubject <MotionSubject/{subjectid}> ;
                    sc:hasMotionState [
                        rdf:type sc:{motionState} ;
                    ];
                    sc:hasOrientation [
                        rdf:type sc:Orientation ;
                        sc:orientation "{orientation}"^^xsd:float ;
                        sc:accuracy "{orientationAccuracy}"^^xsd:float
                    ];
                    sc:hasSpeed [
                        rdf:type sc:Orientation ;
                        sc:speed "{speed}"^^xsd:float ;
                        sc:accuracy "{speedAccuracy}"^^xsd:float
                    ];
                    sc:hasLocation [
                        rdf:type sc:Location ;
                        sc:floor "0"^^xsd:float ;
                        sc:hasPoint [
                            rdf:type geo:Point ;
                            geo:asWKT "POINT({pointLon} {pointLat})"^^geo:wktLiteral
                        ]
                    ]
                ];
                sosa:resultTime [
                    rdf:type time:Instant ;
                    time:inXSDDateTimeStamp "2019-03-20T14:00:00+00:00"^^xsd:dateTimeStamp 
                ] .
            """.format(observationid=str(idObject)+"_"+str(counter),
                       motionState= point[5],
                       orientation= point[2],
                       orientationAccuracy= point[3],
                       speed= point[4],
                       speedAccuracy= point[6],
                       trackerid=idSensor ,
                       subjectid = idObject,
                       pointLon=point[1][0] ,
                       pointLat=point[1][1] ,
                       timestamp=point[0].strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")  ) #%z UTC offset
            
            counter += 1
        
        query += """
        }
        """

        #result = servicePost.query(query,100) # timeout 10 seconds
        servicePost.query(query, 100)  # timeout 10 seconds
        print "Data sent correctly !"

        #for row in result: 
        #    print row
    
    
if __name__ == "__main__":
    # Someone is launching this directly
    sendData({})
    #deleteObject("50c4aa31f3d55bebDUMMY")
    #deleteObject("T5E10.1.0.70-1DUMMY")
