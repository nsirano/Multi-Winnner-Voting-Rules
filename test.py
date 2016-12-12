import MultiWinner
import sys

if __name__ == "__main__":
    """
    Test code for main approximation algorithm from MultiWinner.py
    """
    v1 = MultiWinner.Preference(MultiWinner.create_wmgMap(['a','b','c','d']))
    v2 = MultiWinner.Preference(MultiWinner.create_wmgMap(['a','c','b','d']))
    v3 = MultiWinner.Preference(MultiWinner.create_wmgMap(['a','d','c','b']))
    v4 = MultiWinner.Preference(MultiWinner.create_wmgMap(['a','b','d','c']))
    v5 = MultiWinner.Preference(MultiWinner.create_wmgMap(['b','c','a','d']))
    v6 = MultiWinner.Preference(MultiWinner.create_wmgMap(['c','d','b','a']))

    agents = [v1, v2, v3, v4, v5, v6]
    alternatives = ['a','b','c','d']
    comm_size = len(alternatives)

    print(MultiWinner.algoA_M(comm_size, alternatives, agents))
