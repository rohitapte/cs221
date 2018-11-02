#!/usr/bin/python

import random
import collections
import math
import sys
from util import *

############################################################
# Problem 3: binary classification
############################################################

############################################################
# Problem 3a: feature extraction

def extractWordFeatures(x):
    """
    Extract word features for a string x. Words are delimited by
    whitespace characters only.
    @param string x: 
    @return dict: feature vector representation of x.
    Example: "I am what I am" --> {'I': 2, 'am': 2, 'what': 1}
    """
    # BEGIN_YOUR_CODE (our solution is 4 lines of code, but don't worry if you deviate from this)
    wordDict=collections.defaultdict(float)
    for word in x.split():
        wordDict[word]+=1
    return wordDict
    # END_YOUR_CODE

############################################################
# Problem 3b: stochastic gradient descent

def learnPredictor(trainExamples, testExamples, featureExtractor, numIters, eta):
    '''
    Given |trainExamples| and |testExamples| (each one is a list of (x,y)
    pairs), a |featureExtractor| to apply to x, and the number of iterations to
    train |numIters|, the step size |eta|, return the weight vector (sparse
    feature vector) learned.

    You should implement stochastic gradient descent.

    Note: only use the trainExamples for training!
    You should call evaluatePredictor() on both trainExamples and testExamples
    to see how you're doing as you learn after each iteration.
    '''
    weights = {}  # feature => weight
    # BEGIN_YOUR_CODE (our solution is 12 lines of code, but don't worry if you deviate from this)
    def predict(x):
        phi=featureExtractor(x)
        if dotProduct(weights,phi)<0.0:
            return -1
        else:
            return 1
    for i in range(numIters):
        for item in trainExamples:
            x,y=item
            phi=featureExtractor(x)
            temp=dotProduct(weights,phi)*y
            if temp < 1:increment(weights,-eta*-y,phi)
        print("Iteration:%s, Training error:%s, Test error:%s"%(i,evaluatePredictor(trainExamples,predict),evaluatePredictor(testExamples,predict)))
    # END_YOUR_CODE
    return weights

############################################################
# Problem 3c: generate test case

def generateDataset(numExamples, weights):
    '''
    Return a set of examples (phi(x), y) randomly which are classified correctly by
    |weights|.
    '''
    random.seed(42)
    # Return a single example (phi(x), y).
    # phi(x) should be a dict whose keys are a subset of the keys in weights
    # and values can be anything (randomize!) with a nonzero score under the given weight vector.
    # y should be 1 or -1 as classified by the weight vector.
    def generateExample():
        # BEGIN_YOUR_CODE (our solution is 2 lines of code, but don't worry if you deviate from this)
        phi={}
        for item in random.sample(list(weights),random.randint(1,len(weights))):
            phi[item]=random.randint(1,100)
        y=1 if dotProduct(weights,phi)>1 else 0
        # END_YOUR_CODE
        return (phi, y)
    return [generateExample() for _ in range(numExamples)]

############################################################
# Problem 3e: character features

def extractCharacterFeatures(n):
    '''
    Return a function that takes a string |x| and returns a sparse feature
    vector consisting of all n-grams of |x| without spaces.
    EXAMPLE: (n = 3) "I like tacos" --> {'Ili': 1, 'lik': 1, 'ike': 1, ...
    You may assume that n >= 1.
    '''
    def extract(x):
        # BEGIN_YOUR_CODE (our solution is 6 lines of code, but don't worry if you deviate from this)
        returnDict=collections.defaultdict(int)
        x=x.replace(' ','')
        for i in range(0,len(x)-(n-1)):
            returnDict[x[i:i+n]]+=1
        return returnDict
        # END_YOUR_CODE
    return extract

############################################################
# Problem 4: k-means
############################################################


def kmeans(examples, K, maxIters):
    '''
    examples: list of examples, each example is a string-to-double dict representing a sparse vector.
    K: number of desired clusters. Assume that 0 < K <= |examples|.
    maxIters: maximum number of iterations to run (you should terminate early if the algorithm converges).
    Return: (length K list of cluster centroids,
            list of assignments (i.e. if examples[i] belongs to centers[j], then assignments[i] = j)
            final reconstruction loss)
    '''
    # BEGIN_YOUR_CODE (our solution is 32 lines of code, but don't worry if you deviate from this)
    centroids=[sample.copy() for sample in random.sample(examples,K)]
    bestmatch=[random.randint(0,K-1) for item in examples]
    distances=[0 for item in examples]
    pastmatches=None
    examples_squared=[]
    for item in examples:
        tempdict=collections.defaultdict(float)
        for k,v in item.items():
            tempdict[k]=v*v
        examples_squared.append(tempdict)
    for run_range in range(maxIters):
        centroids_squared=[]
        for item in centroids:
            tempdict = collections.defaultdict(float)
            for k, v in item.items():
                tempdict[k] = v * v
            centroids_squared.append(tempdict)
        for index,item in enumerate(examples):
            min_distance=999999
            for i,cluster in enumerate(centroids):
                distance=sum(examples_squared[index].values())+sum(centroids_squared[i].values())
                #for k in set(item.keys() & cluster.keys()):
                for k in (item.viewkeys() & cluster.viewkeys()):
                    distance+=-2*item[k]*cluster[k]
                if distance<min_distance:
                    min_distance=distance
                    bestmatch[index]=i
                    distances[index]=min_distance
        if pastmatches==bestmatch:
            break
        else:
            clustercounts=[0 for cluster in centroids]
            for i,cluster in enumerate(centroids):
                for k in cluster:
                    cluster[k]=0.0
            for index,item in enumerate(examples):
                clustercounts[bestmatch[index]]+=1
                cluster=centroids[bestmatch[index]]
                for k,v in item.items():
                    if k in cluster:
                        cluster[k]+=v
                    else:
                        cluster[k]=0.0+v
            for i, cluster in enumerate(centroids):
                for k in cluster:
                    cluster[k]/=clustercounts[i]
            pastmatches=bestmatch[:]
    return centroids,bestmatch,sum(distances)
    # END_YOUR_CODE
