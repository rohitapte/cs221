
import collections
import math

SENTENCE_BEGIN = '-BEGIN-'

def sliding(xs, windowSize):
    for i in xrange(1, len(xs) + 1):
        yield xs[max(0, i - windowSize):i]

def removeAll(s, chars):
    return ''.join(filter(lambda c: c not in chars, s))

def alphaOnly(s):
    s = s.replace('-', ' ')
    return filter(lambda c: c.isalpha() or c == ' ', s)

def cleanLine(l):
    return alphaOnly(l.strip().lower())

def words(l):
    return l.split()

############################################################
# Make an n-gram model of words in text from a corpus.

def makeLanguageModels(path):
    unigramCounts = collections.Counter()
    totalCounts = 0
    bigramCounts = collections.Counter()
    bitotalCounts = collections.Counter()
    VOCAB_SIZE = 600000
    LONG_WORD_THRESHOLD = 5
    LENGTH_DISCOUNT = 0.15

    def bigramWindow(win):
        assert len(win) in [1, 2]
        if len(win) == 1:
            return (SENTENCE_BEGIN, win[0])
        else:
            return tuple(win)

    with open(path, 'r') as f:
        for l in f:
            ws = words(cleanLine(l))
            unigrams = [x[0] for x in sliding(ws, 1)]
            bigrams = [bigramWindow(x) for x in sliding(ws, 2)]
            totalCounts += len(unigrams)
            unigramCounts.update(unigrams)
            bigramCounts.update(bigrams)
            bitotalCounts.update([x[0] for x in bigrams])

    def unigramCost(x):
        if x not in unigramCounts:
            length = max(LONG_WORD_THRESHOLD, len(x))
            return -(length * math.log(LENGTH_DISCOUNT) + math.log(1.0) - math.log(VOCAB_SIZE))
        else:
            return math.log(totalCounts) - math.log(unigramCounts[x])

    def bigramModel(a, b):
        return math.log(bitotalCounts[a] + VOCAB_SIZE) - math.log(bigramCounts[(a, b)] + 1)

    return unigramCost, bigramModel

def logSumExp(x, y):
    lo = min(x, y)
    hi = max(x, y)
    return math.log(1.0 + math.exp(lo - hi)) + hi;

def smoothUnigramAndBigram(unigramCost, bigramModel, a):
    '''Coefficient `a` is Bernoulli weight favoring unigram'''

    # Want: -log( a * exp(-u) + (1-a) * exp(-b) )
    #     = -log( exp(log(a) - u) + exp(log(1-a) - b) )
    #     = -logSumExp( log(a) - u, log(1-a) - b )

    def smoothModel(w1, w2):
        u = unigramCost(w2)
        b = bigramModel(w1, w2)
        return -logSumExp(math.log(a) - u, math.log(1-a) - b)

    return smoothModel

############################################################
# Make a map for inverse lookup of words without vowels -> possible
# full words

def makeInverseRemovalDictionary(path, removeChars):
    wordsRemovedToFull = collections.defaultdict(set)

    with open(path, 'r') as f:
        for l in f:
            for w in words(cleanLine(l)):
                wordsRemovedToFull[removeAll(w, removeChars)].add(w)

    wordsRemovedToFull = dict(wordsRemovedToFull)
    empty = set()

    def possibleFills(short):
        return wordsRemovedToFull.get(short, empty)

    return possibleFills
