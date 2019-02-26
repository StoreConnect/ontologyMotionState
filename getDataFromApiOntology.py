import sparql
import re
from rdflib import Literal
from osgeo import ogr
from Point import GPSPoint
import dateutil.parser

### Live database ###
login = 'storeconnect'
password = '************'

endpointQuery = 'http://apiontologie.westeurope.cloudapp.azure.com:8890/strabon/Query'
endpointUpdate = 'http://apiontologie.westeurope.cloudapp.azure.com:8890/strabon/Update'

'''
### Local database ###

login = 'postgres'
password = '********'

endpointQuery = 'http://vps603380.ovh.net:8080/strabon/Query'
#endpointUpdate = 'http://localhost:8890/strabon/Update'
'''

service = sparql.Service(endpointQuery, "utf-8", "POST")

service.authenticate(login, password)

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

def getData():
    query = queryHeaders+ """
        SELECT DISTINCT ?person ?sensor ?point ?t
        WHERE
        {
        	?x rdf:type sosa:Observation .
                ?x sosa:madeBySensor ?sensor .
                ?x sosa:resultTime ?time .
                ?x sosa:hasResult ?r .
                ?r sc:hasMotionSubject ?person .
                ?r sc:hasLocation ?loc .
                ?loc sc:hasPoint ?p .
                ?p rdf:type geo:Point .
                ?p geo:asWKT ?point.
                ?time time:inXSDDateTimeStamp ?t.

        }
        ORDER BY ?t
        """

    list= {}
    result = service.query(query)
    for row in result.fetchone():

        #Sensors
        sensor= row[1].__str__()
        if sensor not in list:
            list[sensor]= {}

        #Persons
        person= row[0].__str__()
        if person not in list[sensor]:
            list[sensor][person]= []

        #Point
        l =  Literal(row[2])
        ogrPoint = ogr.CreateGeometryFromWkt(l.title())
        p = GPSPoint();
        p.long = ogrPoint.GetX()
        p.lat = ogrPoint.GetY()
        l = Literal(row[3])
        d = dateutil.parser.parse(l.title().split(' ')[0])
        p.timestamp = d
        list[sensor][person].append(p)

    return list

if __name__ == '__main__':
    getData()
