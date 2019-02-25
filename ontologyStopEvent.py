import getDataFromApiOntology
from Point import Point3D
import numpy as np
import matplotlib.pyplot as plt

sensors= []
stopedPoints= []

def lissage(Lx,Ly,p):
    Lxout=[]
    Lyout=[]
    Lxout = Lx[p: -p]
    for index in range(p, len(Ly)-p):
        average = np.mean(Ly[index-p : index+p+1])
        Lyout.append(average)
    return Lxout,Lyout

def main():
    sensors= getDataFromApiOntology.getData()

    sensor= sensors.items()[0]
    i= 0
    #for sensor in sensors.items():
    for person in sensor[1].items():
        lat= []
        long= []
        for point in person[1]:
            '''
            points= person[1]
            index= points.index(point)
            #print "%s - %s - %s" % (sensor[0], person[0], point.timestamp)
            if(index-1 >= 0):
                pBefore= points[index-1]

                #check the deltaT
                deltaT= (point.timestamp - pBefore.timestamp).total_seconds()
                #check deltaD
                if(deltaT <= 2 and deltaT >= 0.1):
                    deltaD = pBefore.distanceTo(point)
                    #check vitesse
                    v= deltaD / deltaT

                    print 'P1: %.12f - %.12f - %s' % (pBefore.lat, pBefore.long, pBefore.timestamp.ctime())
                    print 'P2: %.12f - %.12f - %s' % (point.lat, point.long, point.timestamp.ctime())
                    print 'm: %.3f - t: %.3f - v: %.3f' %(deltaD, deltaT, v)

                    #x.append(i)
                    i= i+1
                    vList.append(v)
                '''
            lat.append(point.lat)
            long.append(point.long)

        x, y = lissage(lat, long, 20)
        points= []
        for i in range(len(x)):
            p= GPSPoint()
            p.lat= x[i]
            p.long= y[i]
            points.append(p)
            #width = 1.0
            #plt.bar(x, deltaDList, width, color='b')

        '''
        plt.title(person[0])
        plt.plot(x, y)
        plt.savefig('pos.png')
        plt.show()

        plt.title(person[0])
        plt.plot(x2, y)
        plt.savefig('pos.png')
        plt.show()
        '''


if __name__ == '__main__':
    main()
