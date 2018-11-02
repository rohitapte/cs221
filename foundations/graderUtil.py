"""
Library to do grading of Python programs.
Usage (see grader.py):

    # create a grader
    grader = Grader("Name of assignment")

    # add a basic test
    grader.addBasicPart(name, gradeFunc, maxPoints, maxSeconds, description="a basic test")

    # add a hidden test
    grader.addHiddenPart(name, gradeFunc, maxPoints, maxSeconds, description="a hidden test")

    # add a manual grading part
    grader.addManualPart(name, gradeFunc, maxPoints, description="written problem")

    # run grading
    grader.grade()
"""

import argparse
import datetime, math, pprint, traceback, sys, signal, os, json
import dateutil.parser
import gc

defaultMaxSeconds = 5  # 5 second
TOLERANCE = 1e-4  # For measuring whether two floats are equal

BASIC_MODE = 'basic'  # basic
AUTO_MODE = 'auto'    # basic + hidden
ALL_MODE = 'all'      # basic + hidden + manual

# When reporting stack traces as feedback, ignore parts specific to the grading
# system.
def isTracebackItemGrader(item):
    return item[0].endswith('graderUtil.py')

def isCollection(x):
    return isinstance(x, list) or isinstance(x, tuple)

# Return whether two answers are equal.
def isEqual(trueAnswer, predAnswer, tolerance = TOLERANCE):
    # Handle floats specially
    if isinstance(trueAnswer, float) or isinstance(predAnswer, float):
        return abs(trueAnswer - predAnswer) < tolerance
    # Recurse on collections to deal with floats inside them
    if isCollection(trueAnswer) and isCollection(predAnswer) and len(trueAnswer) == len(predAnswer):
        for a, b in zip(trueAnswer, predAnswer):
            if not isEqual(a, b): return False
        return True
    if isinstance(trueAnswer, dict) and isinstance(predAnswer, dict):
        if len(trueAnswer) != len(predAnswer): return False
        for k, v in trueAnswer.items():
            if not isEqual(predAnswer.get(k), v): return False
        return True

    # Numpy array comparison
    if type(trueAnswer).__name__ == 'ndarray':
        import numpy as np
        if isinstance(trueAnswer, np.ndarray) and isinstance(predAnswer, np.ndarray):
            if trueAnswer.shape != predAnswer.shape:
                return False
            for a, b in zip(trueAnswer, predAnswer):
                if not isEqual(a, b): return False
            return True

    # Do normal comparison
    return trueAnswer == predAnswer

# Run a function, timing out after maxSeconds.
class TimeoutFunctionException(Exception):
    pass
class TimeoutFunction:
    def __init__(self, function, maxSeconds):
        self.maxSeconds = maxSeconds
        self.function = function

    def handle_maxSeconds(self, signum, frame):
        print 'TIMEOUT!'
        raise TimeoutFunctionException()

    def __call__(self, *args):
        if os.name == 'nt':
            # Windows does not have signal.SIGALRM
            # Will not stop after maxSeconds second but can still throw an exception
            timeStart = datetime.datetime.now()
            result = self.function(*args)
            timeEnd = datetime.datetime.now()
            if timeEnd - timeStart > datetime.timedelta(seconds=self.maxSeconds + 1):
                raise TimeoutFunctionException()
            return result
            # End modification for Windows here
        old = signal.signal(signal.SIGALRM, self.handle_maxSeconds)
        signal.alarm(self.maxSeconds + 1)
        result = self.function(*args)
        signal.alarm(0)
        return result

class Part:
    def __init__(self, name, gradeFunc, maxPoints, maxSeconds, extraCredit, description, basic):
        if not isinstance(name, str):
            raise Exception("Invalid name: %s" % name)
        if gradeFunc != None and not callable(gradeFunc):
            raise Exception("Invalid gradeFunc: %s" % gradeFunc)
        if not isinstance(maxPoints, int):
            raise Exception("Invalid maxPoints: %s" % maxPoints)
        if maxSeconds != None and not isinstance(maxSeconds, int):
            raise Exception("Invalid maxSeconds: %s" % maxSeconds)
        if not description:
            print 'ERROR: description required for part {}'.format(name)
        # Specification of part
        self.name = name
        self.gradeFunc = gradeFunc  # Function to call to do grading
        self.maxPoints = maxPoints  # Maximum number of points attainable on this part
        self.maxSeconds = maxSeconds  # Maximum allowed time that the student's code can take (in seconds)
        self.extraCredit = extraCredit  # Whether this is an extra credit problem
        self.description = description  # Description of this part
        self.basic = basic
        # Grading the part
        self.points = 0
        self.side = None  # Side information
        self.seconds = 0
        self.messages = []
        self.failed = False

    def fail(self):
        self.failed = True

    def is_basic(self):
        return self.gradeFunc is not None and self.basic
    def is_hidden(self):
        return self.gradeFunc is not None and not self.basic
    def is_auto(self):
        return self.gradeFunc is not None
    def is_manual(self):
        return self.gradeFunc is None

class Grader:
    def __init__(self, args=sys.argv):
        self.parts = []  # Parts (to be added)
        self.useSolution = False  # Set to true if we are actually evaluating the hidden test cases

        parser = argparse.ArgumentParser()
        parser.add_argument('--js', action='store_true', help='Write JS file with information about this assignment')
        parser.add_argument('--json', action='store_true', help='Write JSON file with information about this assignment')
        parser.add_argument('--summary', action='store_true', help='Don\'t actually run code')
        parser.add_argument('remainder', nargs=argparse.REMAINDER)
        self.params = parser.parse_args(args[1:])

        args = self.params.remainder
        if len(args) < 1:
            self.mode = AUTO_MODE
            self.selectedPartName = None
        else:
            if args[0] in [BASIC_MODE, AUTO_MODE, ALL_MODE]:
                self.mode = args[0]
                self.selectedPartName = None
            else:
                self.mode = AUTO_MODE
                self.selectedPartName = args[0]

        self.messages = []  # General messages
        self.currentPart = None  # Which part we're grading
        self.fatalError = False  # Set this if we should just stop immediately

    def addBasicPart(self, name, gradeFunc, maxPoints=1, maxSeconds=defaultMaxSeconds, extraCredit=False, description=""):
        """Add a basic test case. The test will be visible to students."""
        self.assertNewName(name)
        part = Part(name, gradeFunc, maxPoints, maxSeconds, extraCredit, description, basic=True)
        self.parts.append(part)

    def addHiddenPart(self, name, gradeFunc, maxPoints=1, maxSeconds=defaultMaxSeconds, extraCredit=False, description=""):
        """Add a hidden test case. The output should NOT be visible to students and so should be inside a BEGIN_HIDE block."""
        self.assertNewName(name)
        part = Part(name, gradeFunc, maxPoints, maxSeconds, extraCredit, description, basic=False)
        self.parts.append(part)

    def addManualPart(self, name, maxPoints, extraCredit=False, description=""):
        """Add a manual part."""
        self.assertNewName(name)
        part = Part(name, None, maxPoints, None, extraCredit, description, basic=False)
        self.parts.append(part)

    def assertNewName(self, name):
        if name in [part.name for part in self.parts]:
            raise Exception("Part name %s already exists" % name)

    # Try to load the module (submission from student).
    def load(self, moduleName):
        try:
            return __import__(moduleName)
        except Exception, e:
            self.fail("Threw exception when importing '%s': %s" % (moduleName, e))
            self.fatalError = True
            return None
        except:
            self.fail("Threw exception when importing '%s'" % moduleName)
            self.fatalError = True
            return None

    def gradePart(self, part):
        print '----- START PART %s%s: %s' % (part.name, ' (extra credit)' if part.extraCredit else '', part.description)
        self.currentPart = part

        startTime = datetime.datetime.now()
        try:
            TimeoutFunction(part.gradeFunc, part.maxSeconds)()  # Call the part's function
        except KeyboardInterrupt:
            raise
        except TimeoutFunctionException as e:
            self.fail('Time limit (%s seconds) exceeded.' % part.maxSeconds)
        except MemoryError as e:
            gc.collect()
            self.fail('Memory limit exceeded.')
        except Exception as e:
            self.fail('Exception thrown: %s -- %s' % (str(type(e)), str(e)))
            self.printException()
        except SystemExit as e:
            # Catch SystemExit raised by exit(), quit() or sys.exit()
            # This class is not a subclass of Exception and we don't
            # expect students to raise it.
            self.fail('Unexpected exit.')
            self.printException()
        endTime = datetime.datetime.now()
        part.seconds = (endTime - startTime).seconds
        if part.is_hidden() and not self.useSolution:
            displayPoints = '???/%s points (hidden test ungraded)' % part.maxPoints
        else:
            displayPoints = '%s/%s points' % (part.points, part.maxPoints)
        print '----- END PART %s [took %s (max allowed %s seconds), %s]' % (part.name, endTime - startTime, part.maxSeconds, displayPoints)
        print

    def getSelectedParts(self):
        parts = []
        for part in self.parts:
            if self.selectedPartName is not None and self.selectedPartName != part.name:
                continue
            if self.mode == BASIC_MODE:
                if part.is_basic():
                    parts.append(part)
            elif self.mode == AUTO_MODE:
                if part.is_auto():
                    parts.append(part)
            elif self.mode == ALL_MODE:
                parts.append(part)
            else:
                raise Exception("Invalid mode: {}".format(self.mode))
        return parts

    def grade(self):
        parts = self.getSelectedParts()

        result = {}
        result['mode'] = self.mode

        # Grade it!
        if not self.params.summary and not self.fatalError:
            print '========== START GRADING'
            for part in parts:
                self.gradePart(part)

            # When students have it (not useSolution), only include basic tests.
            activeParts = [part for part in parts if self.useSolution or part.basic]

            totalPoints = sum(part.points for part in activeParts if not part.extraCredit)
            extraCredit = sum(part.points for part in activeParts if part.extraCredit)
            maxTotalPoints = sum(part.maxPoints for part in activeParts if not part.extraCredit)
            maxExtraCredit = sum(part.maxPoints for part in activeParts if part.extraCredit)

            if not self.useSolution:
                print 'Note that the hidden test cases do not check for correctness.' \
                '\nThey are provided for you to verify that the functions do not crash and run within the time limit.' \
                '\nPoints for these parts not assigned by the grader (indicated by "--").'
            print '========== END GRADING [%d/%d points + %d/%d extra credit]' % \
                (totalPoints, maxTotalPoints, extraCredit, maxExtraCredit)

        resultParts = []
        for part in parts:
            r = {}
            r['name'] = part.name

            if self.params.summary:
                # Just print out specification of the part
                r['description'] = part.description
                r['maxSeconds'] = part.maxSeconds
                r['maxPoints'] = part.maxPoints
                r['extraCredit'] = part.extraCredit
                r['basic'] = part.basic
            else:
                r['points'] = part.points
                r['seconds'] = part.seconds
                if part.side is not None:
                    r['side'] = part.side
                r['messages'] = part.messages
            resultParts.append(r)
        result['parts'] = resultParts

        self.output(self.mode, result)

        def display(name, extraCredit):
            parts = [part for part in self.parts if part.extraCredit == extraCredit]
            maxBasicPoints = sum(part.maxPoints for part in parts if part.is_basic())
            maxHiddenPoints = sum(part.maxPoints for part in parts if part.is_hidden())
            maxManualPoints = sum(part.maxPoints for part in parts if part.is_manual())
            print "Total %s (basic auto/coding + hidden auto/coding + manual/written): %d + %d + %d = %d" % \
                (name,
                maxBasicPoints, maxHiddenPoints, maxManualPoints, \
                maxBasicPoints + maxHiddenPoints + maxManualPoints)
        if self.params.summary:
            display('points', False)
            display('extra credit', True)

    def output(self, mode, result):
        if self.params.json:
            path = 'grader-{}.json'.format(mode)
            with open(path, 'w') as out:
                print >>out, json.dumps(result)
            print 'Wrote to %s' % path
        if self.params.js:
            path = 'grader-{}.js'.format(mode)
            with open(path, 'w') as out:
                print >>out, 'var ' + mode + 'Result = '+ json.dumps(result) + ';'
            print 'Wrote to %s' % path

    # Called by the grader to modify state of the current part

    def assignFullCredit(self):
        if not self.currentPart.failed:
            self.currentPart.points = self.currentPart.maxPoints
        return True

    def assignPartialCredit(self, credit):
        self.currentPart.points = credit
        return True;

    def setSide(self, side):
        self.currentPart.side = side

    def requireIsNumeric(self, answer):
        if isinstance(answer, int) or isinstance(answer, float):
            return self.assignFullCredit()
        else:
            return self.fail("Expected either int or float, but got '%s'" % answer)

    def requireIsOneOf(self, trueAnswers, predAnswer):
        if predAnswer in trueAnswers:
            return self.assignFullCredit()
        else:
            return self.fail("Expected one of %s, but got '%s'" % (trueAnswers, predAnswer))

    def requireIsEqual(self, trueAnswer, predAnswer, tolerance = TOLERANCE):
        if isEqual(trueAnswer, predAnswer, tolerance):
            return self.assignFullCredit()
        else:
            return self.fail("Expected '%s', but got '%s'" % (str(trueAnswer), str(predAnswer)))

    def requireIsLessThan(self, lessThanQuantity, predAnswer ):
        if predAnswer < lessThanQuantity:
            return self.assignFullCredit()
        else:
            return self.fail("Expected to be < %f, but got %f" % (lessThanQuantity, predAnswer) )

    def requireIsGreaterThan(self, greaterThanQuantity, predAnswer ):
        if predAnswer > greaterThanQuantity:
            return self.assignFullCredit()
        else:
            return self.fail("Expected to be > %f, but got %f" %
                    (greaterThanQuantity, predAnswer) )

    def requireIsTrue(self, predAnswer):
        if predAnswer:
            return self.assignFullCredit()
        else:
            return self.fail("Expected to be true, but got false" )

    def fail(self, message):
        print 'FAIL:', message
        self.addMessage(message)
        if self.currentPart:
            self.currentPart.points = 0
            self.currentPart.fail()
        return False

    def printException(self):
        tb = [item for item in traceback.extract_tb(sys.exc_traceback) if not isTracebackItemGrader(item)]
        for item in traceback.format_list(tb):
            self.fail('%s' % item)

    def addMessage(self, message):
        if not self.useSolution:
            print message
        if self.currentPart:
            self.currentPart.messages.append(message)
        else:
            self.messages.append(message)
