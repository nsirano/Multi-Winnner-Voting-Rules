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
        print(ranking)
        if len(ranking) > len(alternatives):
            alternatives = sorted(ranking)

        wmgMap = create_wmgMap(ranking)
        agents.append(Preference(wmgMap))

    return agents, alternatives

def borda(alternative, ranking):
    """
    Returns the borda score of an alternative in a given ranking defined as a
    two-dimensional list of alternatives.
    """


    for tier in range(len(ranking)):
        if alternative in ranking[tier]:
            return tier

def algoA(comm_size, alts, agents):
    """
    Algorithm A
    """
    if comm_size <= 2:
        # Betzler
        return

    num_assigned = len(agents)/comm_size
    print(num_assigned, "NUM_ASSIGNED")

    alts_left = alts
    print(alts_left, "ALTS_LEFT")

    current_agents = [a.getOrderVector() for a in agents]
    pp(current_agents)

    print

    phi = list()

    # For each committee member
    for i in range(1, comm_size + 1):
        score = dict()
        bests = dict()

        print(alts_left, "ALTS_LEFT")

        # For each alternative in each rank,
        alt_bests = []
        for alt in alts_left:
            print(alt, "ALT")
            def flat_rank(alt, order_vector):
                '''
                Compresses ranking into 1-dimensional vector and returns the
                index of the alternative in the new vector.
                '''
                yield (a for a in tier for tier in order_vector).index(alt)

            # Sort the agents by ranking of given alt, most preferred first
            print(current_agents, "AGENTS_LEFT")
            agents_left = list(sorted(current_agents,
                                      key=lambda agent:
                                        flat_rank(alt, agent)))

            # Add the first n/K agents to the best fit for the given alternative
            alt_bests = []
            print("len(agents_left) = " + str(len(agents_left)))
            for n in range(int(num_assigned)):
                if agents_left:
                    alt_bests.append(agents_left.pop(0))
                    print(alt_bests[n]), "TEST 1"
            print(len(agents_left))

            pp(alt_bests)
            bests[alt] = list(alt_bests)
            pp(bests)

            # For each alternative relative to each agent,
            score[alt] = 0
            for j in alt_bests:
                # Add the borda score
                #score[alt] += len(alts) - j.index(alt)
                score[alt] += borda(alt, j)

        best_alt = max(score.iteritems(), key=operator.itemgetter(1))[0]
        print(i, best_alt), "TEST 2"
        print(bests[best_alt]), "TEST 3"
        for j in bests[best_alt]:
            print(j, best_alt), "TEST 4"
            if best_alt not in phi:
                phi.append(best_alt)
                
            current_agents.remove(j)

        print(i), "test 5"
        print(alts_left, best_alt), "test 6"
        alts_left.remove(best_alt)

    return phi

def algoC_CC(comm_size, alts, agents, d):
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
                    if (bordaScore(a.pref, alt) > bordaScore(a.pref, a.alt)):
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

def algoC_M(comm_size, alts, agents, d):
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

    # For testing

    print
    print("agent.getIncEdgesMap()")
    pp([a.getIncEdgesMap() for a in agents])
    print
    print("agent.getRankMap()")
    pp([a.getRankMap() for a in agents])
    print
    print("agent.getReverseRankMap()")
    pp([a.getReverseRankMap() for a in agents])
    print
    print("agent.getOrderVector()")
    pp([a.getOrderVector() for a in agents])
    print

    winners = algoA(comm_size, alternatives, agents)
    print(winners)



# ============================================================================ #
if __name__ == "__main__":
	run()
