#!/usr/bin/python

import graderUtil
import util
import random
import sys
import wordsegUtil

grader = graderUtil.Grader()
submission = grader.load('submission')

QUERIES_SEG = [
    'ThestaffofficerandPrinceAndrewmountedtheirhorsesandrodeon',
    'hellothere officerandshort erprince',
    'howdythere',
    'The staff officer and Prince Andrew mounted their horses and rode on.',
    'whatsup',
    'duduandtheprince',
    'duduandtheking',
    'withoutthecourtjester',
    'lightbulbneedschange',
    'imagineallthepeople',
    'thisisnotmybeautifulhouse',
]

QUERIES_INS = [
    'strng',
    'pls',
    'hll thr',
    'whats up',
    'dudu and the prince',
    'frog and the king',
    'ran with the queen and swam with jack',
    'light bulbs need change',
    'ffcr nd prnc ndrw',
    'ffcr nd shrt prnc',
    'ntrntnl',
    'smthng',
    'btfl',
]

QUERIES_BOTH = [
    'stff',
    'hllthr',
    'thffcrndprncndrw',
    'ThstffffcrndPrncndrwmntdthrhrssndrdn',
    'whatsup',
    'ipovercarrierpigeon',
    'aeronauticalengineering',
    'themanwiththegoldeneyeball',
    'lightbulbsneedchange',
    'internationalplease',
    'comevisitnaples',
    'somethingintheway',
    'itselementarymydearwatson',
    'itselementarymyqueen',
    'themanandthewoman',
    'nghlrdy',
    'jointmodelingworks',
    'jointmodelingworkssometimes',
    'jointmodelingsometimesworks',
    'rtfclntllgnc',
]

CORPUS = 'leo-will.txt'

_realUnigramCost, _realBigramCost, _possibleFills = None, None, None

def getRealCosts():
    global _realUnigramCost, _realBigramCost, _possibleFills

    if _realUnigramCost is None:
        sys.stdout.write('Training language cost functions [corpus: %s]... ' % CORPUS)
        sys.stdout.flush()

        _realUnigramCost, _realBigramCost = wordsegUtil.makeLanguageModels(CORPUS)
        _possibleFills = wordsegUtil.makeInverseRemovalDictionary(CORPUS, 'aeiou')

        print 'Done!'
        print ''

    return _realUnigramCost, _realBigramCost, _possibleFills


def add_parts_1(grader, submission):
    grader.addManualPart('1a', 2, description='example to justify the greedy algorithm is suboptimal in word segmentation')

    if grader.selectedPartName in ['1b-2-basic', '1b-3-hidden', '1b-4-hidden', None]:  # avoid timeouts
        unigramCost, _, _ = getRealCosts()

    def t_1b_1():
        def unigramCost(x):
            if x in ['and', 'two', 'three', 'word', 'words']:
                return 1.0
            else:
                return 1000.0

        grader.requireIsEqual('', submission.segmentWords('', unigramCost))
        grader.requireIsEqual('word', submission.segmentWords('word', unigramCost))
        grader.requireIsEqual('two words', submission.segmentWords('twowords', unigramCost))
        grader.requireIsEqual('and three words', submission.segmentWords('andthreewords', unigramCost))

    grader.addBasicPart('1b-1-basic', t_1b_1, maxPoints=1, maxSeconds=2, description='simple test case using hand-picked unigram costs')

    def t_1b_2():
        grader.requireIsEqual('word', submission.segmentWords('word', unigramCost))
        grader.requireIsEqual('two words', submission.segmentWords('twowords', unigramCost))
        grader.requireIsEqual('and three words', submission.segmentWords('andthreewords', unigramCost))

    grader.addBasicPart('1b-2-basic', t_1b_2, maxPoints=1, maxSeconds=2, description='simple test case using unigram cost from the corpus')

    def t_1b_3():
        # Word seen in corpus
        solution1 = submission.segmentWords('pizza', unigramCost)

        # Even long unseen words are preferred to their arbitrary segmentations
        solution2 = submission.segmentWords('qqqqq', unigramCost)
        solution3 = submission.segmentWords('z' * 100, unigramCost)

        # But 'a' is a word
        solution4 = submission.segmentWords('aa', unigramCost)

        # With an apparent crossing point at length 6->7
        solution5 = submission.segmentWords('aaaaaa', unigramCost)
        solution6 = submission.segmentWords('aaaaaaa', unigramCost)


    grader.addHiddenPart('1b-3-hidden', t_1b_3, maxPoints=3, maxSeconds=3, description='simple hidden test case')

    def t_1b_4():
        for query in QUERIES_SEG:
            query = wordsegUtil.cleanLine(query)
            parts = wordsegUtil.words(query)
            pred = [submission.segmentWords(part, unigramCost) for part in parts]

    grader.addHiddenPart('1b-4-hidden', t_1b_4, maxPoints=5, maxSeconds=3, description='hidden test case for all queries in QUERIES_SEG')


def add_parts_2(grader, submission):
    grader.addManualPart('2a', 2, description='example to justify the greedy algorithm is suboptimal in vowel insertion')

    if grader.selectedPartName in ['2b-2-hidden', '2b-4-hidden', None]:  # avoid timeouts
        _, bigramCost, possibleFills = getRealCosts()

    def t_2b_1():
        def bigramCost(a, b):
            corpus = [wordsegUtil.SENTENCE_BEGIN] + 'beam me up scotty'.split()
            if (a, b) in list(zip(corpus, corpus[1:])):
                return 1.0
            else:
                return 1000.0

        def possibleFills(x):
            fills = {
                'bm'   : set(['beam', 'bam', 'boom']),
                'm'    : set(['me', 'ma']),
                'p'    : set(['up', 'oop', 'pa', 'epe']),
                'sctty': set(['scotty']),
            }
            return fills.get(x, set())

        grader.requireIsEqual(
            '',
            submission.insertVowels([], bigramCost, possibleFills)
        )
        grader.requireIsEqual( # No fills
            'zz$z$zz',
            submission.insertVowels(['zz$z$zz'], bigramCost, possibleFills)
        )
        grader.requireIsEqual(
            'beam',
            submission.insertVowels(['bm'], bigramCost, possibleFills)
        )
        grader.requireIsEqual(
            'me up',
            submission.insertVowels(['m', 'p'], bigramCost, possibleFills)
        )
        grader.requireIsEqual(
            'beam me up scotty',
            submission.insertVowels('bm m p sctty'.split(), bigramCost, possibleFills)
        )

    grader.addBasicPart('2b-1-basic', t_2b_1, maxPoints=1, maxSeconds=2, description='simple test case')

    def t_2b_2():
        solution1 = submission.insertVowels([], bigramCost, possibleFills)
        # No fills
        solution2 = submission.insertVowels(['zz$z$zz'], bigramCost, possibleFills)
        solution3 = submission.insertVowels([''], bigramCost, possibleFills)
        solution4 = submission.insertVowels('wld lk t hv mr lttrs'.split(), bigramCost, possibleFills)
        solution5 = submission.insertVowels('ngh lrdy'.split(), bigramCost, possibleFills)


    grader.addHiddenPart('2b-2-hidden', t_2b_2, maxPoints=3, maxSeconds=2, description='simple hidden test case')

    def t_2b_3():
        SB = wordsegUtil.SENTENCE_BEGIN

        # Check for correct use of SENTENCE_BEGIN
        def bigramCost(a, b):
            if (a, b) == (SB, 'cat'):
                return 5.0
            elif a != SB and b == 'dog':
                return 1.0
            else:
                return 1000.0

        solution1 = submission.insertVowels(['x'], bigramCost, lambda x: set(['cat', 'dog']))

        # Check for non-greediness

        def bigramCost(a, b):
            # Dog over log -- a test poem by rf
            costs = {
                (SB, 'cat'):      1.0,  # Always start with cat

                ('cat', 'log'):   1.0,  # Locally prefer log
                ('cat', 'dog'):   2.0,  # rather than dog

                ('log', 'mouse'): 3.0,  # But dog would have been
                ('dog', 'mouse'): 1.0,  # better in retrospect
            }
            return costs.get((a, b), 1000.0)

        def fills(x):
            return {
                'x1': set(['cat', 'dog']),
                'x2': set(['log', 'dog', 'frog']),
                'x3': set(['mouse', 'house', 'cat'])
            }[x]

        solution2 = submission.insertVowels('x1 x2 x3'.split(), bigramCost, fills)

        # Check for non-trivial long-range dependencies
        def bigramCost(a, b):
            # Dogs over logs -- another test poem by rf
            costs = {
                (SB, 'cat'):        1.0,  # Always start with cat

                ('cat', 'log1'):    1.0,  # Locally prefer log
                ('cat', 'dog1'):    2.0,  # Rather than dog

                ('log20', 'mouse'): 1.0,  # And this might even
                ('dog20', 'mouse'): 1.0,  # seem to be okay
            }
            for i in xrange(1, 20):       # But along the way
            #                               Dog's cost will decay
                costs[('log' + str(i), 'log' + str(i+1))] = 0.25
                costs[('dog' + str(i), 'dog' + str(i+1))] = 1.0 / float(i)
            #                               Hooray
            return costs.get((a, b), 1000.0)

        def fills(x):
            f = {
                'x0': set(['cat', 'dog']),
                'x21': set(['mouse', 'house', 'cat']),
            }
            for i in xrange(1, 21):
                f['x' + str(i)] = set(['log' + str(i), 'dog' + str(i), 'frog'])
            return f[x]

        solution3 = submission.insertVowels(['x' + str(i) for i in xrange(0, 22)], bigramCost, fills)


    grader.addHiddenPart('2b-3-hidden', t_2b_3, maxPoints=3, maxSeconds=3, description='simple hidden test case')

    def t_2b_4():
        for query in QUERIES_INS:
            query = wordsegUtil.cleanLine(query)
            ws = [wordsegUtil.removeAll(w, 'aeiou') for w in wordsegUtil.words(query)]
            pred = submission.insertVowels(ws, bigramCost, possibleFills)

    grader.addHiddenPart('2b-4-hidden', t_2b_4, maxPoints=3, maxSeconds=3, description='hidden test case for all queries in QUERIES_INS')


def add_parts_3(grader, submission):


    if grader.selectedPartName in ['3b-2-basic', '3b-3-hidden', '3b-5-hidden', None]:  # avoid timeouts
        unigramCost, bigramCost, possibleFills = getRealCosts()

    def t_3b_1():
        def bigramCost(a, b):
            if b in ['and', 'two', 'three', 'word', 'words']:
                return 1.0
            else:
                return 1000.0

        fills_ = {
            'nd': set(['and']),
            'tw': set(['two']),
            'thr': set(['three']),
            'wrd': set(['word']),
            'wrds': set(['words']),
        }
        fills = lambda x: fills_.get(x, set())

        grader.requireIsEqual('', submission.segmentAndInsert('', bigramCost, fills))
        grader.requireIsEqual('word', submission.segmentAndInsert('wrd', bigramCost, fills))
        grader.requireIsEqual('two words', submission.segmentAndInsert('twwrds', bigramCost, fills))
        grader.requireIsEqual('and three words', submission.segmentAndInsert('ndthrwrds', bigramCost, fills))

    grader.addBasicPart('3b-1-basic', t_3b_1, maxPoints=1, maxSeconds=2, description='simple test case with hand-picked bigram costs and possible fills')

    def t_3b_2():
        bigramCost = lambda a, b: unigramCost(b)

        fills_ = {
            'nd': set(['and']),
            'tw': set(['two']),
            'thr': set(['three']),
            'wrd': set(['word']),
            'wrds': set(['words']),
        }
        fills = lambda x: fills_.get(x, set())

        grader.requireIsEqual(
            'word',
            submission.segmentAndInsert('wrd', bigramCost, fills))
        grader.requireIsEqual(
            'two words',
            submission.segmentAndInsert('twwrds', bigramCost, fills))
        grader.requireIsEqual(
            'and three words',
            submission.segmentAndInsert('ndthrwrds', bigramCost, fills))

    grader.addBasicPart('3b-2-basic', t_3b_2, maxPoints=1, maxSeconds=2, description='simple test case with unigram costs as bigram costs')

    def t_3b_3():
        bigramCost = lambda a, b: unigramCost(b)
        fills_ = {
            'nd': set(['and']),
            'tw': set(['two']),
            'thr': set(['three']),
            'wrd': set(['word']),
            'wrds': set(['words']),
            # Hah!  Hit them with two better words
            'th': set(['the']),
            'rwrds': set(['rewards']),
        }
        fills = lambda x: fills_.get(x, set())

        solution1 = submission.segmentAndInsert('wrd', bigramCost, fills)
        solution2 = submission.segmentAndInsert('twwrds', bigramCost, fills)
        # Waddaya know
        solution3 = submission.segmentAndInsert('ndthrwrds', bigramCost, fills)


    grader.addHiddenPart('3b-3-hidden', t_3b_3, maxPoints=6, maxSeconds=3, description='hidden test case with unigram costs as bigram costs and additional possible fills')

    def t_3b_4():
        def bigramCost(a, b):
            corpus = [wordsegUtil.SENTENCE_BEGIN] + 'beam me up scotty'.split()
            if (a, b) in list(zip(corpus, corpus[1:])):
                return 1.0
            else:
                return 1000.0

        def possibleFills(x):
            fills = {
                'bm'   : set(['beam', 'bam', 'boom']),
                'm'    : set(['me', 'ma']),
                'p'    : set(['up', 'oop', 'pa', 'epe']),
                'sctty': set(['scotty']),
                'z'    : set(['ze']),
            }
            return fills.get(x, set())

        # Ensure no non-word makes it through
        solution1 = submission.segmentAndInsert('zzzzz', bigramCost, possibleFills)
        solution2 = submission.segmentAndInsert('bm', bigramCost, possibleFills)
        solution3 = submission.segmentAndInsert('mp', bigramCost, possibleFills)
        solution4 = submission.segmentAndInsert('bmmpsctty', bigramCost, possibleFills)


    grader.addHiddenPart('3b-4-hidden', t_3b_4, maxPoints=6, maxSeconds=3, description='hidden test case with hand-picked bigram costs and possible fills')

    def t_3b_5():
        smoothCost = wordsegUtil.smoothUnigramAndBigram(unigramCost, bigramCost, 0.2)
        for query in QUERIES_BOTH:
            query = wordsegUtil.cleanLine(query)
            parts = [wordsegUtil.removeAll(w, 'aeiou') for w in wordsegUtil.words(query)]
            pred = [submission.segmentAndInsert(part, smoothCost, possibleFills) for part in parts]

    grader.addHiddenPart('3b-5-hidden', t_3b_5, maxPoints=6, maxSeconds=3, description='hidden test case for all queries in QUERIES_BOTH with bigram costs and possible fills from the corpus')

add_parts_1(grader, submission)
add_parts_2(grader, submission)
add_parts_3(grader, submission)
grader.grade()
