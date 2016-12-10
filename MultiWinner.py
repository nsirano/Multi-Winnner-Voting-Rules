import copy
import math
import operator
import sys

import pprint
pp = pprint.PrettyPrinter(indent=4).pprint

##############################################################################
'''This is just what I am using so far for a class storage objects.
	Pretty much a copy of Voter and AssignmentFunction Classes
 (Parker 12/10)'''
class SingleAssignment:
    def __init__(self, prefObj, altID='<none>'):
        self.pref = prefObj
        self.alt = altID

class FullAssignment:
     def __init__(self, assignmentObjList=[], unmatchedAltList=[]):
        self.assignments = assignmentObjList
        self.unmatchedAlts = unmatchedAltList

#############################################################################
''' All classes below will become obsolete. Parker 12/10 '''
class VoterAgent:
    def __init__(self, idString="<unnamed>", prefAltList=[]):
        self.id = idString
        self.prefs = prefAltList

    def getID(self):
        return self.id

    def setID(self, idString):
        self.id = idString

    def getPrefs(self):
        return self.prefs

    def setPrefs(self, prefAltList):
        self.prefs = prefAltList

    def getSat(self, satRule="Borda", candidateAlternativeIDString="<unnamed>"):
        if (satRule == "Borda"):
            n = len(self.prefs)
            for i in range(n):
                if (candidateAlternativeIDString == self.prefs[i]):
                # Note: This borda method leaves the last ranked candidate with a score of 1
                #  this way, unmentioned candidates on truncated ballots have score of 0.
                    return (n - i)
            return 0

        else:
            return None

class CandidateAlternative:
    def __init__(self, idString="<unnamed>"):
        self.id = idString

    def getID(self):
        return self.id

    def setID(self, idString):
        self.id = idString

class Assignment:
    def __init__(self, candidateAlternative=None, voterAgentList=[]):
        self.alt = candidateAlternative
        self.agents = voterAgentList

    def getAlt(self):
        return self.alt

    def setAlt(self, candidateAlternative):
        self.alt = candidateAlternative

    def getAgents(self):
        return self.agents

    def setAgents(self, voterAgentList):
        self.agents = voterAgentList

class AssignmentMap:
    def __init__(self, assignmentList=[]):
        self.assignments = assignmentList

    def getAssignments(self):
        return self.assignments

    def getAlternativeAssignment(self, candidateAlternativeIDString):
        for a in self.assignments:
            if (a.getAlt().getID() == candidateAlternativeIDString):
                return a
        return None

    def getAgentAssignment(self, voterAgentIDString):
        for a in self.assignments:
            for v in a.getAgents():
                if (v.getID() == voterAgentIDString):
                    return a
        return None

    def getAssignedAgents(self, candidateAlternativeIDString):
        a = self.getAlternativeAssignment(candidateAlternativeIDString)
        if (a != None):
            return a.getAgents()
        else:
            return None

    def getAssignedAlternative(self, voterAgentIDString):
        a = self.getAgentAssignment(voterAgentIDString)
        if (a != None):
            return a.getAlt()
        else:
            return None

    def getTotalSat(self, satRule="Borda"):
        if (satRule == "Borda"):
            totalSat = 0
            for a in self.assignments:
                for v in a.getAgents():
                    totalSat += v.getSat("Borda", a.getAlt().getID())
            return totalSat
        else:
            return -1

class AssignmentFunction:
    def __init__(self, candidateAlternativeList=[], voterAgentList=[]):
        self.alts = candidateAlternativeList
        self.agents = voterAgentList

    #def getSortedAgentsByPref():
        # should this sort the original agent list or create a new one??
        #  create a copy and sort that; maintain integrity of original
        agents = copy.deepcopy(self.agents)


    #ADD VOTING ALGORITHMS HERE

#####################################################################################

# VoterAgent Class Testing
"""
v1 = VoterAgent()
print(v1.getID())
print(v1.getPrefs())

v1.setID("Paul")
print(v1.getID())

v1.setPrefs(['c1', 'c2', 'c3'])
print(v1.getPrefs())
print(v1.getSat('Borda', 'c1'))
print(v1.getSat('Borda', 'c3'))
print(v1.getSat('Borda', 'c4'))

# Candidate Class Testing

c1 = CandidateAlternative()
print(c1.getID())

c1.setID("Bob")
print(c1.getID())

# Assignment Class Testing

a1 = Assignment()
print(a1.getAlt())
print(a1.getAgents())

c1 = CandidateAlternative("Wally Dingmann")
a1.setAlt(c1)
print(a1.getAlt().getID())

v1 = VoterAgent("v1", ['c1','c2','c3'])
v2 = VoterAgent("v2", ['c1','c2','c3'])
v3 = VoterAgent("v3", ['c1','c2','c3'])
av1 = [v1,v2,v3]

a1.setAgents(av1)
for v in a1.getAgents():
    print(v.getID(), ' ', v.getPrefs())

	# AssignmentMap Class Testing

am1 = AssignmentMap()
print(am1.getAssignments())

c1 = CandidateAlternative("c1")
c2 = CandidateAlternative("c2")
c3 = CandidateAlternative("c3")

v1 = VoterAgent("v1", ['c1','c2','c3'])
v2 = VoterAgent("v2", ['c1','c2','c3'])
v3 = VoterAgent("v3", ['c2','c3','c1'])
v4 = VoterAgent("v4", ['c2','c3','c1'])
v5 = VoterAgent("v5", ['c3','c1','c2'])
v6 = VoterAgent("v6", ['c3','c1','c2'])

a1 = Assignment(c1, [v1,v2])
a2 = Assignment(c2, [v3,v4])
a3 = Assignment(c3, [v5,v6])

am1 = AssignmentMap([a1,a2,a3])
print(len(am1.getAssignments()))
print(am1.getAlternativeAssignment('c1').getAlt().getID())
print(am1.getAgentAssignment('v3').getAlt().getID())
print(len(am1.getAssignedAgents('c3')))
print(am1.getAssignedAlternative('v6').getID())
print("Total Satisfaction: ", am1.getTotalSat("Borda"))
"""
#########################################################################################################

class Agent:
    def __init__(self, nameString='<unnamed>', prefList=[], altNameString='none'):
        self.name = nameString
        self.prefs = prefList
        self.alt = altNameString

    def addPrefs(self, prefList):
        self.prefs = prefList

    def addAlt(self, altNameString):
        self.alt = altNameString

class AssignmentFunction:
    def __init__(self, agentList=[], unmatchedAltList=[]):
        self.agents = agentList
        self.unmatchedAlts = unmatchedAltList

    # this might be unnecessary
    def deepCopy(self):
        copyAgentList = copy.deepCopy(self.agents)
        copyUnmatchedAltList = copy.deepCopy(self.unmatchedAlts)
        copyAssignmentFunction = AssignmentFunction(copyAgentList, copyUnmatchedAltList)
        return copyAssignmentFunction

def harmonic(n):
    """
    Calculates the n-th number of the Harmonic Series.
    """
    assert n >= 1, "Invalid number (%d) to calculate Harmonic Series."%n
    return sum((1.0/k) for k in range(1,n+1))

# working+
def bordaSat(agentPrefList, altNameString):
    try:
        rank = agentPrefList.index(altNameString)
        sat = len(agentPrefList) - (rank)  # using rank instead of (rank + 1) to allow for truncated ballots
        return sat
    except ValueError:
        return 0

# working+
# Given a mapping, calculate the total societal satisfaction
def bordaTotalSat(assignmentFunction):
    """
    Given a mapping, calculate the total societal satisfaction.
    """
    totalSum = 0
    for agent in assignmentFunction.agents:
        totalSum += bordaSat(agent.prefs, agent.alt)
    return totalSum

# This works, but is pretty inefficient, try to find a better way when you have more time
def agentSort(agents, alt):
    prefDict = {}
    for a in agents:
        prefDict[a] = bordaSat(a.prefs, alt)
    sortedAgentTuples = sorted(prefDict.items(), key=operator.itemgetter(1), reverse=True)
    sortedAgents = []
    for a in sortedAgentTuples:
        sortedAgents.append(a[0])
    return sortedAgents

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

    phi = dict()

    alts_left = alts
    agents_left = agents

    # For each committee member
    for i in range(1, comm_size + 1):
        score = dict()
        bests = dict()

        # For each alternative
        alt_bests = []
        for alt in alts_left:
            # sort the agents by ranking of given alt, most preferred first
            agents_left = sorted(agents_left, key=lambda agent: agent.prefs.index(alt))

            #for a in agents_left: print(a.name, a.prefs)
            #print
            # add the first n/K agents to the best fit for the given alternative

            alt_bests = []
            for n in range(int(num_assigned)):
                if agents_left:
                    alt_bests.append(agents_left.pop(0))
                    print(alt_bests[n].name)

            bests[alt] = alt_bests

            # add the borda score for each alternative relative to each agent
            score[alt] = 0
            for j in alt_bests:
                score[alt] += len(alts) - j.prefs.index(alt)

        alt_best = max(score.iteritems(), key=operator.itemgetter(1))[0]
        print(i, alt_best)
        print(bests[alt_best])
        for j in bests[alt_best]:
            print(j.name, alt_best)
            phi[j.name] = alt_best

        print(i)
        print(alts_left, alt_best)
        alts_left.remove(alt_best)

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

def parse_data(filename, agents=[], alternatives=[]):
    """
    Parses voter data from input file.
    """
    count = 1
    f = open(sys.argv[1], "r")
    for line in f:
        line = line.rstrip().split(',')
        if count == 1:
            alternatives = sorted(line)

        agents.append(Agent("Agent %d"%(count), line))
        count += 1

    return agents, alternatives

def run():
    """
    Main function to run the program.
    """
    agents = []
    alternatives = []

    # Reads voter data from file
    if len(sys.argv) > 1:
        agents, alternatives = parse_data(sys.argv[1], agents, alternatives)
        print([a.name for a in agents])
        print(alternatives)

    # else runs with the following test data
    else:
        a1 = Agent('Agent 1', ['a', 'b', 'c', 'd'])
        a2 = Agent('Agent 2', ['a', 'c', 'b', 'd'])
        a3 = Agent('Agent 3', ['a', 'd', 'c', 'b'])
        a4 = Agent('Agent 4', ['a', 'b', 'd', 'c'])
        a5 = Agent('Agent 5', ['b', 'c', 'a', 'd'])
        a6 = Agent('Agent 6', ['c', 'd', 'b', 'a'])

        alternatives = ['a', 'b', 'c', 'd']

    af0 = AssignmentFunction(agents)
    #print(len(af0.agents))
    #print(len(af0.unmatchedAlts))
    #print(bordaTotalSat(af0))

    parA = algoA(10, alternatives, agents)
    pp(parA)

    #parCC = algoC_CC(2, ['a', 'b', 'c', 'd'], [a1, a2, a3, a4, a5], 10)
    #print(len(parCC))

    #parM = algoC_M(3, 6, ['a', 'b', 'c', 'd'], [a1, a2, a3, a4, a5, a6], 4)
    #print(len(parM))

    #par = parM
    #for i in range(len(par)):
        #for agent in par[i].agents:
            #print(agent.name, ':', agent.alt)
        #print(par[i].unmatchedAlts)
        #print(bordaTotalSat(par[i]))
        #print('-------------')

# ============================================================================ #
if __name__ == "__main__":
	run()
