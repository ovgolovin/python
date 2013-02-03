#!/usr/bin/env python
from __future__ import division
from operator import mul
import unittest

def ireduce(function, iterable, *initializer):
    """
    Iterator yielding all values (including intermediate),
    with the last value equal to the output of traditional reduce.
    """
    if len(initializer) > 1:
        raise TypeError("You have provided more than 3 arguments.")

    if initializer:
        initializer = initializer[0]
    else:
        initializer = None
    return _ireduce(function, iterable, initializer)

def _ireduce(function, iterable, initializer):
    """
    ireduce helper
    The need to split the generator into function and generator is warranted by the fact that
    if we use only one ireduce generator per se, we would end up having exceptions connected with *initializer
    raised only when next() is called on the resultant iterator, not a moment sooner.
    And with a function the exception will be raised at once, which is much more expected behaviour,
    than a postponed error raise.
    """

    it = iter(iterable)
    if initializer is None:
        try:
            initializer = next(it)
        except StopIteration:
            raise TypeError('ireduce() of empty sequence with no initial value')
    accum_value = initializer
    for x in it:
        accum_value = function(accum_value, x)
        yield accum_value

class Tests(unittest.TestCase):
    def test_trivial(self):
        self.assertEqual(list(ireduce(mul, [1,2,3,4,5], 1)), [1, 2, 6, 24, 120])

    def test_should_raise_if_more_than_four_parameters(self):
        # Error raised at once on calling ireduce
        self.assertRaises(TypeError, ireduce, mul, [1,2,3,4,5], 1, 1)

    def test_should_raise_if_less_then_two_parameters(self):
        self.assertRaises(TypeError, ireduce, mul)
