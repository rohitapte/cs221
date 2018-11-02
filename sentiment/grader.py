#!/usr/bin/python

import graderUtil
import util
import time
from util import *

grader = graderUtil.Grader()
submission = grader.load('submission')

############################################################
# Problem 1: warmup
############################################################

grader.addManualPart('1a', maxPoints=2, description='simulate SGD')
grader.addManualPart('1b', maxPoints=2, description='create small dataset')

############################################################
# Problem 2: predicting movie ratings
############################################################

grader.addManualPart('2a', maxPoints=2, description='loss')
grader.addManualPart('2b', maxPoints=3, description='gradient')
grader.addManualPart('2c', maxPoints=3, description='smallest magnitude')
grader.addManualPart('2d', maxPoints=3, description='largest magnitude')
grader.addManualPart('2e', maxPoints=3, description='linear regression')

############################################################
# Problem 3: sentiment classification
############################################################

### 3a

# Basic sanity check for feature extraction
def test3a0():
    ans = {"a":2, "b":1}
    grader.requireIsEqual(ans, submission.extractWordFeatures("a b a"))
grader.addBasicPart('3a-0-basic', test3a0, maxSeconds=1, description="basic test")

def test3a1():
    random.seed(42)
    for i in range(10):
        sentence = ' '.join([random.choice(['a', 'aa', 'ab', 'b', 'c']) for _ in range(100)])
    submission_ans = submission.extractWordFeatures(sentence)
grader.addHiddenPart('3a-1-hidden', test3a1, maxSeconds=1, description="test multiple instances of the same word in a sentence")

### 3b

def test3b0():
    trainExamples = (("hello world", 1), ("goodnight moon", -1))
    testExamples = (("hello", 1), ("moon", -1))
    featureExtractor = submission.extractWordFeatures
    weights = submission.learnPredictor(trainExamples, testExamples, featureExtractor, numIters=20, eta=0.01)
    grader.requireIsGreaterThan(0, weights["hello"])
    grader.requireIsLessThan(0, weights["moon"])
grader.addBasicPart('3b-0-basic', test3b0, maxSeconds=1, description="basic sanity check for learning correct weights on two training and testing examples each")

def test3b1():
    trainExamples = (("hi bye", 1), ("hi hi", -1))
    testExamples = (("hi", -1), ("bye", 1))
    featureExtractor = submission.extractWordFeatures
    weights = submission.learnPredictor(trainExamples, testExamples, featureExtractor, numIters=20, eta=0.01)
    grader.requireIsLessThan(0, weights["hi"])
    grader.requireIsGreaterThan(0, weights["bye"])
grader.addBasicPart('3b-1-basic', test3b1, maxSeconds=1, description="test correct overriding of positive weight due to one negative instance with repeated words")

def test3b2():
    trainExamples = readExamples('polarity.train')
    devExamples = readExamples('polarity.dev')
    featureExtractor = submission.extractWordFeatures
    weights = submission.learnPredictor(trainExamples, devExamples, featureExtractor, numIters=20, eta=0.01)
    outputWeights(weights, 'weights')
    outputErrorAnalysis(devExamples, featureExtractor, weights, 'error-analysis')  # Use this to debug
    trainError = evaluatePredictor(trainExamples, lambda(x) : (1 if dotProduct(featureExtractor(x), weights) >= 0 else -1))
    devError = evaluatePredictor(devExamples, lambda(x) : (1 if dotProduct(featureExtractor(x), weights) >= 0 else -1))
    print "Official: train error = %s, dev error = %s" % (trainError, devError)
    grader.requireIsLessThan(0.04, trainError)
    grader.requireIsLessThan(0.30, devError)
grader.addBasicPart('3b-2-basic', test3b2, maxPoints=2, maxSeconds=8, description="test classifier on real polarity dev dataset")

### 3c

def test3c0():
    weights = {"hello":1, "world":1}
    data = submission.generateDataset(5, weights)
    for datapt in data:
        grader.requireIsEqual((util.dotProduct(datapt[0], weights) >= 0), (datapt[1] == 1))
grader.addBasicPart('3c-0-basic', test3c0, maxSeconds=1, description="test correct generation of random dataset labels")

def test3c1():
    weights = {}
    for i in range(100):
        weights[str(i + 0.1)] = 1
    data = submission.generateDataset(100, weights)
    for datapt in data:
        grader.requireIsEqual(False, dotProduct(datapt[0], weights) == 0)
grader.addBasicPart('3c-1-basic', test3c1, maxSeconds=1, description="test that the randomly generated example actually coincides with the given weights")

### 3d

grader.addManualPart('3d', maxPoints=2, description='error analysis')

### 3e

def test3e0():
    fe = submission.extractCharacterFeatures(3)
    sentence = "hello world"
    ans = {"hel":1, "ell":1, "llo":1, "low":1, "owo":1, "wor":1, "orl":1, "rld":1}
    grader.requireIsEqual(ans, fe(sentence))
grader.addBasicPart('3e-0-basic', test3e0, maxSeconds=1, description="test basic character n-gram features")

def test3e1():
    random.seed(42)
    for i in range(10):
        sentence = ' '.join([random.choice(['a', 'aa', 'ab', 'b', 'c']) for _ in range(100)])
        for n in range(1, 4):
            submission_ans = submission.extractCharacterFeatures(n)(sentence)
grader.addHiddenPart('3e-1-hidden', test3e1, maxSeconds=1, description="test feature extraction on repeated character n-grams")

### 3f

grader.addManualPart('3f', maxPoints=3, description='explain value of n-grams')

############################################################
# Problem 4: clustering
############################################################

grader.addManualPart('4a', maxPoints=2, description='simulating 2-means')

# basic test for k-means
def test4b0():
    x1 = {0:0, 1:0}
    x2 = {0:0, 1:1}
    x3 = {0:0, 1:2}
    x4 = {0:0, 1:3}
    x5 = {0:0, 1:4}
    x6 = {0:0, 1:5}
    examples = [x1, x2, x3, x4, x5, x6]
    centers, assignments, totalCost = submission.kmeans(examples, 2, maxIters=10)
    # (there are two stable centroid locations)
    grader.requireIsEqual(True, round(totalCost, 3)==4 or round(totalCost, 3)==5.5 or round(totalCost, 3)==5.0)
grader.addBasicPart('4b-0-basic', test4b0, maxSeconds=1, description="test basic k-means on hardcoded datapoints")

def test4b1():
    K = 6
    bestCenters = None
    bestAssignments = None
    bestTotalCost = None
    examples = generateClusteringExamples(numExamples=1000, numWordsPerTopic=3, numFillerWords=1000)
    centers, assignments, totalCost = submission.kmeans(examples, K, maxIters=100)
grader.addHiddenPart('4b-1-hidden', test4b1, maxPoints=1, maxSeconds=3, description="test stability of cluster assignments")

def test4b2():
    K = 6
    bestCenters = None
    bestAssignments = None
    bestTotalCost = None
    examples = generateClusteringExamples(numExamples=1000, numWordsPerTopic=3, numFillerWords=1000)
    centers, assignments, totalCost = submission.kmeans(examples, K, maxIters=100)
grader.addHiddenPart('4b-2-hidden', test4b2, maxPoints=1, maxSeconds=3, description="test stability of cluster locations")

def test4b3():
    K = 6
    bestCenters = None
    bestAssignments = None
    bestTotalCost = None
    examples = generateClusteringExamples(numExamples=10000, numWordsPerTopic=3, numFillerWords=10000)
    centers, assignments, totalCost = submission.kmeans(examples, K, maxIters=100)
    grader.requireIsLessThan(10e6, totalCost)
grader.addHiddenPart('4b-3-basic', test4b3, maxPoints=2, maxSeconds=4, description="make sure the code runs fast enough")

grader.addManualPart('4c', maxPoints=5, description='handling same-cluster constraints')

grader.grade()
