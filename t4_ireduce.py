#!/usr/bin/env python
from __future__ import division
from operator import mul

def ireduce(function, iterable, initializer=None):
    it = iter(iterable)
    if initializer is None:
        try:
            initializer = next(it)
        except StopIteration:
            raise TypeError('reduce() of empty sequence with no initial value')
    accum_value = initializer
    for x in it:
        accum_value = function(accum_value, x)
        yield accum_value


def tests():
    assert(list(ireduce(mul, [1,2,3,4,5], 1)) == [1, 2, 6, 24, 120])
    print('Test passed!')

if __name__ == '__main__':
    tests()