import copy
import math
import operator
import sys

from preference import Preference

import pprint
pp = pprint.PrettyPrinter(indent=4).pprint

class SingleAssignment:
    def __init__(self, prefObj, altID='<none>'):
        self.pref = prefObj
        self.alt = altID

class FullAssignment:
     def __init__(self, assignmentObjList=[], unmatchedAltList=[]):
        self.assignments = assignmentObjList
        self.unmatchedAlts = unmatchedAltList

def usage():
    """
    Prints usage information.
    """
    print("python MultiWinner.py <data.txt>")

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

    return agents, alternatives

def betzler1():
    pass

def algoA(comm_size, alts, agents):
    """
    Algorithm A
    """
    if comm_size <= 2:
        return

    num_assigned = len(agents)/comm_size
    print(num_assigned, "num_assigned")

    alts_left = list(alts)
    agents_left = list(agents)

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
                                                        agent.prefs.index(alt)))

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

def run():
    """
    Main function to run the program.
    """
    check_arguments()

    agents, alternatives = parse_data(sys.argv[1])

# ============================================================================ #
if __name__ == "__main__":
	run()
