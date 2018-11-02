# Simple semantic parser that converts sentences into first-order logic.
# @author Percy Liang

import sys, collections, re
from logic import *

############################################################
# NLP (Tokenization, Part-of-speech tagging, Lemmatization)

class NaturalLanguageProcessor:
    def __init__(self, sentence):
        self.sentence = sentence
        self.process()
        # Ensure everything is lowercased:
        self.tokens = [x.lower() for x in self.tokens]

    def process(self):
        """Create 2 lists of the same length:
        - self.tokens:   raw text tokens (lemmatized)
        - self.pos_tags: part-of-speech tags or word classes
        """
        raise NotImplementedError('preprocess() not implemented.')

# Use NLTK to analyze the sentence
class NLTKProcessor(NaturalLanguageProcessor):
    def process(self):
        try:
            self.processWithNLTK()
        except Exception, e:
            # Fall back to SimpleProcessor
            print >> sys.stderr, 'WARNING: Falling back to SimpleProcessor: ', e
            fallbackProcessor = SimpleProcessor(self.sentence)
            self.tokens = fallbackProcessor.tokens
            self.pos_tags = fallbackProcessor.pos_tags

    def processWithNLTK(self):
        import nltk

        ### Perform tokenization.
        self.tokens = nltk.word_tokenize(self.sentence)

        ### Part-of-speech tagging
        self.pos_tags = map(lambda x : x[1], nltk.pos_tag(self.tokens))

        # Hack arround errors in crappy POS tagger
        # Mistakingly tags VBZ as NNS after a NNP (e.g., John lives in a house)
        for i in range(len(self.pos_tags)-1):
            if self.pos_tags[i] == 'NNP' and self.pos_tags[i+1] == 'NNS':
                self.pos_tags[i+1] = 'VBZ'
        for i in range(len(self.pos_tags)):
            if self.tokens[i] == 'Does': self.pos_tags[i] = 'VBZ' # Mistagged as NNP
            if self.tokens[i] == 'Did': self.pos_tags[i] = 'VBZ' # Mistagged as NNP
            if self.tokens[i] == 'red': self.pos_tags[i] = 'JJ' # Mistagged as VBN
            if self.tokens[i] == 'lives': self.pos_tags[i] = 'VBZ' # Mistagged as NNS
            if self.tokens[i] == 'likes': self.pos_tags[i] = 'VBZ' # Mistagged as IN
            if self.tokens[i] == 'like': self.pos_tags[i] = 'VB' # Mistagged as IN

        # Lemmatize
        lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()
        def lemmatize(token, tag):
            # Only lemmatize with the proper POS
            if token.lower() == 'people': return 'person'
            if tag[0] in 'VN':
                return lemmatizer.lemmatize(token.lower(), tag[0].lower())
            else:
                return token
        self.tokens = [lemmatize(token, tag) for token, tag in zip(self.tokens, self.pos_tags)]

# A fallback NLP system
class SimpleProcessor(NaturalLanguageProcessor):
    def split(self, x):
        # Add spaces around punctuations
        x = re.sub(r'([.,?!:;])', r' \1 ', x)
        return x.strip().split()

    def tag(self, w):
        if w[0].isupper(): return 'NNP'
        if w.endswith('ing'): return 'VBG'
        if w.endswith('ed'): return 'VBD'
        if w in ('.', ',', '?', '!', ':', ';'): return w
        return 'NN'

    def process(self):
        self.tokens = self.split(self.sentence)
        self.pos_tags = [self.tag(token) for token in self.tokens]

# Use tags from the specified categories
def getCategoryProcessor(categories):
    """Return a new NaturalLanguageProcessor class where the pos_tags are
    assigned according to the specified categories.

    |categories| is a dictionay from a category (e.g., "Noun", "PersonName", "NN")
    to a list of words in that category.

    Each word cannot belong to multiple categories. Unrecognized words will be
    tagged as 'Other'

    Example: If |categories| is
        {
            'Noun': ['cats', 'dogs', 'animals'],
            'Verb': ['run', 'walk'],
        }
    Then the pos_tags for 'Cats run fast' will be ['Noun', 'Verb', 'Other'].
    """
    wordToCategory = {}
    for cat in categories:
        for word in categories[cat]:
            assert word not in wordToCategory, \
                    "%s is in both %s and %s" % (word, wordToCategory[word], cat)
            capital = word.capitalize()
            assert capital not in wordToCategory, \
                    "%s is in both %s and %s" % (capital, wordToCategory[capital], cat)
            wordToCategory[word] = cat
            wordToCategory[capital] = cat

    class CategoryProcessor(SimpleProcessor):
        def tag(self, w):
            return wordToCategory.get(w, 'Other')

    return CategoryProcessor

############################################################
# Representation of a natural language utterance.

class Utterance:
    def __init__(self, sentence, processorClass=NLTKProcessor):
        # Preprocess
        sentence = re.sub(r"\ban\b", 'a', sentence)
        sentence = re.sub(r"\bdon't\b", 'do not', sentence)
        sentence = re.sub(r"\bdoesn't\b", 'does not', sentence)
        sentence = re.sub(r"\bit's\b", 'it is', sentence)
        sentence = re.sub(r"\bIt's\b", 'It is', sentence)
        self.sentence = sentence

        # Process the sentence
        nlProcessor = processorClass(self.sentence)
        self.tokens = nlProcessor.tokens
        self.pos_tags = nlProcessor.pos_tags

    def __str__(self):
        return ' '.join('%s/%s' % x for x in zip(self.tokens, self.pos_tags))

############################################################
# A Grammar maps a sequence of natural language tokens to a set of ParserDerivations.

# Try to look inside a lambda (not perfect)
def lambda_rstr(x):
    if isinstance(x, tuple): return str(tuple(map(lambda_rstr, x)))
    if callable(x):
        v = Constant('v')
        try:
            return "(%s => %s)" % (v, lambda_rstr(x(v)))
        except:
            try:
                return "(%s => %s)" % (v, lambda_rstr(x(lambda a : Constant('v('+str(a)+')'))))
            except:
                pass
    return rstr(x)
#print lambda_rstr(lambda x : lambda y : Atom('A', x, y))

# A grammar rule parses the right-hand side |rhs| into a |lhs|
class GrammarRule:
    def __init__(self, lhs, rhs, sem, score = 0):
        self.lhs = lhs
        self.rhs = rhs
        self.sem = sem
        self.score = score
    def __str__(self):
        return "{%s -> %s, score=%s}" % (self.lhs, self.rhs, self.score)

############################################################

BASE_OBJECTS = ['Garfield', 'Pluto', 'Jon']

def createBaseLanguageProcessor():
    # Defines a mapping from each in-domain word to its word class.
    # This automatically creates rules such as
    #   $Noun -> cat
    # with the string "cat" as the denotation
    categories = {
        'Noun': ['cat', 'tabby', 'mammal', 'person'],
        'Verb': ['likes', 'feeds'],
        'Name': BASE_OBJECTS,
        }
    return getCategoryProcessor(categories)

def createBaseEnglishGrammar():
    # Create a basic grammar consisting a set of rules.
    # Please see nlparser.py for more information on the GrammarRule class.
    rules = []

    # Parse if it's a question or statement.
    rules.append(GrammarRule('$ROOT', ['$Statement'], lambda args: ('tell', args[0])))
    rules.append(GrammarRule('$ROOT', ['$Question'], lambda args: ('ask', args[0])))
    rules.append(GrammarRule('$Statement', ['$Clause', '.'], lambda args: args[0]))
    rules.append(GrammarRule('$Question', ['$Clause', '?'], lambda args: args[0]))

    # Add rule for 'every $Noun is a $Noun'
    rules.append(GrammarRule('$Clause', ['every', '$Noun', 'is', 'a', '$Noun'],
        lambda args: Forall('$x', Implies(Atom(args[0].title(), '$x'), Atom(args[1].title(), '$x')))))

    # Add rule for '$Name is a $Noun'
    rules.append(GrammarRule('$Clause', ['$Name', 'is', 'a', '$Noun'],
        lambda args: Atom(args[1].title(), args[0].lower())))

    # Add rule for 'is $Name a $Noun?'
    rules.append(GrammarRule('$Question', ['is', '$Clause-be', '?'],
        lambda args: args[0]))
    rules.append(GrammarRule('$Clause-be', ['$Name', 'a', '$Noun'],
        lambda args: Atom(args[1].title(), args[0].lower())))

    # Add rule for '$Name $Verb $Name'
    rules.append(GrammarRule('$Clause', ['$Name', '$Verb', '$Name'],
        lambda args: Atom(args[1].title(), args[0].lower(), args[2].lower())))

    # Add rule for '$Name $Verb some $Noun'
    rules.append(GrammarRule('$Clause', ['$Name', '$Verb', 'some', '$Noun'],
        lambda args: Exists('$y', And(Atom(args[2].title(), '$y'), Atom(args[1].title(), args[0].lower(), '$y')))))

    return rules


def createToyGrammar():
    rules = []
    rules.append(GrammarRule('$S', ['the', '$B'], lambda args : ('ask', args[0])))
    rules.append(GrammarRule('$B', ['rain'], lambda args : Atom('Rain')))
    return rules

############################################################
# Parser takes an utterance, a grammar and returns a set of ParserDerivations,
# each of which contains a logical form.

# A Derivation includes a logical form, a rule, children derivations (if any) and a score.
class ParserDerivation():
    def __init__(self, form, rule, children, score):
        self.form = form
        self.rule = rule
        self.children = children
        self.score = score
    def dump(self, indent=""):
        print "%s%s: score=%s, rule: %s" % (indent, lambda_rstr(self.form), self.score, self.rule)
        for child in self.children:
            child.dump(indent + "  ")

# Move unary rules (RHS has 1 argument) to the bottom of the list in topological order
# Complain if cycles occur (e.g. "A -> B" and "B -> A" cannot appear simultaneously.)
def sortRules(rules):
    unaries, others = [], []
    colors, children = {}, collections.defaultdict(set)
    for rule in rules:
        if len(rule.rhs) == 1:
            unaries.append(rule)
            a, b = rule.lhs, rule.rhs[0]
            colors[a] = colors[b] = 'white'
            children[a].add(b)
        else:
            others.append(rule)
    # Do topological sort on the symbols in unary rules.
    sortedSymbols = []
    def visit(symbol):
        if colors[symbol] == 'gray':
            raise Exception('Cyclic unary rules detected!')
        if colors[symbol] == 'white':
            colors[symbol] = 'gray'
            for child in children[symbol]:
                visit(child)
            colors[symbol] = 'black'
            sortedSymbols.append(symbol)
    while 'white' in colors.values():
        # Find a symbol with white color and visit it.
        whiteSymbols = [x for x in colors if colors[x] == 'white']
        visit(whiteSymbols[0])
    # Sort the rules
    def key(rule):
        a, b = rule.lhs, rule.rhs[0]
        return (sortedSymbols.index(a), sortedSymbols.index(b))
    unaries.sort(key=key)
    return others + unaries

# Return a sorted list of ParserDerivations.
# Standard bottom-up CKY parsing
def parseUtterance(utterance, rules, verbose=0):
    def isCat(x): return x.startswith('$')
    tokens = utterance.tokens
    n = len(tokens)
    beamSize = 5
    rules = sortRules(rules)

    # 0    start       mid -> split       end        n
    def applyRule(start, end, mid, rule, rhsIndex, children, score):
        #print "applyRule: start=%s end=%s mid=%s, rule=%s[%s], children=%s" % (start, end, mid, rule, rhsIndex, children)
        # Need to arrive at end of tokens exactly when run out of rhs
        if (mid == end) != (rhsIndex == len(rule.rhs)):
            return

        if rhsIndex == len(rule.rhs):
            deriv = ParserDerivation(rule.sem([child.form for child in children]), rule, children, score + rule.score)
            if verbose >= 3:
                print "applyRule: %s:%s%s %s += %s" % (start, end, tokens[start:end], rule.lhs, rstr(deriv.form))
            chart[start][end][rule.lhs].append(deriv)
            return
        a = rule.rhs[rhsIndex]
        if isCat(a):  # Category
            for split in range(mid+1, end+1):
                #print "split", mid, split
                for child in chart[mid][split].get(a, {}):
                    applyRule(start, end, split, rule, rhsIndex+1, children + [child], score + child.score)
        else:  # Token
            if tokens[mid] == a:
                applyRule(start, end, mid+1, rule, rhsIndex+1, children, score)

    # Initialize
    chart = [None] * n # start => end => category => top K derivations (logical form, score)
    for start in range(0, n):
        chart[start] = [None] * (n+1)
        for end in range(start+1, n+1):
            chart[start][end] = collections.defaultdict(list)

    # Initialize with POS tags
    for start in range(0, n):
        # Don't tag these words, because coupla and negation items need to be treated specially
        if utterance.tokens[start] in ('be', 'not'): continue
        chart[start][start+1]['$'+utterance.pos_tags[start]].append(ParserDerivation(utterance.tokens[start], None, [], 0))

    # Parse
    for length in range(1, n+1):  # For each span length...
        for start in range(n - length + 1):  # For each starting position
            end = start + length
            for rule in rules:
                applyRule(start, end, start, rule, 0, [], 0)

            # Prune derivations
            cell = chart[start][end]
            for cat in cell.keys():
                cell[cat] = sorted(cell[cat], key = lambda deriv : -deriv.score)[0:beamSize]

    derivations = chart[0][n]['$ROOT']
    if verbose >= 1:
        print "parseUtterance: %d derivations" % len(derivations)
    if verbose >= 2:
        for deriv in derivations:
            if verbose >= 3:
                deriv.dump("  ")
            else:
                print "  %s: score=%s" % (rstr(deriv.form), deriv.score)
    return derivations

############################################################

# Train the grammar rule scores to get the training examples correct.
# Also acts as a unit test (we should get 100% accuracy).
def trainGrammar(rules):
    # Training examples
    examples = []

    # Zeroary
    examples.append(('It is raining.', ('tell', Atom('Rain'))))
    examples.append(('It is summer.', ('tell', Atom('Summer'))))
    examples.append(('It is wet.', ('tell', Atom('Wet'))))
    examples.append(('It is not summer.', ('tell', Not(Atom('Summer')))))

    # Simple sentences
    examples.append(('John is happy.', ('tell', Atom('Happy', 'john'))))
    examples.append(('John is not happy.', ('tell', Not(Atom('Happy', 'john')))))
    examples.append(('John is a cat.', ('tell', Atom('Cat', 'john'))))
    examples.append(('John is not a dog.', ('tell', Not(Atom('Dog', 'john')))))
    examples.append(('John was born in Seattle.', ('tell', Atom('Bear_in', 'john', 'seattle'))))
    examples.append(('John lives in Seattle.', ('tell', Atom('Live_in', 'john', 'seattle'))))
    examples.append(('John lives in New York.', ('tell', Atom('Live_in', 'john', 'new_york'))))
    examples.append(('John does not live in New York.', ('tell', Not(Atom('Live_in', 'john', 'new_york')))))

    # Miscellaneous
    examples.append(('New York is a big city.', ('tell', And(Atom('Big', 'new_york'), Atom('City', 'new_york')))))
    examples.append(('If it is raining, it is wet.', ('tell', Implies(Atom('Rain'), Atom('Wet')))))

    # Coordination
    examples.append(('John and Bill are cats.', ('tell', And(Atom('Cat', 'john'), Atom('Cat', 'bill')))))
    examples.append(('John is either happy or sad.', ('tell', Xor(Atom('Happy', 'john'), Atom('Sad', 'john')))))
    examples.append(('John lives in Seattle or Portland.', ('tell', Or(Atom('Live_in', 'john', 'seattle'), Atom('Live_in', 'john', 'portland')))))
    examples.append(('Either it is raining or it is snowing.', ('tell', And(Or(Atom('Rain'), Atom('Snow')), Not(And(Atom('Rain'), Atom('Snow')))))))

    # Quantification
    examples.append(('Cats are animals.', ('tell', Forall('$x1', Implies(Atom('Cat', '$x1'), Atom('Animal', '$x1'))))))
    examples.append(('A cat is an animal.', ('tell', Forall('$x1', Implies(Atom('Cat', '$x1'), Atom('Animal', '$x1'))))))
    examples.append(('If a person lives in California, he is happy.', ('tell', Forall('$x1', Implies(And(Atom('Person', '$x1'), Atom('Live_in', '$x1', 'california')), Atom('Happy', '$x1'))))))
    examples.append(('John visited every city.', ('tell', Forall('$x1', Implies(Atom('City', '$x1'), Atom('Visit', 'john', '$x1'))))))
    examples.append(('Every city was visited by John.', ('tell', Forall('$x1', Implies(Atom('City', '$x1'), Atom('Visit_by', '$x1', 'john'))))))
    examples.append(('Every person likes some cat.', ('tell', Forall('$x1', Implies(Atom('Person', '$x1'), Exists('$x2', And(Atom('Cat', '$x2'), Atom('Like', '$x1', '$x2'))))))))
    examples.append(('No city is perfect.', ('tell', Not(Exists('$x1', And(Atom('City', '$x1'), Atom('Perfect', '$x1')))))))

    examples.append(('Does John live in Sweden?', ('ask', Atom('Live_in', 'john', 'sweden'))))

    ### Train the model using Perceptron

    print "============================================================"
    print "Training the grammar on %d examples" % len(examples)
    numUpdates = 0
    def updateWeights(deriv, incr):
        if deriv.rule:
            deriv.rule.score += incr
        for child in deriv.children:
            updateWeights(child, incr)

    # target, pred are both (mode, form)
    # Need to use unify because the variables could be different
    def isCompatible(target, pred):
        return target == pred
        #return target[0] == pred[0] and unify(target[1], pred[1], {})

    for iteration in range(0, 10):
        print '-- Iteration %d' % iteration
        numMistakes = 0
        for x, y in examples:
            # Predict on example
            utterance = Utterance(x)
            derivations = parseUtterance(utterance, rules)
            targetDeriv = None
            for deriv in derivations:
                if isCompatible(y, deriv.form):
                    targetDeriv = deriv
                    break
            if targetDeriv == None:
                print "Impossible to get correct: %s => %s" % (x, rstr(y))
                print "  Utterance:", utterance
                print "  Derivations:"
                for deriv in derivations:
                    print '   ', rstr(deriv.form)
                continue
            predDeriv = derivations[0]

            if predDeriv != targetDeriv:
                print "Mistake: %s => %s, predicted %s" % (x, rstr(y), rstr(predDeriv.form))
                numMistakes += 1
                # Update weights
                numUpdates += 1
                stepSize = 1.0 # / math.sqrt(numUpdates)
                updateWeights(targetDeriv, +stepSize)
                updateWeights(predDeriv, -stepSize)
        if numMistakes == 0: break

    print 'Rules with non-zero weights:'
    for rule in rules:
        if rule.score != 0:
            print ' ', rule
