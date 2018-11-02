from engine.const import Const

import math

class SonarObservation(object):

    def __init__(self, dist):
        self.dist = dist

    def getDist(self):
        return self.dist

class Observation(object):
    
    RADIUS = 3
    
    def __init__(self, pos):
        self.pos = pos
        self.output = True
        
    def remove(self, display):
        assert(self.parts)
        display.remove(self.parts)
        
    def getX(self):
        return self.pos.x
    
    def getY(self):
        return self.pos.y
        
    def getRow(self):
        row = Discretization.yToRow(self.pos.y)
        if not self.output:
            print '---------'
            print self.pos.y
            print self.pos.y / Const.BELIEF_TILE_SIZE
            print int(self.pos.y / Const.BELIEF_TILE_SIZE)
            print round(self.pos.y / Const.BELIEF_TILE_SIZE)
            print '---------'
        self.output = True
        return row
    
    def getCol(self):
        return Discretization.xToCol(self.pos.x)
