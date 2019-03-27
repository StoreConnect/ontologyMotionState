import time
import datetime
import math

_radiusEarth = 6378137 #meters

class Point3D(object):
    def __init__(self):
        self.x= 0
        self.y= 0
        self.z= 0
        self.timestamp= datetime.datetime.now()
        self.state= "Stopping"

    def distanceTo(self, p):
        return math.sqrt(
        (self.x - p.x) * (self.x - p.x) +
        (self.y - p.y) * (self.y - p.y) +
        (self.z - p.z) * (self.z - p.z)
        )

class GPSPoint(object):
    def __init__(self):
        self.lat= 0
        self.long= 0
        self.timestamp= datetime.datetime.now()
        self.deltaT= 0
        self.state= "Stopping"

    def distanceTo(self, p):
        dLat= (self.lat * math.pi / 180) - (p.lat * math.pi / 180)
        dLon= (self.long * math.pi / 180) - (p.long * math.pi / 180)
        a= math.sin(dLat/2) * math.sin(dLat/2) + math.cos(p.lat * math.pi / 180) * math.cos(self.lat * math.pi / 180) * math.sin(dLon/2) * math.sin(dLon/2)
        c= 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d= _radiusEarth * c
        return d

    def toPoint3D(self):
        p= Point3D()
        p.x= _radiusEarth * math.cos(self.long)*math.cos(self.lat)
        p.y= _radiusEarth * math.sin(self.long)*math.cos(self.lat)
        p.z= _radiusEarth * math.sin(self.lat)
        p.timestamp= self.timestamp
        return p
