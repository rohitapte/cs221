from engine.const import Const
from engine.model.agentGraph import AgentGraph

import os
import json

class Layout(object):

    def __init__(self, worldName):
        self.loadData(worldName)
        self.agentGraph = AgentGraph(self.data['agentGraph'])
        self.juniorGraph = AgentGraph(self.data['agentGraph'])
        self.juniorGraph.add(self.data['juniorGraph'])
        self.assertValid()
        
    def loadData(self, worldName):
        layoutFileName = worldName + '.json'
        layoutDir = Const.LAYOUT_DIR
        layoutPath = os.path.join(layoutDir, layoutFileName)
        layoutFile = open(layoutPath)
        self.data = json.load(layoutFile)
        layoutFile.close()
        
    def getAgentStart(self):
        return self.data['starts']

    def getWidth(self):
        return self.data['size'][0]
    
    def getHeight(self):
        return self.data['size'][1]
    
    def getStartX(self):
        return self.data['junior'][0]
    
    def getStartY(self):
        return self.data['junior'][1]
    
    def getFinish(self):
        return self.data['finish']
    
    def getBlockData(self):
        return self.data['blocks']
    
    def getIntersectionNodes(self):
        return self.data['intersections']['nodes']
    
    def getIntersectionData(self):
        return self.data['intersections']
    
    def getJuniorDir(self):
        return self.data['juniorDir']
    
    def getBeliefRows(self):
        return int(self.getHeight() / Const.BELIEF_TILE_SIZE)
    
    def getBeliefCols(self):
        return int(self.getWidth() / Const.BELIEF_TILE_SIZE)
    
    def getAgentGraph(self):
        return self.agentGraph
    
    def getJuniorGraph(self):
        return self.juniorGraph
    
    def assertValid(self):
        width = self.getWidth()
        height = self.getHeight()
        assert(width % Const.BELIEF_TILE_SIZE == 0)
        assert(height % Const.BELIEF_TILE_SIZE == 0)