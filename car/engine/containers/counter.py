'''
Created on Jun 13, 2013

@author: chrispiech
'''

class Counter(object):
    
    def __init__(self):
        self.count = 0
        self.total = 0.0
        
    def addValue(self, value):
        self.total += value
        self.count += 1
        
    def getMean(self):
        return self.total / self.count