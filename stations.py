#station : id, x, y
import random as r
from math import sqrt
import matplotlib.pyplot as plt
import copy as cp

def getMatriceDist(stations):
        mat = []
        for i in range(len(stations)):
            line = []
            for j in range(len(stations)):
                line.append(stations[i].distance(stations[j]))
            mat.append(line)
        return mat

class Line:
    totalLines = 0
    def __init__(self, stations, timeInterval):
        self.id = Line.totalLines
        Line.totalLines += 1       
        self.stations = stations
        self.timeInterval = timeInterval
    def waitTime(self,station,timeStart,actualTime):
        position = self.stations.index(station)
        firstStop = timeStart + position*self.timeInterval
        if actualTime > firstStop :
            return (actualTime - firstStop)%self.timeInterval
        else :
            return firstStop - actualTime
    def addStation(self,station):
        self.stations.append(station)

class Station:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
    def distance(self, station):
        return(sqrt((self.x-station.x)**2+(self.y-station.y)**2))
    def print(self):
        print("["+str(self.id)+","+str(self.x)+","+str(self.y)+"]")


class City:
    def __init__(self, stations):
        self.stations = stations
        self.matriceDist = getMatriceDist(stations)
        self.lines = []
    def __init__(self, stations, lines):
        self.stations = stations
        self.matriceDist = getMatriceDist(stations)
        self.lines = lines
    def addStation(self,station):
        self.stations.append(station)
        self.setMatriceDist()
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
    def setMatriceDist(self):
        self.matriceDist = getMatriceDist(self.stations)
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
        for k in range(j):
            stat = stations[r.randint(0,nbStations-1)]
            if stat in stationsLeft :
                stationsLeft.remove(stat)
            line.addStation(stat)
        lines.append(line)
    for i in stationsLeft:
        j = r.randint(0,nbLines-1)
        lines[j].addStation(i)
    return lines

def generateCity(nb_stations,minx,maxx,miny,maxy,nbLines,minLenLines,maxLenLines,timeInterval):
    stations = generateStations(nb_stations,minx,maxx,miny,maxy)
    lines = generateLines(stations,nbLines,minLenLines,maxLenLines,timeInterval)
    return City(stations,lines)

paris = generateCity(100,0,10,0,10,10,5,15,3)
paris.plot()
