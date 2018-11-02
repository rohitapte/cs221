#!/usr/bin/env python
import random, sys

from engine.const import Const
import graderUtil
import util
import collections
import copy

grader = graderUtil.Grader()
submission = grader.load('submission')

# General Notes:
# - Unless otherwise specified, all parts count for only a single point.
# - Unless otherwise specified, all parts time out in 1 second.

############################################################
# Problem 1: Warmup

grader.addManualPart('1a', 2, description="1a writeup")
grader.addManualPart('1b', 2, description="1b writeup")
grader.addManualPart('1c', 3, description="1c writeup")

############################################################
# Problem 2: Emission probabilities

def test2a():
    ei = submission.ExactInference(10, 10)
    ei.skipElapse = True ### ONLY FOR PROBLEM 2
    ei.observe(55, 193, 200)
    grader.requireIsEqual(0.030841805296, ei.belief.getProb(0, 0))
    grader.requireIsEqual(0.00073380582967, ei.belief.getProb(2, 4))
    grader.requireIsEqual(0.0269846478431, ei.belief.getProb(4, 7))
    grader.requireIsEqual(0.0129150762582, ei.belief.getProb(5, 9))

    ei.observe(80, 250, 150)
    grader.requireIsEqual(0.00000261584106271, ei.belief.getProb(0, 0))
    grader.requireIsEqual(0.000924335357194, ei.belief.getProb(2, 4))
    grader.requireIsEqual(0.0295673460685, ei.belief.getProb(4, 7))
    grader.requireIsEqual(0.000102360275238, ei.belief.getProb(5, 9))

grader.addBasicPart('2a-0-basic', test2a, 2, description="2a basic test for emission probabilities")

def test2a_1(): # test whether they put the pdf in the correct order
    oldpdf = util.pdf
    del util.pdf
    def pdf(a, b, c): # be super rude to them! You can't swap a and c now!
      return a + b
    util.pdf = pdf

    ei = submission.ExactInference(10, 10)
    ei.skipElapse = True ### ONLY FOR PROBLEM 2
    ei.observe(55, 193, 200)

    ei.observe(80, 250, 150)
    util.pdf = oldpdf # replace the old pdf

grader.addHiddenPart('2a-1-hidden',test2a_1, 2, description="2a test ordering of pdf")

def test2a_2():
    random.seed(10)

    ei = submission.ExactInference(10, 10)
    ei.skipElapse = True ### ONLY FOR PROBLEM 2

    N = 50
    p_values = []
    for i in range(N):
      a = int(random.random() * 300)
      b = int(random.random() * 5)
      c = int(random.random() * 300)

      ei.observe(a, b, c)

      for d in range(10):
        for e in range(10):
          p_values.append(ei.belief.getProb(d, e))

grader.addHiddenPart('2a-2-hidden', test2a_2, 3, description="2a advanced test for emission probabilities")

############################################################
# Problem 3: Transition probabilities

def test3a():
    ei = submission.ExactInference(30, 13)
    ei.elapseTime()
    grader.requireIsEqual(0.0105778989624, ei.belief.getProb(16, 6))
    grader.requireIsEqual(0.00250560512469, ei.belief.getProb(18, 7))
    grader.requireIsEqual(0.0165024135157, ei.belief.getProb(21, 7))
    grader.requireIsEqual(0.0178755550388, ei.belief.getProb(8, 4))

    ei.elapseTime()
    grader.requireIsEqual(0.0138327373012, ei.belief.getProb(16, 6))
    grader.requireIsEqual(0.00257237608713, ei.belief.getProb(18, 7))
    grader.requireIsEqual(0.0232612833688, ei.belief.getProb(21, 7))
    grader.requireIsEqual(0.0176501876956, ei.belief.getProb(8, 4))

grader.addBasicPart('3a-0-basic', test3a, 2, description="test correctness of elapseTime()")

def test3a_1i(): # stress test their elapseTime
    A = 30
    B = 30
    random.seed(15)
    ei = submission.ExactInference(A, B)

    N1 = 20
    N2 = 400
    p_values = []
    for i in range(N1):
      ei.elapseTime()
      for i in range(N2):
        d = int(random.random() * A)
        e = int(random.random() * B)
        p_values.append(ei.belief.getProb(d, e))


grader.addHiddenPart('3a-1i-hidden',test3a_1i, 2, description="advanced test for transition probabilities, strict time limit", maxSeconds=5)

def test3a_1ii(): # stress test their elapseTime, making sure they didn't specifically use lombard
    random.seed(15)

    oldworld = Const.WORLD
    Const.WORLD = 'small' # well... they may have made it specific for lombard

    A = 30
    B = 30
    ei = submission.ExactInference(A, B)

    N1 = 20
    N2 = 40
    p_values = []
    for i in range(N1):
      ei.elapseTime()
      for i in range(N2):
        d = int(random.random() * A)
        e = int(random.random() * B)
        p_values.append(ei.belief.getProb(d, e))
    Const.WORLD = oldworld # set it back to what's likely lombard


grader.addHiddenPart('3a-1ii-hidden',test3a_1ii, 1, description="3a test for transition probabilities on other maps, loose time limit", maxSeconds=20)

def test3a_2(): # let's test them together! Very important
    random.seed(20)

    A = 30
    B = 30
    ei = submission.ExactInference(A, B)

    N1 = 20
    N2 = 400
    p_values = []
    for i in range(N1):
      ei.elapseTime()

      a = int(random.random() * 5 * A)
      b = int(random.random() * 5)
      c = int(random.random() * 5 * A)

      ei.observe(a, b, c)
      for i in range(N2):
        d = int(random.random() * A)
        e = int(random.random() * B)
        p_values.append(ei.belief.getProb(d, e))


grader.addHiddenPart('3a-2-hidden', test3a_2, 2, description="advanced test for emission AND transition probabilities, strict time limit", maxSeconds=5)


############################################################
# Problem 4: Particle filtering

def test4a_0():
    random.seed(3)

    pf = submission.ParticleFilter(30, 13)

    pf.observe(555, 193, 800)

    grader.requireIsEqual(0.015, pf.belief.getProb(20, 4))
    grader.requireIsEqual(0.135, pf.belief.getProb(21, 5))
    grader.requireIsEqual(0.85, pf.belief.getProb(22, 6))
    grader.requireIsEqual(0.0, pf.belief.getProb(8, 4))

    pf.observe(525, 193, 830)

    grader.requireIsEqual(0.0, pf.belief.getProb(20, 4))
    grader.requireIsEqual(0.01, pf.belief.getProb(21, 5))
    grader.requireIsEqual(0.99, pf.belief.getProb(22, 6))
    grader.requireIsEqual(0.0, pf.belief.getProb(8, 4))


grader.addBasicPart('4a-0-basic', test4a_0, 2, description="4a basic test for PF observe")

def test4a_1():
    random.seed(3)
    pf = submission.ParticleFilter(30, 13)
    grader.requireIsEqual(69, len(pf.particles)) # This should not fail unless your code changed the random initialization code.

    pf.elapseTime()
    grader.requireIsEqual(200, sum(pf.particles.values())) # Do not lose particles
    grader.requireIsEqual(66, len(pf.particles)) # Most particles lie on the same (row, col) locations

    grader.requireIsEqual(9, pf.particles[(3,9)])
    grader.requireIsEqual(0, pf.particles[(2,10)])
    grader.requireIsEqual(7, pf.particles[(8,4)])
    grader.requireIsEqual(6, pf.particles[(12,6)])
    grader.requireIsEqual(1, pf.particles[(7,8)])
    grader.requireIsEqual(1, pf.particles[(11,6)])
    grader.requireIsEqual(0, pf.particles[(18,7)])
    grader.requireIsEqual(1, pf.particles[(20,5)])

    pf.elapseTime()
    grader.requireIsEqual(200, sum(pf.particles.values())) # Do not lose particles
    grader.requireIsEqual(61, len(pf.particles)) # Slightly more particles lie on the same (row, col) locations

    grader.requireIsEqual(6, pf.particles[(3,9)])
    grader.requireIsEqual(0, pf.particles[(2,10)]) # 0 --> 0
    grader.requireIsEqual(2, pf.particles[(8,4)])
    grader.requireIsEqual(5, pf.particles[(12,6)])
    grader.requireIsEqual(2, pf.particles[(7,8)])
    grader.requireIsEqual(1, pf.particles[(11,6)])
    grader.requireIsEqual(1, pf.particles[(18,7)]) # 0 --> 1
    grader.requireIsEqual(0, pf.particles[(20,5)]) # 1 --> 0

grader.addBasicPart('4a-1-basic', test4a_1, 2, description="4a basic test for PF elapseTime")

def test4a_2():
    random.seed(3)
    pf = submission.ParticleFilter(30, 13)
    grader.requireIsEqual(69, len(pf.particles)) # This should not fail unless your code changed the random initialization code.

    pf.elapseTime()
    grader.requireIsEqual(66, len(pf.particles)) # Most particles lie on the same (row, col) locations
    pf.observe(555, 193, 800)

    grader.requireIsEqual(200, sum(pf.particles.values())) # Do not lose particles
    grader.requireIsEqual(3, len(pf.particles)) # Most particles lie on the same (row, col) locations
    grader.requireIsEqual(0.025, pf.belief.getProb(20, 4))
    grader.requireIsEqual(0.035, pf.belief.getProb(21, 5))
    grader.requireIsEqual(0.0, pf.belief.getProb(21, 6))
    grader.requireIsEqual(0.94, pf.belief.getProb(22, 6))
    grader.requireIsEqual(0.0, pf.belief.getProb(22, 7))

    pf.elapseTime()
    grader.requireIsEqual(5, len(pf.particles)) # Most particles lie on the same (row, col) locations

    pf.observe(660, 193, 50)
    grader.requireIsEqual(0.0, pf.belief.getProb(20, 4))
    grader.requireIsEqual(0.0, pf.belief.getProb(21, 5))
    grader.requireIsEqual(0.095, pf.belief.getProb(21, 6))
    grader.requireIsEqual(0.0, pf.belief.getProb(22, 6))
    grader.requireIsEqual(0.905, pf.belief.getProb(22, 7))

grader.addBasicPart('4a-2-basic', test4a_2, 3, description="4a basic test for PF observe AND elapseTime")

def test4a_3i(): # basic observe stress test
    random.seed(34)
    A = 30
    B = 30
    pf = submission.ParticleFilter(A, B)

    N = 50
    p_values = []
    for i in range(N):
      SEED_MODE = 1000 # setup the random seed for fairness
      seed = int(random.random() * SEED_MODE)
      nextSeed = int(random.random() * SEED_MODE)

      a = int(random.random() * 30)
      b = int(random.random() * 5)
      c = int(random.random() * 30)

      random.seed(seed)
      pf.observe(a, b, c)
      random.seed(seed)
      for d in range(A):
        for e in range(B):
          p_values.append(pf.belief.getProb(d, e))
      random.seed(nextSeed)



grader.addHiddenPart('4a-3i-hidden',test4a_3i,2, description="4a advanced test for PF observe")

def test4a_3ii(): # observe stress test with whether they put the pdf in the correct order or not
    random.seed(34)

    oldpdf = util.pdf
    del util.pdf
    def pdf(a, b, c): # You can't swap a and c now!
      return a + b
    util.pdf = pdf

    A = 30
    B = 30
    random.seed(34)
    pf = submission.ParticleFilter(A, B)

    N = 50
    p_values = []
    for i in range(N):
      SEED_MODE = 1000 # setup the random seed for fairness
      seed = int(random.random() * SEED_MODE)
      nextSeed = int(random.random() * SEED_MODE)

      a = int(random.random() * 30)
      b = int(random.random() * 5)
      c = int(random.random() * 30)

      random.seed(seed)
      pf.observe(a, b, c)
      for d in range(A):
        for e in range(B):
          p_values.append(pf.belief.getProb(d, e))
      random.seed(nextSeed)


    util.pdf = oldpdf # fix the pdf

grader.addHiddenPart('4a-3ii-hidden',test4a_3ii, 2, description="4a test for pdf ordering")

def test4a_4():
    A = 30
    B = 30
    random.seed(35)
    pf = submission.ParticleFilter(A, B)

    N1 = 20
    N2 = 400
    p_values = []
    for i in range(N1):
      SEED_MODE = 1000 # setup the random seed for fairness
      seed = int(random.random() * SEED_MODE)
      nextSeed = int(random.random() * SEED_MODE)

      random.seed(seed)
      pf.elapseTime()

      for i in range(N2):
        d = int(random.random() * A)
        e = int(random.random() * B)
        p_values.append(pf.belief.getProb(d, e))
      random.seed(nextSeed)


grader.addHiddenPart('4a-4-hidden',test4a_4, 3, description="advanced test for PF elapseTime")

def test4a_5():
    A = 30
    B = 30
    random.seed(36)
    pf = submission.ParticleFilter(A, B)

    N1 = 20
    N2 = 400
    p_values = []
    for i in range(N1):
      SEED_MODE = 1000 # setup the random seed for fairness
      seed = int(random.random() * SEED_MODE)
      seed2 = int(random.random() * SEED_MODE)
      nextSeed = int(random.random() * SEED_MODE)

      random.seed(seed)
      pf.elapseTime()

      a = int(random.random() * 5 * A)
      b = int(random.random() * 5)
      c = int(random.random() * 5 * A)

      random.seed(seed2)
      pf.observe(a, b, c)
      for i in range(N2):
        d = int(random.random() * A)
        e = int(random.random() * B)
        p_values.append(pf.belief.getProb(d, e))
      random.seed(nextSeed)


grader.addHiddenPart('4a-5-hidden',test4a_5, 4, description="advanced test for PF observe AND elapseTime")

### Problem 5: which car is it?

grader.addManualPart('5a', 5, description="conditional distribution")
grader.addManualPart('5b', 4, description="number of assignments K!")
grader.addManualPart('5c', 2, description="treewidth")
grader.addManualPart('5d', 6, extraCredit=True, description="efficient algorithm for wrap around")

grader.grade()
