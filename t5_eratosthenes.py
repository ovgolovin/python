#!/usr/bin/env python
from __future__ import division
from itertools import islice, count, chain, ifilter
import unittest

def efficient_primes():
    """
    Prime numbers generator based on very efficient variant of Sieve of Eratosthenes algorithm.

    Solution based on this answer: http://stackoverflow.com/a/10733621/862380
    and this discussion: http://code.activestate.com/recipes/117119/

    This solution uses postponed prime multiple addition to the dictionary,
    which happens at the moment when the current iterator prime guess encounters the square
    of the prime from subgenerator.
    At first glance it takes a subgenerator to produce the primes which already have been produced,
    but it appears to be much more efficient to generate primes again than to save generated primes
    from the current generator.
    This results in much smaller memory footstep and better time complexity.
    """

    for value in (2,3,5,7):
        yield value
    D = {}  # map each composite integer to its first-found prime factor
            # (the first prime factor that revealed to us that number is a composite is a value in this dict)
    ps = (p for p in efficient_primes()) #subiterator (runs the same prime generator to be used to get squares of its values)
    next(ps)    # we may skip p = 2 as we avoid multiples of 2 in the algorithm, and start from p = 3 which multiples
                # must figure in D
    p = next(ps) # 3
    q = p*p # 9
    for guess in count(9, 2): # 9 = 7 + 2 (because we advance by 2 (not 1) as just another means of optimization)
        s = D.pop(guess, None)
        if s is None: # no value for s in D
            if guess < q:   # this is a prime, since it would be in the D otherwise
                            # (some of its factors would put it here as a multiple of itself    )
                yield guess # We don't save its square to D as we may do it later by getting values from subgenertor
                            # which turns out to be much more efficient
            else: # guess == q, and q is is p*p, so it's not a prime
                add(D, guess, 2 * p)    # we add to D the next multiple of p after p*p now,
                                                # remembering that we avoid multiples of 2
                p = next(ps) #the next value of p and q we take from subgenerator.
                q = p*p
        else:
            add(D, guess, s)

def add(D, x, s):
    while True:
        x += s
        if x not in D:
            break
    D[x] = s
    return x


def expanded_oneliner():
    D = {}
    yield 2
    for guess in count(3, 2):
        if guess not in D:
            D[guess**2] = guess
            yield guess
        else:
            p = D[guess]
            x = guess + 2*p
            while x in D:
                x += 2*p
            D[x] = p


one_liner = lambda: (\
        ifilter(
            None,
            chain(
                [2],
                (
                    D.__setitem__(guess**2, guess) or guess if
                        guess not in D else
                        D.__setitem__(
                            next(x for x in count(guess + 2 * D[guess], 2 * D[guess]) if x not in D),
                            D[guess]
                        )
                        for guess in count(3,2)
                )
            )
        ) for D in ({},)
    ).next()



class Tests(unittest.TestCase):
    def test_efficient_primes(self):
        self.assertEqual(list(islice(efficient_primes(),0,20)),
            [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71])

    def test_one_liner(self):
        self.assertEqual(list(islice(one_liner(),0,20)),
            [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71])
