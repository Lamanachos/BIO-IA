#distances en km temps en s
import random as r
from math import sqrt,inf
import matplotlib.pyplot as plt
import copy as cp

def distance(x1,y1,x2,y2):
    return sqrt((x2-x1)**2+(y2-y1)**2)

class Station:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
    def distanceStat(self, station):
        return distance(self.x,self.y,station.x,station.y)
    def distance(self, x1 : int,y1 : int):
        return distance(self.x,self.y,x1,y1)
    def print(self):
        print("["+str(self.id)+","+str(self.x)+","+str(self.y)+"]")

class Line:
    totalLines = 0
    def __init__(self, stations : list[Station], timeInterval):
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
            for i in range(l-2):
                if mat[stats[i].id][stats[i+1].id] != []:
                    mat[stats[i].id][stats[i+1].id].append(line)
                    mat[stats[i+1].id][stats[i].id].append(line)
                else :
                    mat[stats[i+1].id][stats[i].id].append(stats[i+1].distanceStat(stats[i]))
                    mat[stats[i].id][stats[i+1].id].append(stats[i+1].distanceStat(stats[i]))
                    mat[stats[i+1].id][stats[i].id].append(line)
                    mat[stats[i].id][stats[i+1].id].append(line)
        return mat

class City:
    def __init__(self, stations : list[Station]):
        self.stations = stations
        self.lines = []
        self.setMatriceDist()
    def __init__(self, stations : list[Station], lines : list[Line]):
        self.stations = stations
        self.matriceDist = getMatriceDist(stations,lines)
        self.lines = lines
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
        for i in self.stations:
            dist = i.distance(xstart,ystart)
            tabDijkstra.append(dist*720)#en moyenne un humain met 720s à faire 1km
        tabDijkstra.append(distance(xstart,ystart,xend,yend)*720)
        minIndex = tabDijkstra.index(min(tabDijkstra))
        previousMins = [minIndex]
        tabDijkstras = [tabDijkstra.copy()]
        while minIndex != len(tabDijkstra)-1 :
            ts = tabDijkstra[minIndex]
            matDists = self.matriceDist[minIndex]
            for j in range(len(matDists)):
                if matDists[j] != []:
                    for line in matDists[j][1:]:
                        temp = line.waitTime(self.stations[j],tstartSim,tabDijkstra[minIndex]+tstart)
                        if tabDijkstra[j] > temp + ts + (matDists[j][0])*144:
                            tabDijkstra[j] = temp + ts + (matDists[j][0])*144
            distEnd = self.stations[j].distance(xend,yend)*720 + ts
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
        return tabDijkstra[-1],tabDijkstras,distance(xstart,ystart,xend,yend)*720

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

paris = generateCity(100,0,10,0,10,10,5,15,3)
dij = paris.Dijkstra(0,0,10,10,0,0)
print(dij[0])
#print(dij[1][-1])
print(dij[2])
