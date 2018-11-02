#!/usr/bin/env python

import graderUtil, collections, random

grader = graderUtil.Grader()
submission = grader.load('submission')

############################################################
# Problems 1 and 2

### Problem 1
grader.addManualPart('1a', maxPoints=2, description='optimize weighted average')
grader.addManualPart('1b', maxPoints=3, description='swap sum and max')
grader.addManualPart('1c', maxPoints=3, description='expected value of iterated game')
grader.addManualPart('1d', maxPoints=3, description='derive maximum likelihood')
grader.addManualPart('1e', maxPoints=3, description='take gradient')

### Problem 2
grader.addManualPart('2a', maxPoints=2, description='counting faces')
grader.addManualPart('2b', maxPoints=3, description='dynamic program')
grader.addManualPart('2c', maxPoints=3, description='count paths')
grader.addManualPart('2d', maxPoints=3, description='preprocessing with matrices')

############################################################
# Problem 3a: findAlphabeticallyLastWord

grader.addBasicPart('3a-0-basic', lambda :
        grader.requireIsEqual('word', submission.findAlphabeticallyLastWord('which is the last word alphabetically')),
        description='simple test case')

grader.addBasicPart('3a-1-basic', lambda : grader.requireIsEqual('sun', submission.findAlphabeticallyLastWord('cat sun dog')), description='simple test case')
grader.addBasicPart('3a-2-basic', lambda : grader.requireIsEqual('99999', submission.findAlphabeticallyLastWord(' '.join(str(x) for x in range(100000)))), description='big test case')

############################################################
# Problem 3b: euclideanDistance

grader.addBasicPart('3b-0-basic', lambda : grader.requireIsEqual(5, submission.euclideanDistance((1, 5), (4, 1))), description='simple test case')

def test():
    random.seed(42)
    for _ in range(100):
        x1 = random.randint(0, 10)
        y1 = random.randint(0, 10)
        x2 = random.randint(0, 10)
        y2 = random.randint(0, 10)
        ans2 = submission.euclideanDistance((x1, y1), (x2, y2))
grader.addHiddenPart('3b-1-hidden', test, maxPoints=2, description='100 random trials')

############################################################
# Problem 3c: mutateSentences

def test():
    grader.requireIsEqual(sorted(['a a a a a']), sorted(submission.mutateSentences('a a a a a')))
    grader.requireIsEqual(sorted(['the cat']), sorted(submission.mutateSentences('the cat')))
    grader.requireIsEqual(sorted(['and the cat and the', 'the cat and the mouse', 'the cat and the cat', 'cat and the cat and']), sorted(submission.mutateSentences('the cat and the mouse')))
grader.addBasicPart('3c-0-basic', test, maxPoints=1, description='simple test')

def genSentence(K, L): # K = alphabet size, L = length
    return ' '.join(str(random.randint(0, K)) for _ in range(L))

def test():
    random.seed(42)
    for _ in range(10):
        sentence = genSentence(3, 5)
        ans2 = submission.mutateSentences(sentence)
grader.addHiddenPart('3c-1-hidden', test, maxPoints=1, description='random trials')

def test():
    random.seed(42)
    for _ in range(10):
        sentence = genSentence(25, 10)
        ans2 = submission.mutateSentences(sentence)
grader.addHiddenPart('3c-2-hidden', test, maxPoints=2, description='random trials (bigger)')

############################################################
# Problem 3d: dotProduct

def test():
    grader.requireIsEqual(15, submission.sparseVectorDotProduct(collections.defaultdict(float, {'a': 5}), collections.defaultdict(float, {'b': 2, 'a': 3})))
grader.addBasicPart('3d-0-basic', test, maxPoints=1, description='simple test')

def randvec():
    v = collections.defaultdict(float)
    for _ in range(10):
        v[random.randint(0, 10)] = random.randint(0, 10) - 5
    return v
def test():
    random.seed(42)
    for _ in range(10):
        v1 = randvec()
        v2 = randvec()
        ans2 = submission.sparseVectorDotProduct(v1, v2)
grader.addHiddenPart('3d-1-hidden', test, maxPoints=2, description='random trials')

############################################################
# Problem 3e: incrementSparseVector

def test():
    v = collections.defaultdict(float, {'a': 5})
    submission.incrementSparseVector(v, 2, collections.defaultdict(float, {'b': 2, 'a': 3}))
    grader.requireIsEqual(collections.defaultdict(float, {'a': 11, 'b': 4}), v)
grader.addBasicPart('3e-0-basic', test, description='simple test')

def test():
    random.seed(42)
    for _ in range(10):
        v1a = randvec()
        v1b = v1a.copy()
        v2 = randvec()
        submission.incrementSparseVector(v1b, 4, v2)
        for key in list(v1b):
          if v1b[key] == 0:
            del v1b[key]
grader.addHiddenPart('3e-1-hidden', test, maxPoints=2, description='random trials')

############################################################
# Problem 3f: findSingletonWords

def test3f():
    grader.requireIsEqual(set(['quick', 'brown', 'jumps', 'over', 'lazy']), submission.findSingletonWords('the quick brown fox jumps over the lazy fox'))
grader.addBasicPart('3f-0-basic', test3f, description='simple test')

def test3f(numTokens, numTypes):
    import random
    random.seed(42)
    text = ' '.join(str(random.randint(0, numTypes)) for _ in range(numTokens))
grader.addHiddenPart('3f-1-hidden', lambda : test3f(1000, 10), maxPoints=1, description='random trials')
grader.addHiddenPart('3f-2-hidden', lambda : test3f(10000, 100), maxPoints=1, description='random trials (bigger)')

############################################################
# Problem 3g: computeLongestPalindrome

def test3g():
    # Test around bases cases
    grader.requireIsEqual(0, submission.computeLongestPalindromeLength(""))
    grader.requireIsEqual(1, submission.computeLongestPalindromeLength("a"))
    grader.requireIsEqual(2, submission.computeLongestPalindromeLength("aa"))
    grader.requireIsEqual(1, submission.computeLongestPalindromeLength("ab"))
    grader.requireIsEqual(3, submission.computeLongestPalindromeLength("animal"))
grader.addBasicPart('3g-0-basic', test3g, description='simple test')

def test3g(numChars, length):
    import random
    random.seed(42)
    # Generate a random string of the given length
    text = ' '.join(chr(random.randint(ord('a'), ord('a') + numChars - 1)) for _ in range(length))
    ans2 = submission.computeLongestPalindromeLength(text)
grader.addHiddenPart('3g-2-hidden', lambda : test3g(2, 10), maxPoints=1, maxSeconds=1, description='random trials')
grader.addHiddenPart('3g-3-hidden', lambda : test3g(10, 10), maxPoints=1, maxSeconds=1, description='random trials (more characters)')
grader.addHiddenPart('3g-4-hidden', lambda : test3g(5, 20), maxPoints=1, maxSeconds=1, description='random trials')
grader.addHiddenPart('3g-5-hidden', lambda : test3g(5, 400), maxPoints=2, maxSeconds=2, description='random trials (longer)')

grader.grade()
