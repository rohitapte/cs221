import argparse
import submission
import sys
import wordsegUtil

def parseArgs():
    p = argparse.ArgumentParser()
    p.add_argument('--text-corpus', help='Text training corpus')
    p.add_argument('--model', help='Always use this model')
    return p.parse_args()

# REPL and main entry point
def repl(unigramCost, bigramCost, possibleFills, command=None):
    '''REPL: read, evaluate, print, loop'''

    while True:
        sys.stdout.write('>> ')
        line = sys.stdin.readline().strip()
        if not line:
            break

        if command is None:
            cmdAndLine = line.split(None, 1)
            cmd, line = cmdAndLine[0], ' '.join(cmdAndLine[1:])
        else:
            cmd = command
            line = line

        print ''

        if cmd == 'help':
            print 'Usage: <command> [arg1, arg2, ...]'
            print ''
            print 'Commands:'
            print '\n'.join(a + '\t\t' + b for a, b in [
                ('help', 'This'),
                ('seg', 'Segment character sequences'),
                ('ins', 'Insert vowels into words'),
                ('both', 'Joint segment-and-insert'),
                ('fills', 'Query possibleFills() to see possible vowel-fillings of a word'),
                ('ug', 'Query unigram cost function'),
                ('bg', 'Query bigram cost function'),
            ])
            print ''
            print 'Enter empty line to quit'

        elif cmd == 'seg':
            line = wordsegUtil.cleanLine(line)
            parts = wordsegUtil.words(line)
            print '  Query (seg):', ' '.join(parts)
            print ''
            print '  ' + ' '.join(
                submission.segmentWords(part, unigramCost) for part in parts)

        elif cmd == 'ins':
            line = wordsegUtil.cleanLine(line)
            ws = [wordsegUtil.removeAll(w, 'aeiou') for w in wordsegUtil.words(line)]
            print '  Query (ins):', ' '.join(ws)
            print ''
            print '  ' + submission.insertVowels(ws, bigramCost, possibleFills)

        elif cmd == 'both':
            line = wordsegUtil.cleanLine(line)
            smoothCost = wordsegUtil.smoothUnigramAndBigram(unigramCost, bigramCost, 0.2)
            parts = [wordsegUtil.removeAll(w, 'aeiou') for w in wordsegUtil.words(line)]
            print '  Query (both):', ' '.join(parts)
            print ''
            print '  ' + ' '.join(
                submission.segmentAndInsert(part, smoothCost, possibleFills)
                for part in parts
            )

        elif cmd == 'fills':
            line = wordsegUtil.cleanLine(line)
            print '\n'.join(possibleFills(line))

        elif cmd == 'ug':
            line = wordsegUtil.cleanLine(line)
            print unigramCost(line)

        elif cmd == 'bg':
            grams = tuple(wordsegUtil.words(line))
            prefix, ending = grams[-2], grams[-1]
            print bigramCost(prefix, ending)

        else:
            print 'Unrecognized command:', cmd

        print ''

def main():
    args = parseArgs()
    if args.model and args.model not in ['seg', 'ins', 'both']:
        print 'Unrecognized model:', args.model
        sys.exit(1)

    corpus = args.text_corpus or 'leo-will.txt'

    sys.stdout.write('Training language cost functions [corpus: %s]... ' % corpus)
    sys.stdout.flush()

    unigramCost, bigramCost = wordsegUtil.makeLanguageModels(corpus)
    possibleFills = wordsegUtil.makeInverseRemovalDictionary(corpus, 'aeiou')

    print 'Done!'
    print ''

    repl(unigramCost, bigramCost, possibleFills, command=args.model)
