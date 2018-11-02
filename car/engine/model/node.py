'''
Created on Jun 11, 2013

@author: chrispiech
'''

from engine.vector import Vec2d

import math

class Node(object):
    
    def __init__(self, nodeData):
        self.id = nodeData['id']
        pos = nodeData['pos']
        self.dir = nodeData['dir']
        self.x = pos[0]
        self.y = pos[1]
        self.terminal = 'terminal' in nodeData
        
    def getId(self):
        return self.id
    
    def getPos(self):
        return Vec2d(self.x, self.y)
    
    def getDir(self):
        return self.dir
    
    def isTerminal(self):
        return self.terminal
    
    def getDist(self, pos):
        dx = self.x - pos.x
        dy = self.y - pos.y
        return math.sqrt(dx * dx + dy * dy)
    
    def __repr__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ')'