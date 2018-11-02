#!/usr/bin/python

# A natural language interface to a knowledge base.
# rlwrap ./nli.py

import sys, collections, re
import logic, nlparser
import argparse
import submission

# Parse command-line arguments
argparser = argparse.ArgumentParser()
argparser.add_argument('--verbose', default=0)
argparser.add_argument('--inference', default='resolution', help='Inference algorithm (either resolution or modelChecking)')
argparser.add_argument('--utterances', help='Utterances to load before the prompt')
argparser.add_argument('--nltk', help='Use NLTK to analyze sentences', action='store_true', default=False)
argparser.add_argument('--grammar', help='Which grammar to use', default='submission')
argparser.add_argument('--train', help='Whether to train the model', action='store_true')
opts = argparser.parse_args()

class NaturalLanguageInterface:
    def __init__(self):
        self.verbose = opts.verbose

        # Setup model
        if opts.grammar == 'submission':
            self.rules = nlparser.createBaseEnglishGrammar()
            for createRule in [submission.createRule1, submission.createRule2, submission.createRule3]:
                try:
                    self.rules.append(createRule())
                except:
                    print 'Error creating rule...skipping.'
            self.processor = nlparser.createBaseLanguageProcessor()
        elif opts.grammar == 'standard':
            self.rules = nlparser.createStandardEnglishGrammar()
            self.processor = nlparser.NLTKProcessor if opts.nltk else nlparser.SimpleProcessor
        else:
            raise Exception('Unknown grammar: either submission or standard')
        if opts.train:
            nlparser.trainGrammar(self.rules)

        # Create the knowledge base
        self.initKB()

        # Load utterances if they exist
        if opts.utterances:
            for line in open(opts.utterances):
                line = line.strip()
                if line.startswith('#') or line == '': continue
                if self.verbose >= 1:
                    print '------------------------------'
                    print '>', line
                self.process(line)

    def initKB(self):
        if opts.inference == 'resolution':
            self.kb = logic.createResolutionKB()
        elif opts.inference == 'modelChecking':
            self.kb = logic.createModelCheckingKB()
        else:
            raise Exception('Invalid: %s' % opts.inference)

    def process(self, line):
        line = line.strip()
        if line.startswith('#') or line == '': return

        utterance = nlparser.Utterance(line, self.processor)
        if self.verbose >= 1: print 'Shallow analysis:', utterance

        # Handle special commands
        if utterance.tokens[0] == 'help':
            print "Commands:"
            print "  help: print this message"
            print "  verbose <int>: set verbosity level"
            print "  forget: clear the knowledge base"
            print "  dump: display contents of knowledge base"
            print "  <any natural language utterance>"
            return
        if utterance.tokens[0] == 'verbose':
            self.verbose = int(utterance.tokens[1])
            return
        if utterance.tokens[0] == 'forget':
            print "Starting from a blank slate."
            self.initKB()
            return
        if utterance.tokens[0] == 'dump':
            self.kb.dump()
            return

        # Semantic parsing
        derivations = nlparser.parseUtterance(utterance, self.rules, verbose=self.verbose)
        if len(derivations) == 0:
            print "Sorry, I could not parse that."
            return
        deriv = derivations[0]
        mode, form = deriv.form
        if self.verbose >= 1: print 'Parsed logical formula: %s[%s]' % (mode, form)

        # Query the knowledge base
        self.kb.verbose = opts.verbose
        if mode == 'ask': response = self.kb.ask(form)
        if mode == 'tell': response = self.kb.tell(form)
        print
        logic.showKBResponse(response, self.verbose)

    def interactiveLoop(self):
        print "============================================================"
        print "Hello!  Talk to me in English."
        print "Tell me something new (end the sentence with '.') or ask me a question (end the sentence with '?')."
        print "Type 'help' for additional commands."
        while True:
            # Read utterance from stdin
            print '------------------------------'
            sys.stdout.write('> ')
            line = sys.stdin.readline()
            if not line: break
            self.process(line)

NaturalLanguageInterface().interactiveLoop()
