'''
Created on Jun 16, 2013

@author: Chris
'''

from engine.vector import Vec2d
from engine.model.block import Block

class IntersectionNode(object):
    
    idCounter = 0
    
    def __init__(self, pos, dir):
        self.id = IntersectionNode.idCounter
        IntersectionNode.idCounter += 1
        self.edges = []
        self.pos = pos
        self.dir = dir
        
    def getJson(self):
        x = self.pos.x
        y = self.pos.y
        json = '{\n'
        json += '\t"id":' + str(self.id) + ',\n'
        json += '\t"pos": [' + str(x) + ', ' + str(y) + '],\n'
        json += '\t"dir": "' + str(self.dir) + '"\n'
        json += '}'
        return json
    
    def getId(self):
        return self.id
    
    def getEdges(self):
        return self.edges
        
    def addEdge(self, other):
        self.edges.append(other)

class IntersectionSide(object):
    
    def __init__(self):
        self.inNode = None
        self.outNode = None
        
    def getNodes(self):
        nodes = []
        if self.inNode: nodes.append(self.inNode)
        if self.outNode: nodes.append(self.outNode)
        return nodes
    
    def getOut(self):
        return self.outNode
    
    def getIn(self):
        return self.inNode
    
    def hasNodes(self):
        return self.inNode or self.outNode
        
    def addOut(self, pos, dir):
        assert self.outNode == None
        self.outNode = IntersectionNode(pos, dir)
        return self.outNode
    
    def addIn(self, pos, dir):
        assert self.inNode == None
        self.inNode = IntersectionNode(pos, dir)
        return self.inNode

class Intersection(object):
    
    OPPOSITE = {
        'north': 'south',
        'south': 'north',
        'east': 'west',
        'west': 'east'
    }
    
    LEFT_TURN = {
        'north': 'east',
        'south': 'west',
        'east': 'south',
        'west': 'north'
    }
    
    ANGLE_FROM_NORTH = {
        'north': 0,
        'south': 180,
        'east': 90,
        'west': 270                  
    }
    
    def __init__(self, data, id):
        self.data = data
        self.block = Block(data)
        self.id = id
        self.sides = {
            'north': IntersectionSide(),
            'south': IntersectionSide(),
            'east': IntersectionSide(),
            'west': IntersectionSide()
        }
        self.centerNode = None
        
    def getAllNodes(self):
        nodes = []
        for sideName in self.sides:
            side = self.sides[sideName] 
            for node in side.getNodes():
                nodes.append(node)
        if self.centerNode:
            nodes.append(self.centerNode)
        return nodes
    
    def getAllEdgeStrings(self):
        nodes = self.getAllNodes()
        allEdges = []
        for node in nodes:
            others = node.getEdges()
            for other in others:
                edgeString = '[' + str(node.getId()) + ', ' + str(other.getId()) + ']'
                allEdges.append(edgeString)
        return allEdges
        
    def getConnectDir(self, other):
        if other.block.x1 > self.block.x1: return 'east'
        if other.block.x1 < self.block.x1: return 'west'
        if other.block.y1 < self.block.y1: return 'north'
        if other.block.y1 > self.block.y1: return 'south'
        raise Exception('same')
    
    def getNodePos(self, side, isIn, inIsLeft):
        width = self.block.getWidth()
        height = self.block.getHeight()
        center = self.block.getCenter()
        
        isLeft = inIsLeft != isIn
        
        if isLeft:
            offset = Vec2d(-width * .2, -height / 2.0)
        else:
            offset = Vec2d(width * .2, -height / 2.0)
        angle = Intersection.ANGLE_FROM_NORTH[side]
        offset.rotate(angle)
        
        return center + offset
        
    def connect(self, other):
        dir = self.getConnectDir(other)
        opposite = Intersection.OPPOSITE[dir]
        
        inPos = other.getNodePos(opposite, True, False)
        outPos = self.getNodePos(dir, False, False)
        
        xEqual = abs(inPos.x - outPos.x) < 1
        yEqual = abs(inPos.y - outPos.y) < 1
        assert xEqual or yEqual
        
        outNode = self.sides[dir].addOut(outPos, dir)
        inNode = other.sides[opposite].addIn(inPos, dir)
        outNode.addEdge(inNode)
        
    def connectInternal(self):
        for sideNameA in self.sides:
            for sideNameB in self.sides:
                if sideNameA == sideNameB: continue
                inNode = self.sides[sideNameA].getIn()
                outNode = self.sides[sideNameB].getOut()
                if inNode and outNode:
                    inNode.addEdge(outNode)
        if self.isOneSided():
            self.createUTurn()
            
    def isOneSided(self):
        count = 0
        for sideNameA in self.sides:
            if self.sides[sideNameA].hasNodes():
                count += 1
        return count == 1
    
    def getOneSide(self):
        for sideName in self.sides:
            if self.sides[sideName].hasNodes():
                return sideName
        raise Exception('not one sided')
         
    def createCenterNode(self):
        centerPos = self.block.getCenter()
        sideName = self.getOneSide()
        centerDir = Intersection.LEFT_TURN[sideName]
        self.centerNode = IntersectionNode(centerPos, centerDir)
            
    def createUTurn(self):
        self.createCenterNode()
        sideName = self.getOneSide()
        side = self.sides[sideName]
        inNode = side.getIn()
        outNode = side.getOut()
        inNode.addEdge(self.centerNode)
        self.centerNode.addEdge(outNode)
        
            