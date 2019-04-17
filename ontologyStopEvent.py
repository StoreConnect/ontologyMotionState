from Point import GPSPoint
import math
import sendDataToApiOntology
import datetime

s= 0.5
speedAccuracy= 0.1
orientationAccuracy= 10

tabDegrees= []
tabDegrees2= []

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

def ontologyPorcessing(dataDict, store):

    print "Ontology processing..."

    fusedTraj = {}

    for object in dataDict:
        fusedTraj[object] = {}
        fusedTraj[object]["trajectory"] = []
        fusedTraj[object]["sensor"] = dataDict[object]["sensor"]
        points= []
        #reduction de l'echantillonnage
        first_point= dataDict[object]["trajectory"][0]
        point = GPSPoint();
        point.long = first_point[1][0]
        point.lat = first_point[1][1]
        point.timestamp = first_point[0]
        points.append(point)
        for p in dataDict[object]["trajectory"]:
            if (p[0] - first_point[0]) >= datetime.timedelta(seconds=1):
                point = GPSPoint()
                point.long = p[1][0]
                point.lat = p[1][1]
                point.timestamp= p[0]
                points.append(point)
                first_point = p

        # points lisses
        mPoints = []
        # distance entre deux points lisses
        distance = []
        mDistance = []
        mTemps = []
        temps= []
        # Recuperation et lissage des points
        i = 0
        for point in points:
            # Lissage des points et acquisition des distances et deltaT
            fusedTraj[object]["trajectory"].append([])
            index = points.index(point)
            coordinates = []
            if (index + 1 < len(points)):

                pAfter = points[index + 1]

                # calcul de l'azimut (orientation) avec les valeurs brutes
                x = math.cos(point.lat) * math.sin(pAfter.lat) - math.sin(point.lat) * math.cos(pAfter.lat) * math.cos(
                    pAfter.long - point.long)
                y = math.sin(pAfter.long - point.long) * math.cos(pAfter.lat)
                azimut = math.atan2(y, x)
                degrees = math.degrees(azimut) + 180
                # print degrees
                tabDegrees.append(degrees)

                if (index - 1 >= 0):
                    pBefore = points[index - 1]

                    medianePoint = mediane(pBefore, point, pAfter)

                    fusedTraj[object]["trajectory"][index].append(medianePoint.timestamp)

                    mPoints.append(medianePoint)
                    coordinates.append(medianePoint.long)
                    coordinates.append(medianePoint.lat)
                    mIndex = mPoints.index(medianePoint)
                    mBefore = mPoints[mIndex - 1]
                    deltaD = mBefore.distanceTo(medianePoint)
                    distance.append(deltaD)

                    medianePoint.deltaT = (medianePoint.timestamp - pBefore.timestamp).total_seconds()
                    temps.append(medianePoint.deltaT)
                else:
                    coordinates.append(point.long)
                    coordinates.append(point.lat)
                    mPoints.append(point)
                    distance.append(0)
                    temps.append(0)
                    fusedTraj[object]["trajectory"][index].append(point.timestamp)

                fusedTraj[object]["trajectory"][index].append(coordinates)

            else:
                coordinates.append(point.long)
                coordinates.append(point.lat)
                fusedTraj[object]["trajectory"][index].append(point.timestamp)
                fusedTraj[object]["trajectory"][index].append(coordinates)
                mPoints.append(point)
                distance.append(0)
                temps.append(0)
            i += 1

        i = 0
        # calcul de l'azimuth avec les points lisses
        for point in mPoints:
            index = mPoints.index(point)
            if (index + 1 < len(mPoints)):
                pAfter = mPoints[index + 1]

                x = math.cos(point.lat) * math.sin(pAfter.lat) - math.sin(point.lat) * math.cos(
                    pAfter.lat) * math.cos(
                    pAfter.long - point.long)
                y = math.sin(pAfter.long - point.long) * math.cos(pAfter.lat)
                azimut = math.atan2(y, x)
                degrees = math.degrees(azimut) + 180

                # calcul de l'azimuth accuracy
                oldDegree = tabDegrees[i]
                diff = abs(degrees - oldDegree)
                diffMin = min(diff, 360 - diff)

                if diffMin > orientationAccuracy:
                    percent = orientationAccuracy / diffMin
                else:
                    percent = 1.0
            else:
                degrees = 0
                percent = 0
            fusedTraj[object]["trajectory"][i].append(degrees)
            fusedTraj[object]["trajectory"][i].append(percent)
            i += 1

        # lissage des distances
        for d in distance:
            index = distance.index(d)
            if (index - 1 >= 0 and index + 1 < len(distance)):
                dBefore = distance[index - 1]
                dAfter = distance[index + 1]
                medianeDistance = medianeF(dBefore, d, dAfter)
                mDistance.append(medianeDistance)
            else:
                mDistance.append(d)

        for t in temps:
            index = temps.index(t)
            if (index - 1 >= 0 and index + 1 < len(temps)):
                tBefore = temps[index - 1]
                tAfter = temps[index + 1]
                medianeTemps = medianeF(tBefore, t, tAfter)
                mTemps.append(medianeTemps)
            else:
                mTemps.append(t)

        vitesses = []
        mVitesse = []

        i = 0
        for t in mTemps:
            d = mDistance[i]
            if (t != 0):
                v = d / t
            else:
                v = 0
            vitesses.append(v)
            i += 1

        i = 0
        for v in vitesses:
            index = vitesses.index(v)
            if (index - 1 >= 0 and index + 1 < len(vitesses)):
                vBefore = vitesses[index - 1]
                vAfter = vitesses[index + 1]
                medianeVitesse = medianeF(vBefore, v, vAfter)
                mVitesse.append(medianeVitesse)
            else:
                medianeVitesse = v
                mVitesse.append(v)
            fusedTraj[object]["trajectory"][i].append(medianeVitesse)

            if medianeVitesse <= s:
                moveState = "Stopping"
            else:
                moveState = "Walking"
            fusedTraj[object]["trajectory"][i].append(moveState)
            #print dataDict[object]["trajectory"][i]

            # calcul du pourcentage de la speedAccuracy de la vitesse
            dist = abs(v - medianeVitesse)
            if (dist >= speedAccuracy):
                percent = speedAccuracy / dist
            else:
                percent = 1.0
            fusedTraj[object]["trajectory"][i].append(percent)
            i += 1

    sendDataToApiOntology.sendData(fusedTraj, store)