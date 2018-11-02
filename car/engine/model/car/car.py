from engine.vector import Vec2d
from engine.model.observation import SonarObservation
from engine.const import Const

import random
import math

class Car(object):
    
    REVERSE = 'Reverse'
    DRIVE_FORWARD = 'Forward'
    TURN_LEFT = 'Left'
    TURN_RIGHT = 'Right'
    TURN_WHEEL = 'Wheel'
    
    MAX_WHEEL_ANGLE = 130.0
    MAX_SPEED = 16.0
    MAX_ACCELERATION = 10.0
    FRICTION = 2.0
    LENGTH = 30.0
    WIDTH = 15.0 
    RADIUS = math.sqrt(LENGTH ** 2 + WIDTH ** 2)
    
    def __init__(self, pos, dirName, velocity):
        self.initialPos = Vec2d(pos.x, pos.y)
        self.pos = pos
        self.velocity = velocity
        direction = self.dirFromName(dirName)
        self.dir = direction
        self.wheelAngle = 0
        self.maxSpeed = Car.MAX_SPEED
        self.friction = Car.FRICTION
        self.maxWheelAngle = Car.MAX_WHEEL_ANGLE
        
    def getPos(self):
        return self.pos
    
    def getDir(self):
        return self.dir
        
    def getObservation(self, junior):
        #Sonar
        dist = (junior.pos - self.pos).get_length()
        std = Const.SONAR_STD
        return SonarObservation(random.gauss(dist, std))
        
        #Radar
        '''errorForwards = Const.RADAR_NOISE_STD
        errorSide = Const.RADAR_NOISE_STD
        noiseForwards = random.gauss(0, errorForwards)
        noiseSide = random.gauss(0, errorSide)
        
        dirVec = self.dir.normalized()
        sideVec = dirVec.perpendicular()
        point = Vec2d(self.pos.x, self.pos.y)
        point += dirVec * noiseForwards + sideVec * noiseSide
        return Observation(point)'''
        

    def turnCarTowardsWheels(self):
        if self.velocity.get_length() > 0.0:
            self.velocity.rotate(self.wheelAngle)
            self.dir = Vec2d(self.velocity.x, self.velocity.y)

    def update(self):
        self.turnCarTowardsWheels()
        self.pos += self.velocity
        self.turnWheelsTowardsStraight()
        self.applyFriction()
    
    def turnWheelsTowardsStraight(self):
        if self.wheelAngle < 0:
            self.wheelAngle += 0.7
            if self.wheelAngle > 0:
                self.wheelAngle = 0.0
        if self.wheelAngle > 0:
            self.wheelAngle -= 0.7
            if self.wheelAngle < 0:
                self.wheelAngle = 0.0
        
    def decellerate(self, amount):
        speed = self.velocity.get_length()
        if speed == 0: return
        frictionVec = self.velocity.get_reflection().normalized()
        frictionVec *= amount
        self.velocity += frictionVec
        angle = self.velocity.get_angle_between(frictionVec)
        if abs(angle) < 180:
            self.velocity = Vec2d(0, 0)
    
    def applyFriction(self):
        self.decellerate(self.friction)
        
    def setWheelAngle(self, angle):
        self.wheelAngle = angle
        if self.wheelAngle <= -self.maxWheelAngle:
            self.wheelAngle= -self.maxWheelAngle
        if self.wheelAngle >= self.maxWheelAngle:
            self.wheelAngle = self.maxWheelAngle
        
    def turnLeft(self, amount):
        self.wheelAngle -= amount
        if self.wheelAngle <= -self.maxWheelAngle:
            self.wheelAngle= -self.maxWheelAngle
        
    def turnRight(self, amount):
        self.wheelAngle += amount
        if self.wheelAngle >= self.maxWheelAngle:
            self.wheelAngle = self.maxWheelAngle
    
    def accelerate(self, amount):
        amount = min(amount, Car.MAX_ACCELERATION)
        acceleration = Vec2d(self.dir.x, self.dir.y).normalized()
        acceleration *= amount
        self.velocity += acceleration
        if (self.velocity.get_length() >= self.maxSpeed):
            self.velocity.set_length(self.maxSpeed)
           
    # http://www.gamedev.net/page/resources/_/technical/game-programming/2d-rotated-rectangle-collision-r2604 
    def collides(self, otherPos, otherBounds):
        diff = otherPos - self.pos
        dist = diff.get_length()
        if dist > Car.RADIUS * 2: return False
        
        bounds = self.getBounds()
        vec1 = bounds[0] - bounds[1]
        vec2 = otherBounds[0] - otherBounds[1]
        axis = [
            vec1,
            vec1.perpendicular(),
            vec2,
            vec2.perpendicular()
        ]
        for vec in axis:
            (minA, maxA) = Vec2d.projectPoints(bounds, vec)
            (minB, maxB) = Vec2d.projectPoints(otherBounds, vec)
            leftmostA = minA <= minB
            overlap = False
            if leftmostA and maxA >= minB: overlap = True
            if not leftmostA and maxB >= minA: overlap = True
            if not overlap: return False
        return True
            
    def getBounds(self):
        normalDir = self.dir.normalized()
        perpDir = normalDir.perpendicular()
        bounds = [
            self.pos + normalDir * Car.LENGTH / 2 + perpDir * Car.WIDTH / 2,
            self.pos + normalDir * Car.LENGTH / 2 - perpDir * Car.WIDTH / 2,
            self.pos - normalDir * Car.LENGTH / 2 + perpDir * Car.WIDTH / 2,
            self.pos - normalDir * Car.LENGTH / 2 - perpDir * Car.WIDTH / 2
        ]
        return bounds
            
    def dirFromName(self, dirName):
        if dirName == 'north': return Vec2d(0, -1)
        if dirName == 'west': return Vec2d(-1, 0)
        if dirName == 'south': return Vec2d(0, 1)
        if dirName == 'east': return Vec2d(1, 0)
        raise Exception(str(dirName) + ' is not a recognized dir.')
        
