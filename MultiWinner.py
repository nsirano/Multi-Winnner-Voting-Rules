import copy
import math
import operator
import sys

from preference import Preference

import pprint
pp = pprint.PrettyPrinter(indent=4).pprint

def bordaScore(pref, alt):
    # Get alternative rankings from Preference object
    rankMap = pref.getRankMap()
    # Return the Borda Score if the alternative is recognized
    #  (Last ranking borda score of 1)
    try:
        rank = rankMap[alt]
        score = (len(rankMap) - (rank-1))
        return score
    # Return 0 otherwise, allowing for truncated ballots
    except KeyError:
        return 0

class SingleAssignment:
    def __init__(self, prefObj, altID='<none>'):
        self.pref = prefObj
        self.alt = altID

    def getSatScore(self, scoreType='borda'):
        scoreType = scoreType.lower()

        if (scoreType == 'borda'):
            return bordaScore(self.pref, self.alt)

        else:
            print('error: unknown scoring method')

class FullAssignment:
    def __init__(self, assignmentObjList=[], unmatchedAltList=[]):
        self.assignments = assignmentObjList
        self.unmatchedAlts = unmatchedAltList

    def getSatScore(self, scoreType='borda'):
        scoreType = scoreType.lower()

        if (scoreType == 'borda'):
            totalScore = 0
            for a in self.assignments:
                totalScore += a.getSatScore(scoreType)
            return totalScore

        else:
            print('error: unknown scoring method')

def usage():
    """
    Prints usage information.
    """
    print("python MultiWinner.py <data.txt> <comm_size>")

def check_arguments():
    """
    Checks to see if enough arguments are passed to MultiWinner.py.
    """
    if len(sys.argv) < 2:
        print("ERROR: Not enough arguments.")
        usage()
        sys.exit(1)

def sign(n):
    """
    Checks the sign of a number.
    Returns  1 if positive.
    Returns -1 if negative.
    """
    return int(n > 0) - int(n < 0)

def create_wmgMap(ranking):
    """
    Create a weighted majority graph mapping from a voter's preference rankings.
    Each wmgMap is a dictionary of candidates that each maps to another
    dictionary of candidates, excluding the first candidate. The second
    dictionary then maps to '1' if the first candidate is ranked higher than the
    second and maps to '-1' if the first candidate is ranked lower.
    """
    wmgMap = dict()
    alternatives = sorted(ranking)

    # For each alternative as the first candidate,
    for a in range(len(alternatives)):
        wmgMap[a] = dict()

        # For each alternative that is not the first candidate
        for alt in range(len(alternatives)):
            if alt != a:
                alt_index = ranking.index(alternatives[alt])
                a_index   = ranking.index(alternatives[a])
                wmgMap[a][alt] = sign(alt_index - a_index)

    return wmgMap

def create_wmgMap2(ranking):
    """
    Create a weighted majority graph mapping from a voter's preference rankings.
    Each wmgMap is a dictionary of candidates that each maps to another
    dictionary of candidates, excluding the first candidate. The second
    dictionary then maps to '1' if the first candidate is ranked higher than the
    second and maps to '-1' if the first candidate is ranked lower.
    """
    wmgMap = dict()
    alternatives = sorted(ranking) # ?: I don't think this is necessary that they are in alphbetical order?

    # For each alternative as the first candidate,
    for a in alternatives:
        wmgMap[a] = dict()

        # For each alternative that is not the first candidate
        for alt in alternatives:
            if alt != a:
                alt_index = ranking.index(alt)
                a_index   = ranking.index(a)
                wmgMap[a][alt] = sign(alt_index - a_index)

    return wmgMap

def parse_data(filename, agents=[], alternatives=[]):
    """
    Parses voter data from input file.
    """
    f = open(sys.argv[1], "r")
    for line in f:
        ranking = line.rstrip().split(',')
        if len(ranking) > len(alternatives):
            alternatives = sorted(ranking)

        wmgMap = create_wmgMap(ranking)
        agents.append(Preference(wmgMap))

    pp(wmgMap)
    return agents, alternatives

def algoA(comm_size, alts, agents):
    """
    Algorithm A
    """
    if comm_size <= 2:
        # Betzler
        return

    num_assigned = len(agents)/comm_size
    print(num_assigned, "num_assigned")

    alts_left = list(alts)
    agents_left = (a.getOrderVector() for a in agents)

    phi = dict()

    # For each committee member
    for i in range(1, comm_size + 1):
        score = dict()
        bests = dict()

        # For each alternative,
        alt_bests = []
        for alt in alts_left:
            # Sort the agents by ranking of given alt, most preferred first
            agents_left = list(sorted(agents_left, key=lambda agent:
                                                        agent.index(alt)))

            print
            for a in agents_left: pp((a.name, a.prefs)); print("TEST 0")

            # Add the first n/K agents to the best fit for the given alternative
            alt_bests = []
            for n in range(int(num_assigned)):
                if agents_left:
                    alt_bests.append(agents_left.pop(0))
                    print(alt_bests[n].name), "TEST 1"

            pp(alt_bests)
            print(alt, "ALT")
            bests[alt] = list(alt_bests)
            pp(bests)

            # For each alternative relative to each agent,
            score[alt] = 0
            for j in alt_bests:
                # Add the borda score
                score[alt] += len(alts) - j.prefs.index(alt)


        best_alt = max(score.iteritems(), key=operator.itemgetter(1))[0]
        print(i, best_alt), "TEST 2"
        print(bests[best_alt]), "TEST 3"
        for j in bests[best_alt]:
            print(j.name, best_alt), "TEST 4"
            phi[j.name] = best_alt

        print(i), "test 5"
        print(alts_left, best_alt), "test 6"
        alts_left.remove(best_alt)

    return phi

def algoC_CC(K, alts, agents, d):
    """
	Chamberlin Courant Multi-Winner Approximation Algorithm C:

    Algorithm C is a further heuristic improvement over Algorithm B. This time
    the idea is that instead of keeping only one partial function 'phi' that is
    iteratively extended up to the full assignment, we keep a list of up to d
    partial assignment functions, where 'd' is a parameter of the algorithm. At
    each iteration, for each assignment function 'phi' among the 'd' stored ones
    and for each alternative a to which 'phi' has not assigned agents yet, we
    compute an optimal extension of this 'phi' that assigns agents to 'a'. As a
    result we obtain possibly more than 'd' (partial) assignment functions. For
    the next iteration we keep those d that give highest satisfaction.
	"""
	# list of partial assignments
    Par = []
	# initial assignment function
    af0 = AssignmentFunction(agents, alts)
    Par.append(af0)
	# Build the partial assignments up, iteratively adding 1 candidate at a time
    for i in range(K):
		# create a new partial assignment list for testing
        newPar = []
		# for each of the saved partial assignments in list Par
        for af in Par:
			# attempt to place every alternative in committee seat 'i' for current partial assignment
            for alt in af.unmatchedAlts:
                af_prime = copy.deepcopy(af) # this should be a deep copy
                af_prime.unmatchedAlts.remove(alt)
				# assign every agent that prefers this alterative as their assigned alternative
				#   regardless of whether or not they have been previously assigned
                for agent in af_prime.agents:
                    if (bordaSat(agent.prefs, alt) > bordaSat(agent.prefs, agent.alt)):
                        agent.alt = alt
                newPar.append(af_prime)
			# Sort list of partial assignments by total borda satisfaction
            newPar.sort(key=bordaTotalSat, reverse=True)
        # Keep only the top 'd' partial assignments for use in the next iteration
        L = min(len(newPar), d)
        Par = newPar[:L]

    return Par

def algoC_CC2(comm_size, alts, agents, d):
    # Store Preference objects (agents) in SingleAssignment objects
    assignments = []
    for a in agents:
        assignments.append(SingleAssignment(a))

    # List of partial assignments (i.e. incomplete committees)
    paList = []
    # Initial default partial assignment (none assigned)
    pa0 = FullAssignment(assignments, alts)
    paList.append(pa0)

    # Iteratively build up partial assignments by adding 1 alternative at a time
    for i in range(comm_size):
        tmpList = []
        # Extend every partial assignment to include 1 more alternative, trying every permutation
        for pa in paList:
            for alt in pa.unmatchedAlts:
                extendedPA = copy.deepcopy(pa)
                # Assign every agent to the current alternative if preferred
                #  regardles of previous assignments
                for a in extendedPA.assignments:
                    if (bordaSat(a.pref, alt) > bordaSat(a.pref, a.alt)):
                        a.alt = alt
                # The alternative has now been matched
                extendedPA.unmatchedAlts.remove(alt)
                # Save the new extended partial assignment
                tmpList.append(extendedPA)
        # Sort the partial assignments by total satisfaction score
        tmpList = sorted(tmpList, key=lambda pa: pa.getSatScore(), reverse=True)
        # Keep the top L partial assignments for use in the next iteration
        L = min(len(tmpList), d)
        paList = tmpList[:L]

    return paList


def algoC_M(K, N, alts, agents, d):
    """
	Monroe Multi-Winner Approximation Algorithm C:

	Algorithm C is a further heuristic improvement over Algorithm B. This time
    the idea is that instead of keeping only one partial function 'phi' that is
    iteratively extended up to the full assignment, we keep a list of up to 'd'
    partial assignment functions, where 'd' is a parameter of the algorithm. At
    each iteration, for each assignment function 'phi' among the 'd' stored ones
    and for each alternative a to which 'phi' has not assigned agents yet, we
    compute an optimal extension of this 'phi' that assigns agents to 'a'. As a
    result we obtain possibly more than 'd' (partial) assignment functions. For
    the next iteration we keep those 'd' that give highest satisfaction.
    """
	# list of partial assignments
    Par = []
	# initial assignment function
    af0 = AssignmentFunction(agents, alts)
    Par.append(af0)
	# Build the partial assignments up, iteratively adding 1 candidate at a time
    for i in range(K):
		# Create a new partial assignment list for testing
        newPar = []
		# for each of the saved partial assignments in list Par
        for af in Par:
			# attempt to place every alternative in committee seat 'i' for current partial assignment
            for alt in af.unmatchedAlts:
                af_prime = copy.deepcopy(af) # this should be a deep copy
                af_prime.unmatchedAlts.remove(alt)
				# sort agents by the preference for the candidate alternative currently being considered
                sortedAgentsByPref = agentSort(af_prime.agents, alt)
                #print('sortedAgentsByPref=', len(sortedAgentsByPref))
                af_prime.agents = sortedAgentsByPref
				# assign only N/K agents to the current candidate alternative
                counter = 0
                for a in af_prime.agents:
                    if (a.alt == 'none'):
                        a.alt = alt
                        counter += 1
                    if (counter == math.ceil(N / K)):
                        break
				# store the current test partial assignment
                newPar.append(af_prime)
			# Sort the test partial assignments by their total Borda satisfaction
            newPar.sort(key=bordaTotalSat, reverse=True)
		# Keep only the top 'd' partial assignments for use in the next iteration
        L = min(len(newPar), d)
        Par = newPar[:L]
    return Par

def algoC_M2(comm_size, alts, agents, d):
    # Store the number of voting agents
    num_agents = len(agents)

    # Store Preference objects (agents) in SingleAssignment objects
    assignments = []
    for a in agents:
        assignments.append(SingleAssignment(a))

    # List of partial assignments (i.e. incomplete committees)
    paList = []
    # Initial default partial assignment (none assigned)
    pa0 = FullAssignment(assignments, alts)
    paList.append(pa0)

    # Iteratively build up partial assignments by adding 1 alternative at a time
    for i in range(comm_size):
        tmpList = []
        # Extend every partial assignment to include 1 more alternative, trying every permutation
        for pa in paList:
            for alt in pa.unmatchedAlts:
                extendedPA = copy.deepcopy(pa)
                # Sort the single assignments (agents) by their preference for the current alternative
                sortedAssignments = sorted(extendedPA.assignments, key=lambda a: a.pref.getRankMap()[alt])
                extendedPA.assignments = sortedAssignments
                # Assign the top (num_agents / comm_size) agents to the current alternative unless
                #  they have been previously assigned
                counter = 0
                for a in extendedPA.assignments:
                    if (a.alt == '<none>'):
                        a.alt = alt
                        counter += 1
                    if (counter == math.ceil(num_agents / comm_size)):
                        break

                # The alternative has now been matched
                extendedPA.unmatchedAlts.remove(alt)
                # Save the new extended partial assignment
                tmpList.append(extendedPA)

        # Sort the partial assignments by total satisfaction score
        tmpList = sorted(tmpList, key=lambda pa: pa.getSatScore(), reverse=True)
        # Keep the top L partial assignments for use in the next iteration
        L = min(len(tmpList), d)
        paList = tmpList[:L]

    return paList


def run():
    """
    Main function to run the program.
    """
    check_arguments()

    agents, alternatives = parse_data(sys.argv[1])

    if len(sys.argv) > 2:
        comm_size = int(sys.argv[2])

    else:
        comm_size = len(alternatives)

    # For testing    def __init__(self, wmgMap, count = 1):
        self.wmgMap = wmgMap
        self.count = count

    print
    print("agent.getIncEdgesMap()")
    p
    print("agent.getRankMap()")
    print("agent.getReverseRankMap()")
    print("agent.getOrderVector()")

    matchA = algoA(comm_size, alternatives, agents)

# ============================================================================ #
if __name__ == "__main__":
	run()
