from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
  """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
  """
  def __init__(self):
    self.lastPositions = []
    self.dc = None


  def getAction(self, gameState):
    """
    getAction chooses among the best options according to the evaluation function.

    getAction takes a GameState and returns some Directions.X for some X in the set {North, South, West, East, Stop}
    ------------------------------------------------------------------------------
    Description of GameState and helper functions:

    A GameState specifies the full game state, including the food, capsules,
    agent configurations and score changes. In this function, the |gameState| argument
    is an object of GameState class. Following are a few of the helper methods that you
    can use to query a GameState object to gather information about the present state
    of Pac-Man, the ghosts and the maze.

    gameState.getLegalActions():
        Returns the legal actions for the agent specified. Returns Pac-Man's legal moves by default.

    gameState.generateSuccessor(agentIndex, action):
        Returns the successor state after the specified agent takes the action.
        Pac-Man is always agent 0.

    gameState.getPacmanState():
        Returns an AgentState object for pacman (in game.py)
        state.configuration.pos gives the current position
        state.direction gives the travel vector

    gameState.getGhostStates():
        Returns list of AgentState objects for the ghosts

    gameState.getNumAgents():
        Returns the total number of agents in the game

    gameState.getScore():
        Returns the score corresponding to the current state of the game


    The GameState class is defined in pacman.py and you might want to look into that for
    other helper methods, though you don't need to.
    """
    # Collect legal moves and successor states
    legalMoves = gameState.getLegalActions()

    # Choose one of the best actions
    scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
    bestScore = max(scores)
    bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
    chosenIndex = random.choice(bestIndices) # Pick randomly among the best


    return legalMoves[chosenIndex]

  def evaluationFunction(self, currentGameState, action):
    """
    The evaluation function takes in the current and proposed successor
    GameStates (pacman.py) and returns a number, where higher numbers are better.

    The code below extracts some useful information from the state, like the
    remaining food (oldFood) and Pacman position after moving (newPos).
    newScaredTimes holds the number of moves that each ghost will remain
    scared because of Pacman having eaten a power pellet.
    """
    # Useful information you can extract from a GameState (pacman.py)
    successorGameState = currentGameState.generatePacmanSuccessor(action)
    newPos = successorGameState.getPacmanPosition()
    oldFood = currentGameState.getFood()
    newGhostStates = successorGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

    return successorGameState.getScore()


def scoreEvaluationFunction(currentGameState):
  """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
  """
  return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
  """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
  """

  def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
    self.index = 0 # Pacman is always agent index 0
    self.evaluationFunction = util.lookup(evalFn, globals())
    self.depth = int(depth)

######################################################################################
# Problem 1b: implementing minimax

class MinimaxAgent(MultiAgentSearchAgent):
  """
    Your minimax agent (problem 1)
  """

  def getAction(self, gameState):
    """
      Returns the minimax action from the current gameState using self.depth
      and self.evaluationFunction. Terminal states can be found by one of the following:
      pacman won, pacman lost or there are no legal moves.

      Here are some method calls that might be useful when implementing minimax.

      gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

      Directions.STOP:
        The stop direction, which is always legal

      gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

      gameState.getNumAgents():
        Returns the total number of agents in the game

      gameState.getScore():
        Returns the score corresponding to the current state of the game

      gameState.isWin():
        Returns True if it's a winning state

      gameState.isLose():
        Returns True if it's a losing state

      self.depth:
        The depth to which search should continue

    """

    # BEGIN_YOUR_CODE (our solution is 26 lines of code, but don't worry if you deviate from this)
    #define max and min value functions
    def maxValue(gameState,agentIndex,currentDepth):
      #returns (value,action) tuple
      #default value is -inf and default action is to STOP (i.e. do nothing)
      v=(float("-inf"),Directions.STOP)
      nextAgent=(agentIndex + 1)
      for action in gameState.getLegalActions(agentIndex):
        nextGameState=gameState.generateSuccessor(agentIndex,action)
        newVal=minimaxValue(nextGameState,nextAgent,currentDepth)
        if newVal>v[0]:
          v=(newVal,action)
      return v
    def minValue(gameState,agentIndex,currentDepth):
      #returns (value,action) tuple
      #default value is +inf and default action is to STOP (i.e. do nothing)
      v=(float("inf"), Directions.STOP)
      nextAgent=(agentIndex+1)
      if nextAgent==gameState.getNumAgents():
        nextAgent=0
        currentDepth-=1
      for action in gameState.getLegalActions(agentIndex):
        nextGameState=gameState.generateSuccessor(agentIndex,action)
        newVal=minimaxValue(nextGameState,nextAgent,currentDepth)
        if newVal<v[0]:
          v=(newVal,action)
      return v
    def minimaxValue(gameState,agentIndex,currentDepth):
      if gameState.isLose() or gameState.isWin():
        return gameState.getScore()
      if currentDepth<=0:
        return self.evaluationFunction(gameState)
      if agentIndex==0:
        return maxValue(gameState,agentIndex,currentDepth)[0]
      else:
        return minValue(gameState,agentIndex,currentDepth)[0]
    return maxValue(gameState,0,self.depth)[1]
    # END_YOUR_CODE

######################################################################################
# Problem 2a: implementing alpha-beta

class AlphaBetaAgent(MultiAgentSearchAgent):
  """
    Your minimax agent with alpha-beta pruning (problem 2)
  """

  def getAction(self, gameState):
    """
      Returns the minimax action using self.depth and self.evaluationFunction
    """

    # BEGIN_YOUR_CODE (our solution is 49 lines of code, but don't worry if you deviate from this)
    def maxValue(gameState,agentIndex,currentDepth,alpha,beta):
      # returns (value,action) tuple
      # default value is -inf and default action is to STOP (i.e. do nothing)
      v=(float("-inf"),Directions.STOP)
      nextAgent=(agentIndex+1)
      for action in gameState.getLegalActions(agentIndex):
        nextGameState=gameState.generateSuccessor(agentIndex,action)
        newVal=minimaxValue(nextGameState,nextAgent,currentDepth,alpha,beta)
        if newVal>v[0]:
          v=(newVal,action)
        alpha=max(alpha,v[0])
        if v[0]>beta:
          return v

      return v

    def minValue(gameState,agentIndex,currentDepth,alpha,beta):
      # returns (value,action) tuple
      # default value is +inf and default action is to STOP (i.e. do nothing)
      v=(float("inf"),Directions.STOP)
      nextAgent=(agentIndex+1)
      if nextAgent==gameState.getNumAgents():
        nextAgent=0
        currentDepth-=1
      for action in gameState.getLegalActions(agentIndex):
        nextGameState=gameState.generateSuccessor(agentIndex,action)
        newVal=minimaxValue(nextGameState,nextAgent,currentDepth,alpha,beta)
        if newVal<v[0]:
          v=(newVal,action)
        beta=min(beta,v[0])
        if v[0]<alpha:
          return v
      return v

    def minimaxValue(gameState,agentIndex,currentDepth,alpha,beta):
      if gameState.isLose() or gameState.isWin():
        return gameState.getScore()
      if currentDepth<=0:
        return self.evaluationFunction(gameState)
      if agentIndex==0:
        return maxValue(gameState, agentIndex, currentDepth,alpha,beta)[0]
      else:
        return minValue(gameState,agentIndex,currentDepth,alpha,beta)[0]

    return maxValue(gameState,0,self.depth,float("-inf"),float("inf"))[1]
    # END_YOUR_CODE

######################################################################################
# Problem 3b: implementing expectimax

class ExpectimaxAgent(MultiAgentSearchAgent):
  """
    Your expectimax agent (problem 3)
  """

  def getAction(self, gameState):
    """
      Returns the expectimax action using self.depth and self.evaluationFunction

      All ghosts should be modeled as choosing uniformly at random from their
      legal moves.
    """

    # BEGIN_YOUR_CODE (our solution is 25 lines of code, but don't worry if you deviate from this)
    def maxValue(gameState,agentIndex,currentDepth):
      #returns (value,action) tuple
      #default value is -inf and default action is to STOP (i.e. do nothing)
      v=(float("-inf"),Directions.STOP)
      nextAgent=(agentIndex+1)
      for action in gameState.getLegalActions(agentIndex):
        nextGameState=gameState.generateSuccessor(agentIndex,action)
        newVal=minimaxValue(nextGameState,nextAgent,currentDepth)
        if newVal>v[0]:
          v=(newVal,action)
      return v
    def expectimaxValue(gameState,agentIndex,currentDepth):
      #returns (value,action) tuple
      #default value is +inf and default action is to STOP (i.e. do nothing)
      v=[0.0]
      nextAgent=(agentIndex+1)
      if nextAgent==gameState.getNumAgents():
        nextAgent=0
        currentDepth-=1
      for action in gameState.getLegalActions(agentIndex):
        nextGameState=gameState.generateSuccessor(agentIndex,action)
        newVal=minimaxValue(nextGameState,nextAgent,currentDepth)
        v.append(newVal)
      v.pop(0)
      return sum(v)/len(v)
    def minimaxValue(gameState,agentIndex,currentDepth):
      if gameState.isLose() or gameState.isWin():
        return gameState.getScore()
      if currentDepth<=0:
        return self.evaluationFunction(gameState)
      if agentIndex==0:
        return maxValue(gameState,agentIndex,currentDepth)[0]
      else:
        return expectimaxValue(gameState,agentIndex,currentDepth)
    return maxValue(gameState,0,self.depth)[1]
    # END_YOUR_CODE

######################################################################################
# Problem 4a (extra credit): creating a better evaluation function

def betterEvaluationFunction(currentGameState):
  """
    Your extreme, unstoppable evaluation function (problem 4).

    DESCRIPTION: <write something here so we know what you did>
  """

  # BEGIN_YOUR_CODE (our solution is 26 lines of code, but don't worry if you deviate from this)
  currentPacmanPosition = currentGameState.getPacmanPosition()
  food = currentGameState.getFood()
  foodAsList = food.asList()
  ghostStates = currentGameState.getGhostStates()
  huntingGhosts = []
  scaredGhosts = []
  scaredTimes=[]
  for ghost in ghostStates:
    if ghost.scaredTimer:
      scaredTimes.append(ghost.scaredTimer)
      scaredGhosts.append(ghost)
    else:
      huntingGhosts.append(ghost)
  capsules=currentGameState.getCapsules()
  remainingFood=len(foodAsList)
  remainingCapsules=len(capsules)
  currentScore = currentGameState.getScore()
  distToClosestFood = float("inf")
  invDistanceToClosestFood=0
  for item in foodAsList:
    dist = util.manhattanDistance(currentPacmanPosition, item)
    if dist < distToClosestFood:
      distToClosestFood = dist

  if distToClosestFood>0:
    invDistanceToClosestFood=1/distToClosestFood
  if len(foodAsList)<3:
    invDistanceToClosestFood=100000
  if len(foodAsList)==1:
    invDistToClosestFood=500000
  distToClosestCapsules = float("inf")
  invDistToClosestCapsule=0
  if remainingCapsules == 0:
    distToClosestCapsules = 0
  for item in capsules:
    dist = util.manhattanDistance(currentPacmanPosition, item)
    if dist < distToClosestCapsules:
      distToClosestCapsules = dist
  if distToClosestCapsules>0:
    invDistToClosestCapsule=1/distToClosestCapsules
  distToHuntingGhost=float("inf")
  for ghost in huntingGhosts:
    dist = util.manhattanDistance(currentPacmanPosition, ghost.getPosition())
    if dist < distToHuntingGhost:
      distToHuntingGhost = dist
  #distToHuntingGhost=max(3,distToHuntingGhost)
  if len(scaredGhosts) == 0:
    distToScaredGhost = 0
    scaredTime=0
  else:
    distToScaredGhost = float("inf")
    for ghost in scaredGhosts:
      dist = util.manhattanDistance(currentPacmanPosition, ghost.getPosition())
      if dist < distToScaredGhost:
        distToScaredGhost = dist
    scaredTime=scaredTimes[0]
  invDistToHuntingGhost = 0
  if distToHuntingGhost > 0:
    invDistToHuntingGhost = 1.0 / distToHuntingGhost
  invDistToScaredGhost = 0
  if distToScaredGhost > 0:
    invDistToScaredGhost = 1.0 / distToScaredGhost
  score=currentGameState.getScore()\
        -2*invDistToHuntingGhost\
        +15*scaredTime*invDistToScaredGhost\
        -2*remainingFood\
        -3*invDistToClosestCapsule\
        -1*distToClosestFood
  return score
  #return currentGameState.getScore()
  # END_YOUR_CODE

# Abbreviation
better = betterEvaluationFunction
