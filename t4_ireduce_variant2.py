#!/usr/bin/env python
from __future__ import division
from operator import mul
import unittest

class _Pad(object):
    """
    Just pad to be able to track default value
    """
    _pad_instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._pad_instance:
            cls._pad_instance = super(_Pad, cls).__new__(cls, *args, **kwargs)
        return cls._pad_instance

def ireduce(function, iterable, initializer=_Pad()):
    """
    Iterator yielding all values (including intermediate),
    with the last value equal to the output of traditional reduce.
    """
    it = iter(iterable)
    if initializer is _Pad():
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
        self.assertRaises(TypeError, ireduce, mul, [1,2,3,4,5], 1, 1)

    def test_should_raise_if_less_then_two_parameters(self):
        self.assertRaises(TypeError, ireduce, mul)
