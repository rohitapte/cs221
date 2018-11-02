
from engine.model.layout import Layout
from intersection import *

class GraphCreater(object):
    
    def __init__(self, fileName):
        self.layout = Layout(fileName)
    
    def run(self):
        data = self.layout.getIntersectionData()
        self.interDict = self.getInterDict(data)
        self.edgeDict = self.getEdgeDict(data)
        self.createExteralConnections()
        self.createInternalConnections()
        print '"agentGraph": {'
        self.outputNodes()
        self.outputEdges()
        print '}'
        
    def outputEdges(self):
        allEdges = []
        for interId in self.interDict:
            inter = self.interDict[interId]
            for node in inter.getAllEdgeStrings():
                allEdges.append(node)
                
        
        print '"edges": ['
        for i in range(len(allEdges)):
            edge = allEdges[i]
            if i != len(allEdges) - 1: edge += ','
            print edge
        print ']'
        
    def outputNodes(self):
        allNodes = []
        for interId in self.interDict:
            inter = self.interDict[interId]
            for node in inter.getAllNodes():
                allNodes.append(node)
                
        print '"nodes": ['
        for i in range(len(allNodes)):
            node = allNodes[i]
            json = node.getJson()
            if i != len(allNodes) - 1: json += ','
            print json
        print '],'
        
    def createInternalConnections(self):
        for interId in self.interDict:
            inter = self.interDict[interId]
            inter.connectInternal()
        
    def createExteralConnections(self):
        for outId in self.edgeDict:
            outInter = self.interDict[outId]
            for inId in self.edgeDict[outId]:
                inInter = self.interDict[inId]
                outInter.connect(inInter)

    def getEdgeDict(self, data):
        edgeData = data['edges']
        edgeDict = {}
        for key in edgeData:
            edgeDict[int(key)] = edgeData[key]
        return edgeDict

    def getInterDict(self, data):
        nodeData = data['nodes']
        nodeDict = {}
        for i in range(len(nodeData)):
            datum = nodeData[i]
            nodeDict[i] = Intersection(datum, i)
        return nodeDict


        