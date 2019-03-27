import getDataFromApiOntology
from Point import GPSPoint
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta

s= 0.5

sensors= []
def medianeF(f1, f2, f3):
    f= [f1, f2, f3]
    return (max(f) + min(f))/2

def mediane(p1, p2, p3):
    lat= [p1.lat, p2.lat, p3.lat]
    long= [p1.long, p2.long, p3.long]
    minLat= min(lat)
    maxLat= max(lat)
    minLong= min(long)
    maxLong= max(long)

    mediane= GPSPoint()
    mediane.lat= (minLat+maxLat)/2
    mediane.long= (minLong+maxLong)/2
    mediane.timestamp= p2.timestamp

    return mediane

def main():
    sensors= getDataFromApiOntology.getData()

    sensor= sensors.items()[0]
    i= 0
    x=[]
    x1=[]
    x2=[]
    temps=[]
    vitesse=[]
    lat1= []
    lat2= []
    #for sensor in sensors.items():
    for person in sensor[1].items():
        #points lisses
        mPoints= []
        #distance entre deux points lisses
        distance= []
        mDistance=[]
        mTemps= []
        #Recuperation et lissage des points
        i= 0
        for point in person[1]:
            points= person[1]

            #Lissage des points et acquisition des distances et deltaT
            index= points.index(point)
            if((index-1 >= 0) and (index+1 < len(points))):

                pBefore= points[index-1]
                pAfter= points[index+1]

                medianePoint=  mediane(pBefore, point,  pAfter)
                mPoints.append(medianePoint)

                mIndex= mPoints.index(medianePoint)
                mBefore= mPoints[mIndex-1]
                deltaD= mBefore.distanceTo(medianePoint)
                distance.append(deltaD)

                medianePoint.deltaT= (medianePoint.timestamp - pBefore.timestamp).total_seconds()
                temps.append(medianePoint.deltaT)

                x1.append(point.long)
                lat2.append(point.lat)
            else:
                mPoints.append(point)
                distance.append(0)
                temps.append(0)
            x.append(i)
            i= i+1

        i= 0
        '''
        #lissage des distances
        for p in mPoints:
            index= mPoints.index(p)
            x.append(p.long)
            lat1.append(p.lat)
            if(index-1 >= 0):
                pBefore= mPoints[index-1]
                #check the deltaD
                deltaD= pBefore.distanceTo(p)
            else:

            distance.append(deltaD)
        '''
        for d in distance:
            index= distance.index(d)
            if(index-1 >=0 and index+1 < len(distance)):
                dBefore= distance[index-1]
                dAfter= distance[index+1]
                medianeDistance= medianeF(dBefore, d, dAfter)
                mDistance.append(medianeDistance)
            else:
                mDistance.append(d)
            x2.append(i)
            i=i+1

        for t in temps:
            index= temps.index(t)
            if(index-1>=0 and index+1 < len(temps)):
                tBefore= temps[index-1]
                tAfter= temps[index+1]
                medianeTemps= medianeF(tBefore, t, tAfter)
                mTemps.append(medianeTemps)
            else:
                mTemps.append(t)

        i=0
        vitesses=[]
        mVitesse= []
        for t in mTemps:
            d= mDistance[i]
            if(t != 0):
                v= d/t
            else:
                v= 0
            print("%.4f - %0.4f - %0.4f" % (d, t, v))
            vitesses.append(v)
            i= i+1

        for v in vitesses:
            index= vitesses.index(v)
            if(index-1>=0 and index+1 < len(vitesses)):
                vBefore= vitesses[index-1]
                vAfter= vitesses[index+1]
                medianeVitesse= medianeF(vBefore, v, vAfter)
                mVitesse.append(medianeVitesse)
            else:
                mVitesse.append(v)

        seuil= []
        for l in x2:
            seuil.append(s)




        #plt.title(person[0])
        plt.title("Trajectory")
        #plt.plot(x, temps)
        #plt.plot(x, vitesse)
        #plt.plot(x, distance)
        plt.plot(x1, lat2)
        #plt.plot(x, lat1)
        #plt.savefig('deltaT.png')
        plt.show()

        plt.title("Delta time")
        plt.plot(x, temps)
        plt.plot(x, mTemps)
        #plt.savefig('pos.png')
        plt.show()

        plt.title("Delta distance")
        plt.plot(x2, distance)
        plt.plot(x2, mDistance)
        #plt.savefig('pos.png')
        plt.show()

        plt.title("Vitesse")
        #plt.plot(x2, mTemps)
        #plt.plot(x2, mDistance)
        plt.plot(x2, vitesses)
        plt.plot(x2, mVitesse)
        plt.plot(x2, seuil)
        #plt.savefig('pos.png')
        plt.show()


if __name__ == '__main__':
    main()
