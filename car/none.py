'''
Licensing Information: Please do not distribute or publish solutions to this
project. You are free to use and extend Driverless Car for educational
purposes. The Driverless Car project was developed at Stanford, primarily by
Chris Piech (piech@cs.stanford.edu). It was inspired by the Pacman projects.
'''
from engine.const import Const
import util, math

# Class: NoInference
# ---------------------
# Maintain and update a belief distribution over the probability of a car
# being in a tile using exact updates (correct, but slow times).
class NoInference(object):
    
    # Function: Init
    # --------------
    # Constructer that initializes an ExactInference object which has
    # numRows x numCols number of tiles.
    def __init__(self, numRows, numCols):
        self.belief = util.Belief(numRows, numCols)
   
    # Function: Observe
    # -----------------
    # Updates beliefs based on the distance observation and your agents position.
    # The noisyDistance is a gaussian distribution with mean of the true distance
    # and std = Const.SONAR_STD. The variable agentX is the x location of 
    # your car (not the one you are tracking) and agentY is your y location.
    def observe(self, agentX, agentY, observedDist):
        pass

    # Function: Elapse Time
    # ---------------------
    # Update your inference to handle the passing of one heartbeat. Use the
    # transition probability you created in Learner  
    def elapseTime(self):
        pass
      
    # Function: Get Belief
    # ---------------------
    # Returns your belief of the probability that the car is in each tile. Your
    # belief probabilities should sum to 1.    
    def getBelief(self):
        return self.belief
    
