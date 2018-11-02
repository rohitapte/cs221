import graphicsUtils
from engine.model.car.car import Car
from engine.const import Const
from engine.model.observation import Observation
from engine.vector import Vec2d
import colorsys
import threading

class Display(object):
    
    WHITE = graphicsUtils.formatColor(1.0, 1.0, 1.0)
    RED = graphicsUtils.formatColor(1.0, 0.0, 0.0)
    GREEN = graphicsUtils.formatColor(0.16, 0.49, 0.31)
    BLUE = graphicsUtils.formatColor(0.0, 0.0, 1.0)
    BLACK = graphicsUtils.formatColor(0.0, 0.0, 0.0)
    GREY = graphicsUtils.formatColor(0.5, .5, 0.5)
    
    VISIBLE_CUTTOFF = 0.001
    
    
    partDict = {}
    beliefParts = []
    beliefValue = []
    beliefColor = []
    observations = []
    
    graphicsLock = threading.Lock()
    
    COLORS = [
        'purple',
        'green',
        'teal',
        'red',
        'orange',
        'yellow'
    ]
    COLOR_HUES = {
        'purple' : 0.8,
        'green' : 0.3,
        'teal' : 0.49,
        'red' : 0.0,
        'orange' : 0.125,
        'yellow' : 0.21
    }
    
    @staticmethod
    def initGraphics(layout):
        graphicsUtils.begin_graphics(
            width=layout.getWidth(), 
            height=layout.getHeight(), 
            color = Display.WHITE,
            title = Const.TITLE
        );
        
    @staticmethod
    def endGraphics():
        graphicsUtils.end_graphics()

    @staticmethod
    def raiseEndGraphics():
        graphicsUtils.raiseEndGraphics()
    
    @staticmethod
    def drawCar(car):
        if car in Display.partDict:
            Display._remove(car)
        color = Display.GREY
        if car.isJunior():
            color = Display.BLACK
        parts = graphicsUtils.rectangle(
            car.pos, Car.LENGTH, 
            Car.WIDTH, 
            color, 
            car.dir
        )
        Display.partDict[car] = parts
        
    @staticmethod
    def drawObservation(obs):
        parts = Display.drawCircle(obs.pos, Observation.RADIUS)
        Display.partDict[obs] = parts
    
    @staticmethod
    def drawSquare(pos, size, color):
        return graphicsUtils.square(pos, size, color)
    
    @staticmethod
    def drawFinish(block):
        graphicsUtils.rectangle(
                block.getCenter(), 
                block.getHeight(), 
                block.getWidth(), 
                Display.GREEN, 
                None,
                1.0
            )
    
    @staticmethod
    def drawBlocks(blocks):
        for block in blocks:
            graphicsUtils.rectangle(
                block.getCenter(), 
                block.getHeight(), 
                block.getWidth(), 
                Display.BLUE, 
                None,
                1.0
            )
        
    @staticmethod
    def drawCircle(pos, radius):
        return graphicsUtils.circle(pos, radius, Display.RED, Display.RED)
    
    @staticmethod
    def drawBelief(model):
        Display.beliefVisible = []
        for r in range(model.getBeliefRows()):
            beliefValueRow = []
            beliefPartRow = []
            beliefColorRow = []
            for c in range(model.getBeliefCols()):
                square = Display.drawBeliefSquare(r, c, 'purple', 0.0, model)
                beliefPartRow.append(square)
                beliefValueRow.append(0.0)
                beliefColorRow.append(None)
            Display.beliefParts.append(beliefPartRow)
            Display.beliefValue.append(beliefValueRow)
            Display.beliefColor.append(beliefColorRow)
                
    @staticmethod
    def drawBeliefSquare(row, col, color, value, model):
        tileSize = Const.BELIEF_TILE_SIZE
        x = col * tileSize + tileSize / 2.0
        y = row * tileSize + tileSize / 2.0
        if not model.inBounds(x, y): return None
        color = Display._getBeliefSquareColor(color, value)
        return Display.drawSquare(Vec2d(x, y), tileSize, color)
         
    # make thread safe
    @staticmethod
    def getKeys():
        #print 'attempt get keys'
        Display._acquireLock()
        #print 'get keys'
        keys = graphicsUtils.keys_waiting() + graphicsUtils.keys_pressed()
        Display._releaseLock()
        return keys
    
    # make thread safe
    @staticmethod
    def graphicsSleep(timeToSleep):
        graphicsUtils.sleep(timeToSleep)
        #time.sleep(timeToSleep)
        '''for _ in range(int(timeToSleep / 0.005)):
            #print 'attempt sleep'
            Display._acquireLock()
            #print 'sleep'
            graphicsUtils.sleep(0.001)
            Display._releaseLock()
            time.sleep(0.004)'''
        
        #graphicsUtils.sleep(timeToSleep)
        #time.sleep(timeToSleep)
        '''startWait = time.time()
        Display._acquireLock()
        timeToSleep -= time.time() - startWait
        graphicsUtils.refresh()
        if timeToSleep > 0:
            graphicsUtils.sleep(timeToSleep)
        Display._releaseLock()'''
             
    # make thread safe
    @staticmethod
    def updateBelief(color, belief):
        Display._acquireLock()
        total = belief.getSum()
        if abs(total - 1.0) > 0.001:
            raise Exception('belief does not sum to 1 ('+str(total)+'). Use the normalize method.')
        for r in range(belief.getNumRows()):
            for c in range(belief.getNumCols()):
                value = belief.getProb(r, c)
                Display._updateBeliefSquare(r, c, value, color)
        Display._releaseLock()
    
    # make thread safe
    @staticmethod
    def move(obj, delta):
        #print 'attempt move'
        Display._acquireLock()
        #print 'move'
        parts = Display.partDict[obj]
        #assert(parts)
        graphicsUtils.move_by(parts, delta.x, delta.y)
        #print 'end move'
        Display._releaseLock()
        
    # make thread safe
    @staticmethod
    def rotate(obj, angle):
        if angle == 0: return
        #print 'attempt rotate'
        Display._acquireLock()
        #print 'rotate'
        parts = Display.partDict[obj]
        #assert(parts)
        graphicsUtils.rotate_by(parts, angle)
        Display._releaseLock()
                
    @staticmethod
    def _getBeliefSquareColor(color, value):
        value = min(1.0, value * 15)
        saturation = value
        hue = Display.COLOR_HUES[color]
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, 1.0)
        color = graphicsUtils.formatColor(r, g, b)
        return color        
    
    @staticmethod
    def _isVisible(value):
        return value >= Display.VISIBLE_CUTTOFF
    
    @staticmethod
    def _updateBeliefSquare(r, c, value, colorName):
        part = Display.beliefParts[r][c]
        if part == None: return
        oldValue = Display.beliefValue[r][c]
        oldColor = Display.beliefColor[r][c]
        wasVisible = Display._isVisible(oldValue)
        isVisible = Display._isVisible(value) 
        if not isVisible: value = 0.0
        if oldColor != colorName and oldValue >= value: return
        if not isVisible and not wasVisible: return
        color = Display._getBeliefSquareColor(colorName, value)
        graphicsUtils.changeColor(part, color)
        Display.beliefValue[r][c] = value
        Display.beliefColor[r][c] = colorName
        
    @staticmethod
    def _acquireLock():
        return
        #print 'acquire'
        return Display.graphicsLock.acquire()
    
    @staticmethod
    def _releaseLock():
        return
        #print 'release'
        return Display.graphicsLock.release()
     
    ####################################
    # Depreicated
    ####################################
        
    @staticmethod
    def _remove(obj):
        parts = Display.partDict[obj]
        graphicsUtils.remove_from_screen(parts);
        
    @staticmethod
    def redrawObservations(observations):
        raise Exception('depreicated')
        for obs in Display.observations:
            Display._remove(obs)
        for obs in observations:
            Display.drawObservation(obs)
        Display.observations = observations
