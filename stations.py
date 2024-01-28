#distances en km temps en s
import random as r
from math import sqrt,inf
import matplotlib.pyplot as plt
import copy as cp
import time as t

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
            steps.append([str(stops[i][1])+" to "+str(stops[i+1][1]),timestep])
        return tabDijkstra[-1],tabDijkstras,distance(xstart,ystart,xend,yend)*720,stops,steps

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


# paris = generateCity(100,0,10,0,10,10,5,15,180)
# dij = paris.Dijkstra(0,0,10,10,0,0)
# print(dij[0])
# for i in dij[1]:
#     print(i)
# print(dij[3])

""" stations = [Station(0,0,0),Station(2,0,1),Station(1,0,2)]
lines = [Line(stations,180)]
city = City(stations,lines) """
start = t.time()
city = generateCity(300,0,10,0,10,16,5,15,180)
print(t.time()-start)
start = t.time()
dij = city.Dijkstra(0,0,10,10,0,500)
print(t.time()-start)

