from engine.model.car.car import Car
from engine.view.display import Display
from engine.vector import Vec2d
from engine.const import Const

class Junior(Car):
    
    FORWARD_KEY = 'Up'
    BACK_KEY = 'Back'
    LEFT_KEY = 'Left'
    RIGHT_KEY = 'Right'
    
    ACCELERATION = 1.4
    FRICTION = 1.0
    WHEEL_TURN = 2.0
    WHEEL_TURN_HUMAN = 1.0
    MAX_WHEEL_ANGLE = 10.0
    MAX_SPEED = 5.0
    
    def setup(self, pos, direction, velocity):
        Car.__init__(self, pos, direction, velocity)
        self.maxSpeed = Junior.MAX_SPEED
        self.friction = Junior.FRICTION
        self.maxWheelAngle = Junior.MAX_WHEEL_ANGLE
        if not Const.AUTO:
            Junior.WHEEL_TURN = Junior.WHEEL_TURN_HUMAN
        else:
            self.maxWheelAngle = Junior.MAX_WHEEL_ANGLE *2
    
    def isJunior(self):
        return True
    
    def action(self):
        keys = Display.getKeys()
        actions = self.getActions(keys)
        self.applyActions(actions)
        return 'q' in keys
    
    def getActions(self, keys):
        actions = []
        forwardDown = Junior.FORWARD_KEY in keys or 'w' in keys
        leftDown = Junior.LEFT_KEY in keys or 'a' in keys
        rightDown = Junior.RIGHT_KEY in keys or 'd' in keys
        if forwardDown:
            actions.append(Car.DRIVE_FORWARD)
        if not (leftDown and rightDown):
            if leftDown:
                actions.append(Car.TURN_LEFT)
            if rightDown:
                actions.append(Car.TURN_RIGHT)
        return actions
    
    def autonomousAction(self, beliefs, agentGraph):
        oldPos = Vec2d(self.pos.x, self.pos.y)
        oldDir = Vec2d(self.dir.x, self.dir.y)
        oldVel = Vec2d(self.velocity.x, self.velocity.y)
        actions = self.getAutonomousActions(beliefs, agentGraph)
        assert self.pos == oldPos
        assert self.dir == oldDir
        assert self.velocity == oldVel
        if Car.DRIVE_FORWARD in actions:
            percent = actions[Car.DRIVE_FORWARD]
            percent = max(percent, 0.0)
            percent = min(percent, 1.0)
            self.accelerate(Junior.ACCELERATION * percent)
        if Car.TURN_WHEEL in actions:
            turnAngle = actions[Car.TURN_WHEEL]
            self.setWheelAngle(turnAngle)
        
        
    def applyActions(self, actions):
        moveForward = Car.DRIVE_FORWARD in actions
        turnLeft = Car.TURN_LEFT in actions
        turnRight = Car.TURN_RIGHT in actions
        
        assert not (turnLeft and turnRight)
        
        if moveForward:
            self.accelerate(Junior.ACCELERATION)
        if turnLeft:
            self.turnLeft(Junior.WHEEL_TURN)
        if turnRight:
            self.turnRight(Junior.WHEEL_TURN)
        
        
