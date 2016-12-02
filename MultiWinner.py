import copy
import operator
import math

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
    - Each agent is, on average, represented by someone whom they prefer to
      at least (1 - ((K-1)/(2*(m-1))) - (H_K/K)) fraction of the candidates,
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
    Par = []
    af0 = AssignmentFunction(agents, alts)
    Par.append(af0)
    for i in range(K):
        newPar = []
        for af in Par:
            for alt in af.unmatchedAlts:
                af_prime = copy.deepcopy(af) # this should be a deep copy
                af_prime.unmatchedAlts.remove(alt)
                for agent in af_prime.agents:
                    if (bordaSat(agent.prefs, alt) > bordaSat(agent.prefs, agent.alt)):
                        agent.alt = alt
                newPar.append(af_prime)
            newPar.sort(key=bordaTotalSat, reverse=True)
        L = min(len(newPar), d)
        Par = newPar[:L]

    return Par

def algoC_M(K, N, alts, agents, d):
    Par = []
    af0 = AssignmentFunction(agents, alts)
    Par.append(af0)
    for i in range(K):
        newPar = []
        for af in Par:
            for alt in af.unmatchedAlts:
                af_prime = copy.deepcopy(af) # this should be a deep copy
                af_prime.unmatchedAlts.remove(alt)

                sortedAgentsByPref = agentSort(af_prime.agents, alt)
                #print('sortedAgentsByPref=', len(sortedAgentsByPref))
                af_prime.agents = sortedAgentsByPref

                counter = 0
                for a in af_prime.agents:
                    if (a.alt == 'none'):
                        a.alt = alt
                        counter += 1
                    if (counter == math.ceil(N / K)):
                        break

                newPar.append(af_prime)

            newPar.sort(key=bordaTotalSat, reverse=True)
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
