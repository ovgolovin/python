#!/usr/bin/env python
from __future__ import division
from itertools import islice

def primes():
    """
    Prime numbers generator based on very efficient implementation of Eratosthenes sieve algorithm.

    Solution based on this answer: http://stackoverflow.com/a/10733621/862380
    and this discussion: http://code.activestate.com/recipes/117119/

    This solution uses later addition of stepping information for a prime
    into the dict only when the prime's square is seen among the candidates.
    This results in much smaller dict with performance and empirical time complexity improvement as well.
    """

    yield 2
    yield 3
    D = {}
    c = 5 #3+2 (because we advance by 2 (not 1) as another means of optimization)
    ps = (p for p in primes()) #subiterator (runs the same prime generator to be used to produce squares of its values)
    next(ps) #skip 2 (because we avoid 2 by advancing by 2, not 1 : we use c+=2)
    p = next(ps) #3
    q = p*p #9
    while True:
        if c not in D:
            if c < q:
                yield c
            else: #c==q
                x = add(D,c+2*p,2*p) #we add next after q=p*p multiple of p to D now, remembering that we avoid multiples of 2
                p = next(ps) #the next value of p and q we take from subgenerator.
                q = p*p
        else:
            s = D.pop(c) #just move the existing value in D forward by s=2*p
            x = add(D,c+s,s)
        c += 2; #advance by 2 to a

def add(D,x,s):
    while x in D:
        x += s
    D[x] = s
    return x

def tests():
    assert(list(islice(primes(),0,20)) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71])
    print('Test passed!')

if __name__ == '__main__':
    tests()