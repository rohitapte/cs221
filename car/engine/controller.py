from model.model import Model
from const import Const
from view.display import Display
from model.layout import Layout
from vector import Vec2d
from containers.counter import Counter
from userThread import UserThread
import util as util
import view.graphicsUtils

import time
import math
import sys
import traceback

class Controller(object):
    
    def __init__(self):
        self.layout = Layout(Const.WORLD)
        Display.initGraphics(self.layout)
        self.model = Model(self.layout)
        self.carChanges = {}
        self.errorCounter = Counter()
        self.consecutiveLate = 0
        
        
    def learn(self, learner):
        self.isLearning = True
        self.learner = learner
        return self.run()
        
    def drive(self):
        self.isLearning = False
        return self.run()
        
    def run(self):
        self.render()
        self.userThread = UserThread(self.model.junior, self.model)
        self.userThread.start()
        self.iteration = 0
        while not self.isGameOver():
            self.resetTimes()
            startTime = time.time()
            self.printStats()
            
            self.otherCarUpdate()
            self.calculateError()
                        
            duration = time.time() - startTime
            timeToSleep = Const.SECONDS_PER_HEARTBEAT - duration
            # self.checkLate(timeToSleep)
            timeToSleep = max(0.01, timeToSleep)
            Display.graphicsSleep(timeToSleep)
            self.iteration += 1
        if not self.userThread.quit and not self.isLearning:
            self.outputGameResult()
        self.userThread.stop()
        Display.graphicsSleep(0.1)
        self.userThread.join()
        return self.userThread.quit
        
    def freezeFrame(self):
        while True:
            keys = Display.getKeys()
            if 'q' in keys: return
            Display.graphicsSleep(0.1)
        
    def outputGameResult(self):
        collided = self.userThread.hasCollided()
        for car in self.model.getCars():
            Display.drawCar(car)
        print '*********************************'
        print '* GAME OVER                     *'
        if collided:
            print '* CAR CRASH!!!!!'
        else:
            print '* You Win!'
        print '*********************************'    
        
            
    def isGameOver(self):
        if self.isLearning:
            keys = Display.getKeys()
            if 'q' in keys: 
                self.userThread.quit = True
                return True
            return self.iteration > Const.TRAIN_ITERATIONS
        if self.userThread.quit:
            return True
        if self.userThread.victory:
            return True
        return self.userThread.hasCollided()

    def round(self, num):
        return round(num * 1000) / 1000.0

    def checkLate(self, timeToSleep):
        secsLate = self.round(-timeToSleep)
        if secsLate > 0:
            self.consecutiveLate += 1
            if self.consecutiveLate < 3: return
            print '*****************************'
            print 'WARNING: Late to update (' + str(secsLate) + 's)'
            
            print 'Infer time: ' + str(self.round(self.inferTime))
            print 'Action time: ' + str(self.round(self.actionTime))
            print 'Update time: ' + str(self.round(self.updateTime))
            print 'Draw time: ' + str(self.round(self.drawTime))
            print '*****************************'
        else:
            self.consecutiveLate = 0

    def resetTimes(self):
        self.actionTime = 0
        self.inferTime = 0
        self.drawTime = 0
        self.updateTime = 0

    def printStats(self):
        if self.isLearning: return
        if self.iteration == 0: return
        if self.iteration % Const.REPORT_ITER != 0: return
        print '-------------'
        print 'iteration ' + str(self.iteration)
        error = self.errorCounter.getMean() * Const.BELIEF_TILE_SIZE
        print 'error: ' + str(error)
        print'--------------'
        print ''
        

    def juniorUpdate(self):
        junior = self.model.junior
        junior.action()
        self.move([junior])

    def otherCarUpdate(self):
        if True or Const.INFERENCE != 'none':
            self.infer()
        self.act()
        self.move(self.model.getOtherCars())
        
    def observe(self):
        if self.isLearning: return
        juniorX = self.model.junior.pos.x
        juniorY = self.model.junior.pos.y
        for car in self.model.getOtherCars():
            observation = car.getObservation(self.model.junior)
            obsDist = observation.getDist()
            inference = car.getInference()
            inference.observe(juniorX, juniorY, obsDist)
        
    def elapseTime(self):
        if self.isLearning: return
        if Const.CARS_PARKED: return
        for car in self.model.getOtherCars():
            inference = car.getInference()
            inference.elapseTime()
            
    def updateBeliefs(self):
        if self.isLearning: return
        beliefs = []
        for car in self.model.getOtherCars():
            belief = car.getInference().getBelief()
            color = car.getColor()
            Display.updateBelief(color, belief)
            beliefs.append(belief)
        self.model.setProbCar(beliefs)
        
    def infer(self):
        start = time.time()

        try:
            self.elapseTime()
            self.observe()
        except  Exception, e:
            print 'caught'
            traceback.print_exc()
            Display.raiseEndGraphics()
            Display.graphicsSleep(0.01)
            self.userThread.quit = True
           
            
        inferEnd = time.time()
        self.inferTime += inferEnd - start
        self.updateBeliefs()
        self.drawTime += time.time() - inferEnd
        
    def act(self):
        start = time.time()
        for car in self.model.getOtherCars():
            car.action()
        self.actionTime += time.time() - start

    def move(self, cars):
        for car in cars:
            start = time.time()
            oldDir = Vec2d(car.dir.x, car.dir.y)
            oldPos = Vec2d(car.pos.x, car.pos.y)
            car.update()
            newPos = car.getPos()
            newDir = car.getDir()
            deltaPos = newPos - oldPos
            deltaAngle = oldDir.get_angle_between(newDir)
            self.updateTime += time.time() - start
            if Const.SHOW_CARS or car.isJunior():
                self.moveCarDisplay(car, deltaPos, deltaAngle)
            
            if self.isLearning:
                self.learner.noteCarMove(oldPos, newPos)
            
    def calculateError(self):
        if self.isLearning: return
        #if Const.INFERENCE == 'none': return
        if len(self.model.getOtherCars()) == 0: return
        errors = []
        for car in self.model.getOtherCars():
            error = self.calculateErrorForCar(car)
            errors.append(error)
        aveError = float(sum(errors)) / len(errors)
        self.errorCounter.addValue(aveError)
    
    def calculateErrorForCar(self, otherCar):
        pos = otherCar.getPos()
        carRow = util.yToRow(pos.y)
        carCol = util.xToCol(pos.x)
        belief = otherCar.getInference().getBelief()
        total = belief.getSum()
        if abs(total - 1.0) > 0.001:
            raise Exception('belief does not sum to 1. Use the normalize method.')
        totalError = 0
        for r in range(belief.getNumRows()):
            for c in range(belief.getNumCols()):
                prob = belief.getProb(r, c)
                difRow = r - carRow
                difCol = c - carCol
                error = math.sqrt(difRow ** 2 + difCol ** 2)
                errorSquared = error ** 2
                totalError += errorSquared * prob
        return totalError


    def moveCarDisplay(self, car, deltaPos, deltaAngle):
        start = time.time()
        Display.move(car, deltaPos)
        Display.rotate(car, deltaAngle)
        self.drawTime += time.time() - start
        
    def render(self):
        Display.drawBelief(self.model)
        Display.drawBlocks(self.model.getBlocks())
        if Const.SHOW_CARS:
            for car in self.model.getCars():
                Display.drawCar(car)
        else:
            Display.drawCar(self.model.getJunior())
        Display.drawFinish(self.model.getFinish())
        view.graphicsUtils.refresh()
