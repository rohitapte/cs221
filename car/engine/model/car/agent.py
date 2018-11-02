'''
Created on Jun 11, 2013

@author: chrispiech
'''
from engine.model.car.car import Car
from engine.view.display import Display
from engine.vector import Vec2d
from submission import ParticleFilter, ExactInference
from none import NoInference
from engine.const import Const
import random

class Agent(Car):
    
    ACCELERATION = 10.0
    MAX_SPEED_STD = 2.0
    
    colorCounter = 0
    
    def __init__(self, startNode, agentGraph, model, agentComm):
        self.agentGraph = agentGraph
        self.model = model
        self.agentComm = agentComm
        startPos = startNode.getPos()
        startDirName = startNode.getDir()
        super(Agent, self).__init__(startPos, startDirName, Vec2d(0, 0))
        self.maxSpeed = random.gauss(Car.MAX_SPEED, Agent.MAX_SPEED_STD)
        self.goalNode = self.getGoalNode(startNode.getId())
        self.hasInference = False
        self.color = self.initColor()
        
        self.inIntersection = True
        self.claimedIntersection = None
    
    def initColor(self):
        colors = Display.COLORS
        index = Agent.colorCounter % len(colors)
        Agent.colorCounter += 1
        return colors[index]
        
    def getColor(self):
        return self.color
        
    def isJunior(self):
        return False

    def update(self):
        if Const.CARS_PARKED: return
        return super(Agent, self).update()

    def isCloseToOtherCar(self):
        newBounds = []
        offset = self.dir.normalized() * 1.5 * Car.LENGTH
        for bound in self.getBounds():
            bound += offset
            newBounds.append(bound)
        newPos = self.pos + offset
        for agent in self.agentComm.getAgents():
            if agent.collides(newPos, newBounds): return True
        return False

    def driveToGoal(self):
        if self.isCloseToOtherCar():
            self.velocity = Vec2d(0, 0)
            self.agentComm.unclaimIntersection(self)
            return
        
        #self.accelerate(Agent.ACCELERATION)
        #return
        
        frontOfCar = self.pos + self.dir.normalized() * Car.LENGTH
        if self.inIntersection:
            
            inter = self.model.getIntersection(frontOfCar.x, frontOfCar.y)
            
            
            if not self.agentComm.claimIntersection(inter, self): return
            self.accelerate(Agent.ACCELERATION)    
            if not inter:
                self.agentComm.unclaimIntersection(self)
                self.inIntersection = False
        else:
            if self.model.inIntersection(frontOfCar.x, frontOfCar.y):
                self.velocity = Vec2d(0, 0)
                self.agentComm.unclaimIntersection(self)
                self.inIntersection = True
            else:
                self.accelerate(Agent.ACCELERATION)

    def getAcceleratorAction(self, vectorToGoal):
        distanceToGoal = vectorToGoal.get_length()
        if distanceToGoal > 30:
            self.driveToGoal()
        else:
            self.arrivedAtGoal()

    def getWheelAction(self, vectorToGoal):
        turnAngle = -vectorToGoal.get_angle_between(self.dir)
        self.setWheelAngle(turnAngle)
    
    def arrivedAtGoal(self):
        currentId = self.goalNodeId
        self.getGoalNode(currentId)
    
    def getGoalNode(self, currendId):
        goalIds = self.agentGraph.getNextNodeIds(currendId)
        possibleGoals = []
        for goalId in goalIds:
            goal = self.agentGraph.getNode(goalId)
            goalVec = goal.getPos() - self.pos
            goalAngle = self.dir.get_angle_between(goalVec)
            if abs(goalAngle) < 90:
                possibleGoals.append(goalId)
            
        if len(possibleGoals) == 0: return
            
        self.goalNodeId = random.choice(possibleGoals)
        self.goalNode = self.agentGraph.getNode(self.goalNodeId)
        self.goalPos = self.goalNode.getPos()
        
    def getStartPos(self, startData):
        nodeId = startData['id']
        startNode = self.agentGraph.getNode(nodeId)
        return startNode.getPos()
    
    def getInference(self):
        if not self.hasInference:
            rows = self.model.getBeliefRows()
            cols = self.model.getBeliefCols()
            if Const.INFERENCE == 'particleFilter':
                self.inference = ParticleFilter(rows, cols)
            elif Const.INFERENCE == 'exactInference':
                self.inference = ExactInference(rows, cols)
            elif Const.INFERENCE == 'none':
                self.inference = NoInference(rows, cols)
            else:
                raise Exception(Const.INFERENCE + ' not understood')
            self.hasInference = True
        return self.inference
    
    def action(self):
        vectorToGoal = (self.goalPos - self.pos)
        self.getAcceleratorAction(vectorToGoal)
        self.getWheelAction(vectorToGoal)
        
