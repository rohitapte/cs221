from car.car import Car
from car.agent import Agent
from car.junior import Junior
from autoDriver import AutoDriver
from engine.vector import Vec2d
from engine.const import Const
from engine.model.block import Block
from engine.model.agentCommunication import AgentCommunication

import threading
import copy
import util

class Model(object):

    def __init__(self, layout):
        self._initBlocks(layout)
        self._initIntersections(layout)
        self.layout = layout
        startX = layout.getStartX()
        startY = layout.getStartY()
        startDirName = layout.getJuniorDir()
        self.junior = AutoDriver()
        self.junior.setup(
            Vec2d(startX, startY), 
            startDirName, 
            Vec2d(0, 0)
        )
        self.cars = [self.junior]
        self.otherCars = []
        self.finish = Block(layout.getFinish())

        agentComm = AgentCommunication()
        agentGraph = layout.getAgentGraph()
        for _ in range(Const.NUM_AGENTS):
            startNode = self._getStartNode(agentGraph)
            other = Agent(startNode, layout.getAgentGraph(), self, agentComm)
            self.cars.append(other)
            self.otherCars.append(other)
        self.observations = []
        agentComm.addAgents(self.otherCars)
        self.modelLock = threading.Lock()
        self.probCarSet = False
        
    def _initBlocks(self, layout):
        self.blocks = []
        for blockData in layout.getBlockData():
            block = Block(blockData)
            self.blocks.append(block)
            
    def _initIntersections(self, layout):
        self.intersections = []
        for blockData in layout.getIntersectionNodes():
            block = Block(blockData)
            self.intersections.append(block)
            
    def _getStartNode(self, agentGraph):
        while True:
            node = agentGraph.getRandomNode()
            pos = node.getPos()
            alreadyChosen = False
            for car in self.otherCars:
                if car.getPos() == pos:
                    alreadyChosen = True
                    break
            if not alreadyChosen: 
                return node
            
    def checkVictory(self):
        bounds = self.junior.getBounds()
        for point in bounds:
            if self.finish.containsPoint(point.x, point.y): return True
        return False
            
    def checkCollision(self, car):
        bounds = car.getBounds()
        # check for collision with fixed obstacles
        for point in bounds:
            if not self.inBounds(point.x, point.y): return True
        
        # check for collision with other cars
        for other in self.cars:
            if other == car: continue
            if other.collides(car.getPos(), bounds): return True
        return False
        
    def getIntersection(self, x, y):
        for intersection in self.intersections:
            if intersection.containsPoint(x, y): return intersection
        return None
        
    def inIntersection(self, x, y):
        return self.getIntersection(x, y) != None
            
    def inBounds(self, x, y):
        if x < 0 or x >= self.getWidth(): return False
        if y < 0 or y >= self.getHeight(): return False
        for block in self.blocks:
            if block.containsPoint(x, y): return False
        return True
    
    def getWidth(self):
        return self.layout.getWidth()
    
    def getHeight(self):
        return self.layout.getHeight()
    
    def getBeliefRows(self):
        return self.layout.getBeliefRows()
    
    def getBeliefCols(self):
        return self.layout.getBeliefCols()
            
    def getBlocks(self):
        return self.blocks
    
    def getFinish(self):
        return self.finish
        
    def getCars(self):
        return self.cars
    
    def getOtherCars(self):
        return self.otherCars
    
    def getJunior(self):
        return self.junior
    
    def getAgentGraph(self):
        return self.layout.getAgentGraph()
    
    def getJuniorGraph(self):
        return self.layout.getJuniorGraph()
    
    def setProbCar(self, beliefs):
        self.modelLock.acquire()
        total = util.Belief(self.getBeliefRows(), self.getBeliefCols(), 0.0)
        for r in range(self.getBeliefRows()):
            for c in range(self.getBeliefCols()):
                pNot = 1.0
                for b in beliefs:
                    carP = b.getProb(r, c)
                    pNot *= (1.0 - carP)
                p = 1.0 - pNot
                total.setProb(r, c, p)
        self.probCar = total
        self.modelLock.release()
        self.probCarSet = True
    
    def getProbCar(self):
        if not self.probCarSet: return None
        self.modelLock.acquire()
        probCar = copy.deepcopy(self.probCar)
        self.modelLock.release()
        return probCar