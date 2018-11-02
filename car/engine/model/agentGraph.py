
'''
Created on Jun 11, 2013

@author: chrispiech
'''

from node import Node
from engine.vector import Vec2d
import random

class AgentGraph(object):
    
    def __init__(self, data):
        self.nodeMap = {}
        self.pathGraph = {}
        self.loadNodes(data)
        self.loadPath(data)
        
    def add(self, moreData):
        self.loadNodes(moreData)
        self.loadPath(moreData)
        
    def getNode(self, nodeId):
        return self.nodeMap[nodeId]
    
    def getNodeX(self, nodeId):
        return self.getNode(nodeId).getPos().x
    
    def getNodeY(self, nodeId):
        return self.getNode(nodeId).getPos().y
    
    def atNode(self, nodeId, pos):
        node = self.nodeMap[nodeId]
        dist = node.getDist(pos)
        return dist < 30
    
    def nodeIsLeft(self, nodeId, carPos, carDir):
        correctNode = nodeId == 5
        c = self.getNode(nodeId).getPos()
        a = carPos
        b = carPos + carDir
        return ((b.x - a.x)*(c.y - a.y) - (b.y - a.y)*(c.x - a.x)) < 0   
        
    def isTerminal(self, nodeId):
        return self.getNode(nodeId).isTerminal()
    
    def nodeIsRight(self, nodeId, carPos, carDir):
        correctNode = nodeId == 5
        c = self.getNode(nodeId).getPos()
        a = carPos
        b = carPos + carDir
        return ((b.x - a.x)*(c.y - a.y) - (b.y - a.y)*(c.x - a.x)) > 0 
    
    def getNextNodeIds(self, nodeId):
        if not nodeId in self.pathGraph: return []
        return self.pathGraph[nodeId]
    
    def getRandomNode(self):
        id = random.choice(self.nodeMap.keys())
        return self.getNode(id)
    
    def getNearestNode(self, pos):
        nearestId = None
        nearestDist = None
        for nodeId in self.nodeMap:
            node = self.nodeMap[nodeId]
            dist = node.getDist(pos)
            if nearestId == None or dist < nearestDist:
                nearestDist = dist
                nearestId = nodeId
        return nearestId
        
    def loadNodes(self, data):
        nodeData = data['nodes']
        
        for nodeDatum in nodeData:
            node = Node(nodeDatum)
            nodeId = node.getId()
            self.nodeMap[nodeId] = node

    def loadPath(self, data):
        pathData = data['edges']
        for edge in pathData:
            start = edge[0]
            end = edge[1]
            if not start in self.pathGraph:
                self.pathGraph[start] = []
            self.pathGraph[start].append(end)
