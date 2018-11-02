from const import Const
from view.display import Display
from vector import Vec2d


import time
import threading

class UserThread(threading.Thread):
    
    uiLock = threading.Lock()
    
    def __init__(self, junior, model):
        threading.Thread.__init__(self)
        self.junior = junior
        self.model = model
        self.collision = False
        self.quit = False
        self.victory = False
        self.stopFlag = threading.Event()
        
    def run(self):
        while not self.shouldStop():
            startTime = time.time()
            self.heartbeat()
            elapsed = time.time() - startTime
            timeToSleep = Const.SECONDS_PER_UI_HEARTBEAT - elapsed
            if timeToSleep > 0:
                time.sleep(timeToSleep)             
    
    def shouldStop(self):
        if self.stopFlag.is_set(): return True
        if self.collision: return True
        if self.quit: return True
        if self.victory: return True
        return False
                
    def stop(self):
        self.stopFlag.set()
                
    def hasCollided(self):
        return self.collision

    def heartbeat(self):        
        oldDir = Vec2d(self.junior.dir.x, self.junior.dir.y)
        oldPos = Vec2d(self.junior.pos.x, self.junior.pos.y)
        quitAction = self.junior.action()
        carProb = self.model.getProbCar()
        if carProb and Const.AUTO:
            agentGraph = self.model.getJuniorGraph()
            self.junior.autonomousAction(carProb, agentGraph)
        if quitAction: 
            self.quit = True
            return
        self.junior.update()
        self.collision = self.model.checkCollision(self.junior)
        self.victory = self.model.checkVictory()
        newPos = self.junior.getPos()
        newDir = self.junior.getDir()
        deltaPos = newPos - oldPos
        deltaAngle = oldDir.get_angle_between(newDir)
        Display.move(self.junior, deltaPos)
        Display.rotate(self.junior, deltaAngle)
        
