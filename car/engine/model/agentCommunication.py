class AgentCommunication(object):
    
    def __init__(self):
        self.intersectionClaims = {}
        
    
    def claimIntersection(self, intersection, car):
        if intersection in self.intersectionClaims: 
            claimee = self.intersectionClaims[intersection]
            if claimee != car: return False
        self.intersectionClaims[intersection] = car
        return True
    
    def addAgents(self, agentList):
        self.agents = agentList
    
    def getAgents(self):
        return self.agents
    
    def unclaimIntersection(self, car):
        toRelease = []
        for inter in self.intersectionClaims:
            claimee = self.intersectionClaims[inter]
            if claimee == car:
                toRelease.append(inter)
        for inter in toRelease:
            del self.intersectionClaims[inter]