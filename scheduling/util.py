import json, re

# General code for representing a weighted CSP (Constraint Satisfaction Problem).
# All variables are being referenced by their index instead of their original
# names.
class CSP:
    def __init__(self):
        # Total number of variables in the CSP.
        self.numVars = 0

        # The list of variable names in the same order as they are added. A
        # variable name can be any hashable objects, for example: int, str,
        # or any tuple with hashtable objects.
        self.variables = []

        # Each key K in this dictionary is a variable name.
        # values[K] is the list of domain values that variable K can take on.
        self.values = {}

        # Each entry is a unary factor table for the corresponding variable.
        # The factor table corresponds to the weight distribution of a variable
        # for all added unary factor functions. If there's no unary function for 
        # a variable K, there will be no entry for K in unaryFactors.
        # E.g. if B \in ['a', 'b'] is a variable, and we added two
        # unary factor functions f1, f2 for B,
        # then unaryFactors[B]['a'] == f1('a') * f2('a')
        self.unaryFactors = {}

        # Each entry is a dictionary keyed by the name of the other variable
        # involved. The value is a binary factor table, where each table
        # stores the factor value for all possible combinations of
        # the domains of the two variables for all added binary factor
        # functions. The table is represented as a dictionary of dictionary.
        #
        # As an example, if we only have two variables
        # A \in ['b', 'c'],  B \in ['a', 'b']
        # and we've added two binary functions f1(A,B) and f2(A,B) to the CSP,
        # then binaryFactors[A][B]['b']['a'] == f1('b','a') * f2('b','a').
        # binaryFactors[A][A] should return a key error since a variable
        # shouldn't have a binary factor table with itself.

        self.binaryFactors = {}

    def add_variable(self, var, domain):
        """
        Add a new variable to the CSP.
        """
        if var in self.variables:
            raise Exception("Variable name already exists: %s" % str(var))

        self.numVars += 1
        self.variables.append(var)
        self.values[var] = domain
        self.unaryFactors[var] = None
        self.binaryFactors[var] = dict()


    def get_neighbor_vars(self, var):
        """
        Returns a list of variables which are neighbors of |var|.
        """
        return self.binaryFactors[var].keys()

    def add_unary_factor(self, var, factorFunc):
        """
        Add a unary factor function for a variable. Its factor
        value across the domain will be *merged* with any previously added
        unary factor functions through elementwise multiplication.

        How to get unary factor value given a variable |var| and
        value |val|?
        => csp.unaryFactors[var][val]
        """
        factor = {val:float(factorFunc(val)) for val in self.values[var]}
        if self.unaryFactors[var] is not None:
            assert len(self.unaryFactors[var]) == len(factor)
            self.unaryFactors[var] = {val:self.unaryFactors[var][val] * \
                factor[val] for val in factor}
        else:
            self.unaryFactors[var] = factor

    def add_binary_factor(self, var1, var2, factor_func):
        """
        Takes two variable names and a binary factor function
        |factorFunc|, add to binaryFactors. If the two variables already
        had binaryFactors added earlier, they will be *merged* through element
        wise multiplication.

        How to get binary factor value given a variable |var1| with value |val1| 
        and variable |var2| with value |val2|?
        => csp.binaryFactors[var1][var2][val1][val2]
        """
        # never shall a binary factor be added over a single variable
        try:
            assert var1 != var2
        except:
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print '!! Tip:                                                                       !!'
            print '!! You are adding a binary factor over a same variable...                  !!'
            print '!! Please check your code and avoid doing this.                               !!'
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            raise

        self.update_binary_factor_table(var1, var2,
            {val1: {val2: float(factor_func(val1, val2)) \
                for val2 in self.values[var2]} for val1 in self.values[var1]})
        self.update_binary_factor_table(var2, var1, \
            {val2: {val1: float(factor_func(val1, val2)) \
                for val1 in self.values[var1]} for val2 in self.values[var2]})

    def update_binary_factor_table(self, var1, var2, table):
        """
        Private method you can skip for 0c, might be useful for 1c though.
        Update the binary factor table for binaryFactors[var1][var2].
        If it exists, element-wise multiplications will be performed to merge
        them together.
        """
        if var2 not in self.binaryFactors[var1]:
            self.binaryFactors[var1][var2] = table
        else:
            currentTable = self.binaryFactors[var1][var2]
            for i in table:
                for j in table[i]:
                    assert i in currentTable and j in currentTable[i]
                    currentTable[i][j] *= table[i][j]

############################################################
# CSP examples.

def create_map_coloring_csp():
    """
    A classic CSP of coloring the map of Australia with 3 colors.
    """
    csp = CSP()
    provinces = ['WA', 'NT', 'Q', 'NSW', 'V', 'SA', 'T']
    neighbors = {
        'SA' : ['WA', 'NT', 'Q', 'NSW', 'V'],
        'NT' : ['WA', 'Q'],
        'NSW' : ['Q', 'V']
    }
    colors = ['red', 'blue', 'green']
    def are_neighbors(a, b):
        return (a in neighbors and b in neighbors[a]) or \
            (b in neighbors and a in neighbors[b])

    # Add the variables and binary factors
    for p in provinces:
        csp.add_variable(p, colors)
    for p1 in provinces:
        for p2 in provinces:
            if are_neighbors(p1, p2):
                # Neighbors cannot have the same color
                csp.add_binary_factor(p1, p2, lambda x, y : x != y)
    return csp

def create_weighted_csp():
    """
    An example demonstrating how to create a weighted CSP.
    """
    csp = CSP()
    csp.add_variable('A', [1, 2, 3])
    csp.add_variable('B', [1, 2, 3, 4, 5])
    csp.add_unary_factor('A', lambda x : x > 1)
    csp.add_unary_factor('A', lambda x : x != 2)
    csp.add_unary_factor('B', lambda y : 1.0 / y)
    csp.add_binary_factor('A', 'B', lambda x, y : x != y)
    return csp

def get_or_variable(csp, name, variables, value):
    """
    Create a new variable with domain [True, False] that can only be assigned to
    True iff at least one of the |variables| is assigned to |value|. You should
    add any necessary intermediate variables, unary factors, and binary
    factors to achieve this. Then, return the name of this variable.

    @param name: Prefix of all the variables that are going to be added.
        Can be any hashable objects. For every variable |var| added in this
        function, it's recommended to use a naming strategy such as
        ('or', |name|, |var|) to avoid conflicts with other variable names.
    @param variables: A list of variables in the CSP that are participating
        in this OR function. Note that if this list is empty, then the returned
        variable created should never be assigned to True.
    @param value: For the returned OR variable being created to be assigned to
        True, at least one of these variables must have this value.

    @return result: The OR variable's name. This variable should have domain
        [True, False] and constraints s.t. it's assigned to True iff at least
        one of the |variables| is assigned to |value|.
    """
    result = ('or', name, 'aggregated')
    csp.add_variable(result, [True, False])

    # no input variable, result should be False
    if len(variables) == 0:
        csp.add_unary_factor(result, lambda val: not val)
        return result

    # Let the input be n variables X0, X1, ..., Xn.
    # After adding auxiliary variables, the factor graph will look like this:
    #
    # ^--A0 --*-- A1 --*-- ... --*-- An --*-- result--^^
    #    |        |                  |
    #    *        *                  *
    #    |        |                  |
    #    X0       X1                 Xn
    #
    # where each "--*--" is a binary constraint and "--^" and "--^^" are unary
    # constraints. The "--^^" constraint will be added by the caller.
    for i, X_i in enumerate(variables):
        # create auxiliary variable for variable i
        # use systematic naming to avoid naming collision
        A_i = ('or', name, i)
        # domain values:
        # - [ prev ]: condition satisfied by some previous X_j
        # - [equals]: condition satisfied by X_i
        # - [  no  ]: condition not satisfied yet
        csp.add_variable(A_i, ['prev', 'equals', 'no'])

        # incorporate information from X_i
        def factor(val, b):
            if (val == value): return b == 'equals'
            return b != 'equals'
        csp.add_binary_factor(X_i, A_i, factor)

        if i == 0:
            # the first auxiliary variable, its value should never
            # be 'prev' because there's no X_j before it
            csp.add_unary_factor(A_i, lambda b: b != 'prev')
        else:
            # consistency between A_{i-1} and A_i
            def factor(b1, b2):
                if b1 in ['equals', 'prev']: return b2 != 'no'
                return b2 != 'prev'
            csp.add_binary_factor(('or', name, i - 1), A_i, factor)

    # consistency between A_n and result
    # hacky: reuse A_i because of python's loose scope
    csp.add_binary_factor(A_i, result, lambda val, res: res == (val != 'no'))
    return result

############################################################
# Course scheduling specifics.

# Information about a course:
# - self.cid: course ID (e.g., CS221)
# - self.name: name of the course (e.g., Artificial Intelligence)
# - self.quarters: quarters without the years (e.g., Aut)
# - self.minUnits: minimum allowed units to take this course for (e.g., 3)
# - self.maxUnits: maximum allowed units to take this course for (e.g., 3)
# - self.prereqs: list of course IDs that must be taken before taking this course.
class Course:
    def __init__(self, info):
        self.__dict__.update(info)

    # Return whether this course is offered in |quarter| (e.g., Aut2013).
    def is_offered_in(self, quarter):
        return any(quarter.startswith(q) for q in self.quarters)

    def short_str(self): return '%s: %s' % (self.cid, self.name)

    def __str__(self):
        return 'Course{cid: %s, name: %s, quarters: %s, units: %s-%s, prereqs: %s}' % (self.cid, self.name, self.quarters, self.minUnits, self.maxUnits, self.prereqs)


# Information about all the courses
class CourseBulletin:
    def __init__(self, coursesPath):
        """
        Initialize the bulletin.

        @param coursePath: Path of a file containing all the course information.
        """
        # Read courses (JSON format)
        self.courses = {}
        info = json.loads(open(coursesPath).read())
        for courseInfo in info.values():
            course = Course(courseInfo)
            self.courses[course.cid] = course

# A request to take one of a set of courses at some particular times.
class Request:
    def __init__(self, cids, quarters, prereqs, weight):
        """
        Create a Request object.

        @param cids: list of courses from which only one is chosen.
        @param quarters: list of strings representing the quarters (e.g. Aut2013)
            the course must be taken in.
        @param prereqs: list of strings representing courses pre-requisite of
            the requested courses separated by comma. (e.g. CS106,CS103,CS109)
        @param weight: real number denoting how much the student wants to take
            this/or one the requested courses.
        """
        self.cids = cids
        self.quarters = quarters
        self.prereqs = prereqs
        self.weight = weight

    def __str__(self):
        return 'Request{%s %s %s %s}' % \
            (self.cids, self.quarters, self.prereqs, self.weight)

    def __eq__(self, other): return str(self) == str(other)

    def __cmp__(self, other): return cmp(str(self), str(other))

    def __hash__(self): return hash(str(self))

    def __repr__(self): return str(self)

# Given the path to a preference file and a
class Profile:
    def __init__(self, bulletin, prefsPath):
        """
        Parses the preference file and generate a student's profile.

        @param prefsPath: Path to a txt file that specifies a student's request
            in a particular format.
        """
        self.bulletin = bulletin

        # Read preferences
        self.minUnits = 9  # minimum units per quarter
        self.maxUnits = 12 # maximum units per quarter
        self.quarters = [] # (e.g., Aut2013)
        self.taken = set()  # Courses that we've taken
        self.requests = []
        for line in open(prefsPath):
            m = re.match('(.*)\\s*#.*', line)
            if m: line = m.group(1)
            line = line.strip()
            if len(line) == 0: continue

            # Units
            m = re.match('minUnits (.+)', line)
            if m:
                self.minUnits = int(m.group(1))
                continue
            m = re.match('maxUnits (.+)', line)
            if m:
                self.maxUnits = int(m.group(1))
                continue

            # Register a quarter (quarter, year)
            m = re.match('register (.+)', line)
            if m:
                quarter = m.group(1)
                m = re.match('(Aut|Win|Spr|Sum)(\d\d\d\d)', quarter)
                if not m:
                    raise Exception("Invalid quarter '%s', want something like Spr2013" % quarter)
                self.quarters.append(quarter)
                continue

            # Already taken a course
            m = re.match('taken (.+)', line)
            if m:
                cid = self.ensure_course_id(m.group(1))
                self.taken.add(cid)
                continue

            # Request to take something
            # also match & to parse MS&E courses correctly
            m = re.match('request ([\w&]+)(.*)', line)
            if m:
                cids = [self.ensure_course_id(m.group(1))]
                quarters = []
                prereqs = []
                weight = 1  # Default: would want to take
                args = m.group(2).split()
                for i in range(0, len(args), 2):
                    if args[i] == 'or':
                        cids.append(self.ensure_course_id(args[i+1]))
                    elif args[i] == 'after':  # Take after a course
                        prereqs = [self.ensure_course_id(c) for c in args[i+1].split(',')]
                    elif args[i] == 'in':  # Take in a particular quarter
                        quarters = [self.ensure_quarter(q) for q in args[i+1].split(',')]
                    elif args[i] == 'weight':  # How much is taking this class worth
                        weight = float(args[i+1])
                    elif args[i].startswith('#'): # Comments
                        break
                    else:
                        raise Exception("Invalid arguments: %s" % args)
                self.requests.append(Request(cids, quarters, prereqs, weight))
                continue

            raise Exception("Invalid command: '%s'" % line)

        # Determine any missing prereqs and validate the request.
        self.taken = set(self.taken)
        self.taking = set()

        # Make sure each requested course is taken only once
        for req in self.requests:
            for cid in req.cids:
                if cid in self.taking:
                    raise Exception("Cannot request %s more than once" % cid)
            self.taking.update(req.cids)

        # Make sure user-designated prerequisites are requested
        for req in self.requests:
            for prereq in req.prereqs:
                if prereq not in self.taking:
                    raise Exception("You must take " + prereq)

        # Add missing prerequisites if necessary
        for req in self.requests:
            for cid in req.cids:
                course = self.bulletin.courses[cid]
                for prereq_cid in course.prereqs:
                    if prereq_cid in self.taken:
                        continue
                    elif prereq_cid in self.taking:
                        if prereq_cid not in req.prereqs:
                            req.prereqs.append(prereq_cid)
                            print "INFO: Additional prereqs inferred: %s after %s" % \
                                (cid, prereq_cid)
                    else:
                        print "WARNING: missing prerequisite of %s -- %s; you should add it as 'taken' or 'request'" %  \
                            (cid, self.bulletin.courses[prereq_cid].short_str())

    def print_info(self):
        print "Units: %d-%d" % (self.minUnits, self.maxUnits)
        print "Quarter: %s" % self.quarters
        print "Taken: %s" % self.taken
        print "Requests:"
        for req in self.requests: print '  %s' % req

    def ensure_course_id(self, cid):
        if cid not in self.bulletin.courses:
            raise Exception("Invalid course ID: '%s'" % cid)
        return cid

    def ensure_quarter(self, quarter):
        if quarter not in self.quarters:
            raise Exception("Invalid quarter: '%s'" % quarter)
        return quarter

def extract_course_scheduling_solution(profile, assign):
    """
    Given an assignment returned from the CSP solver, reconstruct the plan. It
    is assume that (req, quarter) is used as the variable to indicate if a request
    is being assigned to a speific quarter, and (quarter, cid) is used as the variable
    to indicate the number of units the course should be taken in that quarter.

    @param profile: A student's profile and requests
    @param assign: An assignment of your variables as generated by the CSP
        solver.

    @return result: return a list of (quarter, courseId, units) tuples according
        to your solution sorted in chronological of the quarters provided.
    """
    result = []
    if not assign: return result
    for quarter in profile.quarters:
        for req in profile.requests:
            cid = assign[(req, quarter)]
            if cid == None: continue
            if (cid, quarter) not in assign:
                result.append((quarter, cid, None))
            else:
                result.append((quarter, cid, assign[(cid, quarter)]))
    return result

def print_course_scheduling_solution(solution):
    """
    Print a schedule in a nice format based on a solution.

    @para solution: A list of (quarter, course, units). Units can be None, in which
        case it won't get printed.
    """

    if solution == None:
        print "No schedule found that satisfied all the constraints."
    else:
        print "Here's the best schedule:"
        print "Quarter\t\tUnits\tCourse"
        for quarter, course, units in solution:
            if units != None:
                print "  %s\t%s\t%s" % (quarter, units, course)
            else:
                print "  %s\t%s\t%s" % (quarter, 'None', course)
