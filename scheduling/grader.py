#!/usr/bin/env python
"""
Grader for template assignment
Optionally run as grader.py [basic|all] to run a subset of tests
"""

import random

import graderUtil
import util
import collections
import copy
grader = graderUtil.Grader()
submission = grader.load('submission')


############################################################
# Problem 0a, 0b

grader.addManualPart('0a', 4, description="Define light bulb CSP")
grader.addManualPart('0b', 4, description="Solving the CSP")

############################################################
# Problem 0c: Simple Chain CSP

def test0c():
    solver = submission.BacktrackingSearch()
    solver.solve(submission.create_chain_csp(4))
    grader.requireIsEqual(1, solver.optimalWeight)
    grader.requireIsEqual(2, solver.numOptimalAssignments)
    grader.requireIsEqual(9, solver.numOperations)

grader.addBasicPart('0c-1-basic', test0c, 1, maxSeconds=1, description="Basic test for create_chain_csp")

############################################################
# Problem 1a: N-Queens

def test1a_1():
    nQueensSolver = submission.BacktrackingSearch()
    nQueensSolver.solve(submission.create_nqueens_csp(8))
    grader.requireIsEqual(1.0, nQueensSolver.optimalWeight)
    grader.requireIsEqual(92, nQueensSolver.numOptimalAssignments)
    grader.requireIsEqual(2057, nQueensSolver.numOperations)

grader.addBasicPart('1a-1-basic', test1a_1, 2, maxSeconds=1, description="Basic test for create_nqueens_csp for n=8")

def test1a_2():
    nQueensSolver = submission.BacktrackingSearch()
    nQueensSolver.solve(submission.create_nqueens_csp(3))

grader.addHiddenPart('1a-2-hidden', test1a_2, 1, maxSeconds=1, description="Test create_nqueens_csp with n=3")

def test1a_3():
    nQueensSolver = submission.BacktrackingSearch()
    nQueensSolver.solve(submission.create_nqueens_csp(4))

    nQueensSolver = submission.BacktrackingSearch()
    nQueensSolver.solve(submission.create_nqueens_csp(7))

grader.addHiddenPart('1a-3-hidden', test1a_3, 1, maxSeconds=1, description="Test create_nqueens_csp with different n")

############################################################
# Problem 1b: Most constrained variable


def test1b_1():
    mcvSolver = submission.BacktrackingSearch()
    mcvSolver.solve(submission.create_nqueens_csp(8), mcv = True)
    grader.requireIsEqual(1.0, mcvSolver.optimalWeight)
    grader.requireIsEqual(92, mcvSolver.numOptimalAssignments)
    grader.requireIsEqual(1361, mcvSolver.numOperations)

grader.addBasicPart('1b-1-basic', test1b_1, 1, maxSeconds=1, description="Basic test for MCV with n-queens CSP")

def test1b_2():
    mcvSolver = submission.BacktrackingSearch()
    # We will use our implementation of n-queens csp
    # mcvSolver.solve(our_nqueens_csp(8), mcv = True)

grader.addHiddenPart('1b-2-hidden', test1b_2, 1, maxSeconds=1, description="Test for MCV with n-queens CSP")

def test1b_3():
    mcvSolver = submission.BacktrackingSearch()
    mcvSolver.solve(util.create_map_coloring_csp(), mcv = True)

grader.addHiddenPart('1b-3-hidden', test1b_3, 2, maxSeconds=1, description="Test MCV with different CSPs")

############################################################
# Problem 1c: Arc consistency

def test1c_1():
    acSolver = submission.BacktrackingSearch()
    acSolver.solve(submission.create_nqueens_csp(8), ac3 = True)
    grader.requireIsEqual(1.0, acSolver.optimalWeight)
    grader.requireIsEqual(92, acSolver.numOptimalAssignments)
    grader.requireIsEqual(21, acSolver.firstAssignmentNumOperations)
    grader.requireIsEqual(769, acSolver.numOperations)

grader.addBasicPart('1c-1-basic', test1c_1, 1, maxSeconds=1, description="Basic test for AC-3 with n-queens CSP")

def test1c_2():
    acSolver = submission.BacktrackingSearch()
    acSolver.solve(util.create_map_coloring_csp(), ac3 = True)

grader.addHiddenPart('1c-2-hidden', test1c_2, 2, maxSeconds=1, description="Test AC-3 for map coloring CSP")

def test1c_3():
    acSolver = submission.BacktrackingSearch()
    # We will use our implementation of n-queens csp
    # acSolver.solve(our_nqueens_csp(8), mcv = True, ac3 = True)

grader.addHiddenPart('1c-3-hidden', test1c_3, 1, maxSeconds=1, description="Test MCV+AC-3 for n-queens CSP with n=8")

def test1c_4():
    acSolver = submission.BacktrackingSearch()
    # We will use our implementation of n-queens csp
    # acSolver.solve(our_nqueens_csp(7), mcv = True, ac3 = True)

grader.addHiddenPart('1c-4-hidden', test1c_4, 2, maxSeconds=1, description="Test MCV+AC-3 for n-queens CSP with n=7")

def test1c_5():
    acSolver = submission.BacktrackingSearch()
    acSolver.solve(util.create_map_coloring_csp(), mcv = True, ac3 = True)

grader.addHiddenPart('1c-5-hidden', test1c_5, 2, maxSeconds=1, description="Test MCV+AC-3 for map coloring CSP")

############################################################
# Problem 2a

grader.addManualPart('2a', 4, description="Writeup of 2a")

############################################################
# Problem 2b: Sum factor

def test2b_1():
    csp = util.CSP()
    csp.add_variable('A', [0, 1, 2, 3])
    csp.add_variable('B', [0, 6, 7])
    csp.add_variable('C', [0, 5])

    sumVar = submission.get_sum_variable(csp, 'sum-up-to-15', ['A', 'B', 'C'], 15)
    csp.add_unary_factor(sumVar, lambda n: n in [12, 13])
    sumSolver = submission.BacktrackingSearch()
    sumSolver.solve(csp)
    grader.requireIsEqual(4, sumSolver.numOptimalAssignments)

    csp.add_unary_factor(sumVar, lambda n: n == 12)
    sumSolver = submission.BacktrackingSearch()
    sumSolver.solve(csp)
    grader.requireIsEqual(2, sumSolver.numOptimalAssignments)

grader.addBasicPart('2b-1-basic', test2b_1, 2, maxSeconds=1, description="Basic test for get_sum_variable")

def test2b_2():
    csp = util.CSP()
    sumVar = submission.get_sum_variable(csp, 'zero', [], 15)
    sumSolver = submission.BacktrackingSearch()
    sumSolver.solve(csp)

    csp.add_unary_factor(sumVar, lambda n: n > 0)
    sumSolver = submission.BacktrackingSearch()
    sumSolver.solve(csp)

grader.addHiddenPart('2b-2-hidden', test2b_2, 1, maxSeconds=1, description="Test get_sum_variable with empty list of variables")

def test2b_3():
    csp = util.CSP()
    csp.add_variable('A', [0, 1, 2])
    csp.add_variable('B', [0, 1, 2])
    csp.add_variable('C', [0, 1, 2])

    sumVar = submission.get_sum_variable(csp, 'sum-up-to-7', ['A', 'B', 'C'], 7)
    sumSolver = submission.BacktrackingSearch()
    sumSolver.solve(csp)

    csp.add_unary_factor(sumVar, lambda n: n == 6)
    sumSolver = submission.BacktrackingSearch()
    sumSolver.solve(csp)

grader.addHiddenPart('2b-3-hidden', test2b_3, 2, maxSeconds=1, description="Test get_sum_variable with different variables")

############################################################
# Problem 3

def verify_schedule(bulletin, profile, schedule, checkUnits = True):
    """
    Returns true if the schedule satisifies all requirements given by the profile.
    """
    goodSchedule = True
    all_courses_taking = dict((s[1], s[0]) for s in schedule)

    # No course can be taken twice.
    goodSchedule *= len(all_courses_taking) == len(schedule)
    if not goodSchedule:
        print 'course repeated'
        return False

    # Each course must be offered in that quarter.
    goodSchedule *= all(bulletin.courses[s[1]].is_offered_in(s[0]) for s in schedule)
    if not goodSchedule:
        print 'course not offered'
        return False

    # If specified, only take the course at the requested time.
    for req in profile.requests:
        if len(req.quarters) == 0: continue
        goodSchedule *= all([s[0] in req.quarters for s in schedule if s[1] in req.cids])
    if not goodSchedule:
        print 'course taken at wrong time'
        return False

    # If a request has multiple courses, at most one is chosen.
    for req in profile.requests:
        if len(req.cids) == 1: continue
        goodSchedule *= len([s for s in schedule if s[1] in req.cids]) <= 1
    if not goodSchedule:
        print 'more than one exclusive group of courses is taken'
        return False

    # Must take a course after the prereqs
    for req in profile.requests:
        if len(req.prereqs) == 0: continue
        cids = [s for s in schedule if s[1] in req.cids] # either empty or 1 element
        if len(cids) == 0: continue
        quarter, cid, units = cids[0]
        for prereq in req.prereqs:
            if prereq in profile.taking:
                goodSchedule *= prereq in all_courses_taking
                if not goodSchedule:
                    print 'not all prereqs are taken'
                    return False
                goodSchedule *= profile.quarters.index(quarter) > \
                    profile.quarters.index(all_courses_taking[prereq])
    if not goodSchedule:
        print 'course is taken before prereq'
        return False

    if not checkUnits: return goodSchedule
    # Check for unit loads
    unitCounters = collections.Counter()
    for quarter, c, units in schedule:
        unitCounters[quarter] += units
    goodSchedule *= all(profile.minUnits <= u and u <= profile.maxUnits \
        for k, u in unitCounters.items())
    if not goodSchedule:
        print 'unit count out of bound for quarter'
        return False

    return goodSchedule

# Load all courses.
bulletin = util.CourseBulletin('courses.json')

############################################################
# Problem 3a: Quarter specification

def test3a_1():
    profile = util.Profile(bulletin, 'profile3a.txt')
    cspConstructor = submission.SchedulingCSPConstructor(bulletin, copy.deepcopy(profile))
    csp = cspConstructor.get_basic_csp()
    cspConstructor.add_quarter_constraints(csp)
    alg = submission.BacktrackingSearch()
    alg.solve(csp)

    # Verify correctness.
    grader.requireIsEqual(3, alg.numOptimalAssignments)
    sol = util.extract_course_scheduling_solution(profile, alg.optimalAssignment)
    for assignment in alg.allAssignments:
        sol = util.extract_course_scheduling_solution(profile, assignment)
        grader.requireIsTrue(verify_schedule(bulletin, profile, sol, False))

grader.addBasicPart('3a-1-basic', test3a_1, 2, maxSeconds=4, description="Basic test for add_quarter_constraints")

def test3a_2():
    profile = util.Profile(bulletin, 'profile3a1.txt')
    cspConstructor = submission.SchedulingCSPConstructor(bulletin, copy.deepcopy(profile))
    csp = cspConstructor.get_basic_csp()
    cspConstructor.add_quarter_constraints(csp)
    alg = submission.BacktrackingSearch()
    alg.solve(csp)

    # Verify correctness.

grader.addHiddenPart('3a-2-hidden', test3a_2, 2, maxSeconds=3, description="Test add_quarter_constraints with different profiles")

def test3a_3():
    profile = util.Profile(bulletin, 'profile3a2.txt')
    cspConstructor = submission.SchedulingCSPConstructor(bulletin, copy.deepcopy(profile))
    csp = cspConstructor.get_basic_csp()
    cspConstructor.add_quarter_constraints(csp)
    alg = submission.BacktrackingSearch()
    alg.solve(csp)

    # Verify correctness.

grader.addHiddenPart('3a-3-hidden', test3a_3, 1, maxSeconds=3, description="Test add_quarter_constraints with no quarter specified")

############################################################
# Problem 3b: Unit load

def test3b_1():
    profile = util.Profile(bulletin, 'profile3b.txt')
    cspConstructor = submission.SchedulingCSPConstructor(bulletin, copy.deepcopy(profile))
    csp = cspConstructor.get_basic_csp()
    cspConstructor.add_unit_constraints(csp)
    alg = submission.BacktrackingSearch()
    alg.solve(csp)

    # Verify correctness.
    grader.requireIsEqual(15, alg.numOptimalAssignments)
    for assignment in alg.allAssignments:
        sol = util.extract_course_scheduling_solution(profile, assignment)
        grader.requireIsTrue(verify_schedule(bulletin, profile, sol))

grader.addBasicPart('3b-1-basic', test3b_1, 2, maxSeconds=7, description="Basic test for add_unit_constraints")

def test3b_2():
    profile = util.Profile(bulletin, 'profile3b1.txt')
    cspConstructor = submission.SchedulingCSPConstructor(bulletin, copy.deepcopy(profile))
    csp = cspConstructor.get_basic_csp()
    cspConstructor.add_unit_constraints(csp)
    alg = submission.BacktrackingSearch()
    alg.solve(csp)

    # Verify correctness.

grader.addHiddenPart('3b-2-hidden', test3b_2, 3, maxSeconds=3, description="Test add_unit_constraints with different profiles")

def test3b_3():
    profile = util.Profile(bulletin, 'profile3b2.txt')
    cspConstructor = submission.SchedulingCSPConstructor(bulletin, copy.deepcopy(profile))
    csp = cspConstructor.get_basic_csp()
    cspConstructor.add_all_additional_constraints(csp)
    alg = submission.BacktrackingSearch()
    alg.solve(csp)

    # Verify correctness.

grader.addHiddenPart('3b-3-hidden', test3b_3, 1, maxSeconds=4, description="Test unsatisfiable scheduling")

def test3b_4():
    profile = util.Profile(bulletin, 'profile3b3.txt')
    cspConstructor = submission.SchedulingCSPConstructor(bulletin, copy.deepcopy(profile))
    csp = cspConstructor.get_basic_csp()
    cspConstructor.add_all_additional_constraints(csp)
    alg = submission.BacktrackingSearch()
    alg.solve(csp, mcv = True, ac3 = True)

    # Verify correctness.

grader.addHiddenPart('3b-4-hidden', test3b_4, 3, maxSeconds=25, description="Test MVC+AC-3+all additional constraints")

grader.addManualPart('3c', 2, description="Your own schedule")
grader.addManualPart('4a', 2, extraCredit=True, description="Worst-case treewidth")
grader.addManualPart('4b', 6, extraCredit=True, description="Efficient algorithm")

grader.grade()
