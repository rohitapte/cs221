'''
Licensing Information: Please do not distribute or publish solutions to this
project. You are free to use and extend Driverless Car for educational
purposes. The Driverless Car project was developed at Stanford, primarily by
Chris Piech (piech@cs.stanford.edu). It was inspired by the Pacman projects.
'''
from engine.model.car.junior import Junior
from engine.model.car.car import Car

import util
import random

# Class: AutoDriver
# ---------------------
# An initially naive autonomous driver that drives around a map, avoiding cars
# based on beliefs. Feel free to extend this class. It is *not* required!
class AutoDriver(Junior):

    MIN_PROB = 0.02
    
    # Funciton: Init
    # ---------------------
    # Create an autonomous driver. Give it a number of heartBeats to wait before
    # it starts to drive
    def __init__(self):
        self.nodeId = None
        self.nextId = None
        self.nextNode = None
        self.burnInIterations = 30
    
    # Funciton: Get Autonomous Actions
    # ---------------------
    # Given the current belief about where other cars are and a graph of how
    # one can driver around the world, chose a next action.
    def getAutonomousActions(self, beliefOfOtherCars, agentGraph):
        # Don't start until after your burn in iterations have expired
        if self.burnInIterations > 0:
            self.burnInIterations -= 1
            return[]
        
        # Chose a next node to drive towards. Note that you can ask
        # a if its a terminal using node.isTerminal()
        if self.nodeId == None:
            self.nodeId = agentGraph.getNearestNode(self.pos)
        if self.nextId == None:
            self.choseNextId(agentGraph)
        if agentGraph.atNode(self.nextId, self.pos):
            self.nodeId = self.nextId
            self.choseNextId(agentGraph)
          
        # given a next node, drive towards that node. Stop if you
        # are too close to another car
        goalPos = agentGraph.getNode(self.nextId).getPos()
        vectorToGoal = goalPos - self.pos
        wheelAngle = -vectorToGoal.get_angle_between(self.dir)
        driveForward = not self.isCloseToOtherCar(beliefOfOtherCars)
        actions = {
            Car.TURN_WHEEL: wheelAngle
        }
        if driveForward:
            actions[Car.DRIVE_FORWARD] = 1.0
        return actions
    
    # Funciton: Is Close to Other Car
    # ---------------------
    # Given the current belief about where other cars are decides if
    # there is a car in the spot where we are about to drive. 
    def isCloseToOtherCar(self, beliefOfOtherCars):
        newBounds = []
        offset = self.dir.normalized() * 1.5 * Car.LENGTH
        newPos = self.pos + offset
        row = util.yToRow(newPos.y)
        col = util.xToCol(newPos.x)
        p = beliefOfOtherCars.getProb(row, col)
        return p > AutoDriver.MIN_PROB
    
    # Funciton: Chose Next Id
    # ---------------------
    # You have arrived at self.nodeId. Chose a next node to drive
    # towards.
    def choseNextId(self, agentGraph):
        nextIds = agentGraph.getNextNodeIds(self.nodeId)
        if nextIds == []: 
            self.nextId = None
        else:
            self.nextId = random.choice(nextIds)
