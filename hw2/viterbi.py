#!/usr/bin/python

import sys, math
from collections import defaultdict

MODEL = sys.argv[1]

# Viterbi Scores Dictionary
K = {}
# State Table
State = {}
# transition Probability
Q = {}
# Emission Probability
E = {}

State['final'] = 0
State['init'] = 0

f = open(MODEL)
# Model Data
for l in f:
    data = list(l.split())

    if data[0] == 'tri_trans':
        prev = data[1]
        POS = data[2]
        prob = data[3]
        if data[1] not in Q:
            Q[data[1]] = defaultdict(int)
        # Set transition Probability
        Q[prev][POS] = prob
    elif data[0] == 'emit':
        POS = data[1]
        word = data[2]
        prob = data[3]
        if POS not in E:
            E[POS] = defaultdict(int)
            State[POS] = 0
        # Set emission Probability
        E[POS][word] = prob


def viterbi(sentence, n):
    # Returns a Sequence of Tags for the input Sentence
    pi = defaultdict(lambda: float('-inf'))
    # Initialize Start States
    pi[(-1,'init','init')] = pi[(0,'init','init')] = [1] * len(State)
    bp = {}
    y = []
    for k in xrange(1, n):
        for w in K[k-2]:
            for u in K[k-1]:
                for v in K[k]:
                    vprev = math.log(pi[(k-1,w,u)])
                    q = math.log(Q[(w,u)][v])
                    e = math.log(E[v][sentence[k]])
                    # Update Max
                    pi[(k,u,v)] = max(vprev + q + e, pi[(k,u,v)])
        # Generate BP as argmax \
        # Returns a tuple with max value \
        # for the current word column
        # as t = ((k,u,v), max)
        t = max((key,v) for key,v in pi.itemrs if key[0] == k)
        bp[t[0]] = t[0][2]

    for u in K[n-1]:
        for v in K[n]:
            vprev = math.log(pi[(n, u, v)])
            q = math.log(Q[(u,v)]['final'])
            pi[(n, u, v)] = max(vprev + q, pi[(n, u, v)])

    t = max((key, v) for key, v in pi.itemrs if key[0] == n)
    yn = t[0][2]
    yn_1 = t[0][1]
    y.append(yn_1)
    y.append(yn)

# Sentence Input
for line in sys.stdin:
    s = list(line.split())
    K = {}

    for i in xrange(1, len(s)+1):
        K[i] = State

    viterbi(s, len(s))