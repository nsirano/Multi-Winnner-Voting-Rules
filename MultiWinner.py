import copy
import operator
import math


class VoterAgent:
	def __init__(self, idString="<unnamed>", prefAltList=[]):
		self.id = id
		self.prefs = prefAltList

	def getID(self):
		return self.id

	def setID(self, idString):
		self.id = idString

	def getPrefs(self):
		return self.prefs

	def setPrefs(self, prefAltList):
		self.prefs = prefAltList

class CandidateAlternative:
	def __init__(self, idString="<unnamed>"):
		self.id = idString

	def getID(self):
		return self.id

	def setID(self, idString):
		self.id = idString

class Assignment:
	def __init__(self, candidateAlternative, voterAgentList=[]):
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
		a = self.getAlternativeAssignment()
		if (a != None):
			return a.getAgents()
		else:
			return None

	def getAssignedAlternative(self, voterAgentIDString):
		a = self.getAgentAssignment()
		if (a != None):
			return a.getAlt()
		else:
			return None
'''
class AssignmentFunction:
	def __init__(self, candidateAlternativeList=[], voterAgentList=[]):
		self.alts = candidateAlternativeList
		self.agents = voterAgentList


	#ADD VOTING ALGORITHMS HERE

'''

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
    '''
    Calculates the n-th number of the Harmonic Series.
    '''
    assert n >= 1, "Invalid number (%d) to calculate Harmonic Series."%n
    return sum((1.0/k) for k in range(1,n+1))

def algo_A(comm_size, num_candidates):
    '''
    - Let K = comm_size
    - Let m = num_candidates
    - Let H_K be the K-th harmonic number.
    - Each agent is, on average, represented by someone whom they prefer to
      at least (1 - ((K-1)/(2*(m-1))) - (H_K/K)) fraction of the candidates.
      where H_K is the K-th harmonic number.
    - Each member of the committee represents roughly the same number of agents.
    - Holds for every possible profile of (complete) preference orders.
    - Approximates the Monroe rule.
    '''
    return 1 - ((comm_size)/(2*(num_candidates-1))) - (harmonic(comm_size)/comm_size)

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


def algoC_CC(K, alts, agents, d):
	'''
	Chamberlin Courant Multi-Winner Approximation Algorithm C
		Algorithm C is a further heuristic improvement over Algorithm B. This time the idea is that instead of keeping only
	one partial function Φ that is iteratively extended up to the full assignment, we keep a list of up to d partial assignment
	functions, where d is a parameter of the algorithm. At each iteration, for each assignment function Φ among the d stored
	ones and for each alternative a to which Φ has not assigned agents yet, we compute an optimal extension of this Φ that
	assigns agents to a. As a result we obtain possibly more than d (partial) assignment functions. For the next iteration we
	keep those d that give highest satisfaction.
	'''
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
	'''
	Monroe Multi-Winner Approximation Algorithm C
		Algorithm C is a further heuristic improvement over Algorithm B. This time the idea is that instead of keeping only
	one partial function Φ that is iteratively extended up to the full assignment, we keep a list of up to d partial assignment
	functions, where d is a parameter of the algorithm. At each iteration, for each assignment function Φ among the d stored
	ones and for each alternative a to which Φ has not assigned agents yet, we compute an optimal extension of this Φ that
	assigns agents to a. As a result we obtain possibly more than d (partial) assignment functions. For the next iteration we
	keep those d that give highest satisfaction.
	'''
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

a1 = Agent('1', ['a', 'b', 'c', 'd'])
a2 = Agent('2', ['b', 'a', 'c', 'd'])
a3 = Agent('3', ['b', 'c', 'a', 'd'])
a4 = Agent('4', ['a', 'd', 'c', 'b'])
a5 = Agent('5', ['a', 'b', 'c', 'd'])
a6 = Agent('6', ['c', 'b', 'a', 'd'])

af0 = AssignmentFunction([a1,a2,a3,a4,a5])
#print(len(af0.agents))
#print(len(af0.unmatchedAlts))
#print(bordaTotalSat(af0))

parCC = algoC_CC(2, ['a', 'b', 'c', 'd'], [a1, a2, a3, a4, a5], 10)
#print(len(parCC))

parM = algoC_M(3, 6, ['a', 'b', 'c', 'd'], [a1, a2, a3, a4, a5, a6], 4)
#print(len(parM))

par = parM
for i in range(len(par)):
    for agent in par[i].agents:
        print(agent.name, ':', agent.alt)
    print(par[i].unmatchedAlts)
    print(bordaTotalSat(par[i]))
    print('-------------')
