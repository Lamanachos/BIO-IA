#distances en km temps en s
import random as r
from math import sqrt,inf
import matplotlib.pyplot as plt
import copy as cp
import time as t
import json

def distance(x1,y1,x2,y2):
    return sqrt((x2-x1)**2+(y2-y1)**2)

class Station:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
    
    @classmethod
    def fromJson(cls,fj : list[int]):
        return cls(fj[0],fj[1],fj[2])
    
    def toJson(self):
        return [self.id,self.x,self.y]
    def distanceStat(self, station):
        return distance(self.x,self.y,station.x,station.y)
    def distance(self, x1 : int,y1 : int):
        return distance(self.x,self.y,x1,y1)
    def print(self):
        print("["+str(self.id)+","+str(self.x)+","+str(self.y)+"]")
    
class Line:
    totalLines = 0
    def __init__(self, stations : list[Station], timeInterval,id=None):
        if id == None :
            self.id = Line.totalLines
            Line.totalLines += 1
        else :
            self.id = id
        self.stations = stations
        self.timeInterval = timeInterval
    
    @classmethod
    def fromJson(cls,fj : [list[int],int,int],allStations : list[Station]):
        stations = []
        print(fj)
        for i in fj[0]:
            ind = 0
            for j in range(len(allStations)):
                if allStations[j].id == i:
                    print("hi")
                    ind = j
            stations.append(allStations[ind])
        return cls(stations,fj[1],fj[2])
    
    def toJson(self):
        statsIds = []
        for i in self.stations:
            statsIds.append(i.id)
        return [statsIds,self.timeInterval,self.id]
    def waitTime(self,station,timeStart,actualTime):
        if station in self.stations :
            position = self.stations.index(station)
            firstStop = 0
            for i in range(position):
                firstStop += self.stations[i].distanceStat(self.stations[i+1])*144
            if actualTime > firstStop :
                return (actualTime - firstStop)%self.timeInterval
            else :
                return firstStop - actualTime
    def addStation(self,station):
        self.stations.append(station)

def getMatriceDist(stations,lines : list[Line]):
        mat = []
        for i in range(len(stations)):
            l = []
            for j in range(len(stations)):
                l.append([])
            mat.append(l)
        for line in lines:
            stats = line.stations
            l = len(stats)
            for i in range(l-1):
                id1 = stations.index(stats[i])
                id2 = stations.index(stats[i+1])
                if mat[id1][id2] != []:
                    mat[id1][id2].append(line)
                    mat[id2][id1].append(line)
                else :
                    mat[id2][id1].append(stats[i+1].distanceStat(stats[i]))
                    mat[id1][id2].append(stats[i+1].distanceStat(stats[i]))
                    mat[id2][id1].append(line)
                    mat[id1][id2].append(line)
        return mat

class City:
    def __init__(self, stations : list[Station], lines : list[Line]):
        self.stations = stations
        self.matriceDist = getMatriceDist(stations,lines)
        self.lines = lines

    @classmethod
    def fromJson(cls,fjStations,fjLines):
        stations = []
        lines = []
        for i in fjStations:
            stations.append(Station.fromJson(i))
        for i in fjLines:
            lines.append(Line.fromJson(i,stations))
        return cls(stations,lines)

    def toJson(self):
        jLines = []
        jStations = []
        for i in self.stations:
            jStations.append(i.toJson())
        for i in self.lines:
            jLines.append(i.toJson())
        return jStations,jLines
    def addStation(self,station):
        self.stations.append(station)
    def addLine(self,line : Line):
        for station in line.stations :
            if station not in self.stations :
                self.stations.append(station)
        self.lines.append(line)
        self.setMatriceDist()
    def addLines(self, lines : list[Line]):
        for i in lines :
            self.addLine(i)
        self.setMatriceDist()
    def setLines(self, lines):
        self.lines = lines
        self.setMatriceDist()
    def setMatriceDist(self):
        self.matriceDist = getMatriceDist(self.stations,self.lines)
    def print(self):
        for i in self.stations:
            i.print()
    def plot(self):
        xs = []
        ys = []
        for i in self.stations:
            xs.append(i.x)
            ys.append(i.y)
        for line in self.lines:
            lx,ly = [],[]
            for station in line.stations:
                lx.append(station.x)
                ly.append(station.y)
            plt.plot(lx,ly,label = line.id)
        plt.scatter(xs,ys)
        plt.legend()
        plt.show()
    def Dijkstra(self,xstart,ystart,xend,yend,tstart,tstartSim):
        tabDijkstra = []
        tabLine = []
        for i in self.stations:
            dist = i.distance(xstart,ystart)
            tabDijkstra.append(dist*720)#en moyenne un humain met 720s à faire 1km
            tabLine.append("Walk")
        tabDijkstra.append(distance(xstart,ystart,xend,yend)*720)
        tabLine.append("Walk")
        minIndex = tabDijkstra.index(min(tabDijkstra))
        previousMins = [minIndex]
        tabDijkstras = [tabDijkstra.copy()]
        tabLines = [tabLine.copy()]
        while minIndex != len(tabDijkstra)-1 :
            ts = tabDijkstra[minIndex]
            #print("tab : ",tabDijkstra)
            #print("minIndex : ",minIndex)
            #print("ts : ",ts)
            matDists = self.matriceDist[minIndex]
            #print("matDists : ",matDists)
            for j in range(len(matDists)):
                if matDists[j] != []:
                    #print("j : ",j)
                    for line in matDists[j][1:]:
                        temp = line.waitTime(self.stations[j],tstartSim,tabDijkstra[minIndex]+tstart)
                        if tabDijkstra[j] > temp + ts + (matDists[j][0])*144:
                            tabDijkstra[j] = temp + ts + (matDists[j][0])*144
                            tabLine[j] = line.id
            distEnd = self.stations[minIndex].distance(xend,yend)*720 + ts
            if distEnd < tabDijkstra[-1]:
                tabDijkstra[-1] = distEnd
            tempmin = inf
            tempminIndex = -1
            for i in range(len(tabDijkstra)):
                if (tabDijkstra[i]<tempmin) and (i not in previousMins):
                    tempmin = tabDijkstra[i]
                    tempminIndex = i
            minIndex = tempminIndex
            previousMins.append(minIndex)
            tabDijkstras.append(tabDijkstra.copy())
            tabLines.append(tabLine.copy())
        #get the clean way
        stops = []
        point = tabDijkstras[-1][-1]
        pointIndex = -1
        l = len(tabDijkstras)
        for i in range(1,l+1):
            #print("point : ",point)
            #print("pointIndex : ",pointIndex)
            #print("tab : ",tabDijkstras[l-i])
            currDist =  tabDijkstras[l-i][pointIndex]
            if  currDist != point :
                pointIndex = previousMins[l-i]
                point = tabDijkstras[l-i][pointIndex]
                stops.insert(0,[point,pointIndex])
        stops.insert(0,[0,"Start"])
        stops.append([tabDijkstra[-1],"End"])
        steps = []
        for i in range(0,len(stops)-1):
            timestep = stops[i+1][0]-stops[i][0]
            if (i != 0) and (i != len(stops)-2):
                wait = timestep - self.matriceDist[stops[i+1][1]][stops[i][1]][0]*144
                steps.append(["Wait",wait])
                timestep = timestep - wait
            nextStat = stops[i+1][1]
            if nextStat != "End":
                steps.append([str(stops[i][1])+" to "+str(stops[i+1][1]) + " with " + str(tabLines[-1][stops[i+1][1]]),timestep])
            else :
                steps.append([str(stops[i][1])+" to "+str(stops[i+1][1]) + " with Walk",timestep])
        return tabDijkstra[-1],steps
    def test(self,tstart,tend,nbTrips):
        tot = 0
        nbTot = 0
        for i in range(nbTrips):
            xstart = r.random()*10
            ystart = r.random()*10
            xend = r.random()*10
            yend = r.random()*10
            dij = self.Dijkstra(xstart,ystart,xend,yend,tstart+(tend-tstart)*i/nbTrips,0)
            tot += dij[0]
            nbTot += 1
        return tot/nbTot


def generateStations(nb_stations,minx,maxx,miny,maxy):
    stations = []
    for i in range(nb_stations):
        stations.append(Station(i,r.random()*(maxx-minx)+minx,r.random()*(maxy-miny)+miny))
    return stations

def generateLines(stations,nbLines,minLenLines,maxLenLines,timeInterval):
    lines = []
    nbStations = len(stations)
    stationsLeft = cp.copy(stations)
    for i in range(nbLines):
        line = Line([],timeInterval) 
        j = r.randint(minLenLines,maxLenLines)
        tempStats = stations.copy()
        for k in range(j):
            stat = tempStats[r.randint(0,len(tempStats)-1)]
            if stat in stationsLeft :
                stationsLeft.remove(stat)
            line.addStation(stat)
            tempStats = stations.copy()
            tempStats.remove(stat)
        lines.append(line)
    for i in stationsLeft:
        j = r.randint(0,nbLines-1)
        lines[j].addStation(i)
    return lines

def generateCity(nb_stations,minx,maxx,miny,maxy,nbLines,minLenLines,maxLenLines,timeInterval):
    stations = generateStations(nb_stations,minx,maxx,miny,maxy)
    lines = generateLines(stations,nbLines,minLenLines,maxLenLines,timeInterval)
    return City(stations,lines)


""" stations = [Station(0,0,0),Station(2,0,1),Station(1,0,2)]
lines = [Line(stations,180)]
city = City(stations,lines) """
""" start = t.time()
city = generateCity(300,0,10,0,10,16,15,25,180)
print(t.time()-start)
start = t.time()
#dij = city.Dijkstra(0,0,10,10,0,10000)
#print(dij[4])
test = city.test(10000,10002,100)
print(test)
city.setLines(generateLines(city.stations,16,15,25,180))
test = city.test(10000,10002,100)
print(test)
print(t.time()-start) """
stations = [Station(0,0,0),Station(2,1,1),Station(1,0,2)]
lines = [Line(stations,180)]
city = City(stations,lines)
#city.plot()
jstats,jlines = city.toJson()
with open("./cities/city1_stations.json", "w") as city_file:
    json.dump(jstats, city_file, indent=4)

with open("./cities/city1_lines.json", "w") as city_file:
    json.dump(jlines, city_file, indent=4)

with open("./cities/city1_stations.json", "r") as city_file:
    stations = json.load(city_file)

with open("./cities/city1_lines.json", "r") as city_file:
    lines = json.load(city_file)

city = City.fromJson(stations,lines)
city.plot()