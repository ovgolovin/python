#!/usr/bin/env python
from __future__ import division
import unittest


class irange(object):
    """
    Pure Python implementation of xrange.
    Implements slicing and iteration.
    """

    def __init__(self, *args):
        self._slice = slice(*args)
        if self._slice.stop is None:
            # slice(*args) will never put None in stop unless it was
            # given as None explicitly.
            raise TypeError("irange stop must not be None")

    @property
    def start(self):
        if self._slice.start is not None:
            return self._slice.start
        return 0

    @property
    def stop(self):
        return self._slice.stop

    @property
    def step(self):
        if self._slice.step is not None:
            return self._slice.step
        return 1

    def __hash__(self):
        return hash(self._slice)

    def __cmp__(self, other):
        return (cmp(type(self), type(other)) or
                cmp(self._slice, other._slice))

    def __repr__(self):
        return '{!s}({!r}, {!r}, {!r})'.format(self.__class__.__name__,
                                   self.start, self.stop, self.step)

    def __len__(self):
        if (self.stop - self.start) * (self.step / abs(self.step)) <= 0:
            return 0
        else:
            return 1 + (abs(self.stop - self.start) - 1) // abs(self.step)

    def __getitem__(self, index):
        # this also makes the object support iteration protocol
        if isinstance(index, slice):
            start, stop, step = index.indices(len(self))
            return irange(self._index(start),
                self._index(stop), step*self.step)
        elif isinstance(index, (int, long)):
            if index < 0:
                fixed_index = index + len(self)
            else:
                fixed_index = index

            if not 0 <= fixed_index < len(self):
                raise IndexError('Index {:d} out of {!r}'.format(index, self))

            return self._index(fixed_index)
        else:
            raise TypeError('irange indices must be slices or integers')

    def _index(self, i):
        return self.start + self.step * i


class Tests(unittest.TestCase):

    def test_one_argument(self):
        self.assertEqual(list(irange(10)), list(xrange(10)))

    def test_two_arguments(self):
        self.assertEqual(list(irange(2,10)), list(xrange(2,10)))

    def test_three_arguments(self):
        self.assertEqual(list(irange(2,10,2)), list(xrange(2,10,2)))

    def test_negative_step(self):
        self.assertEqual(list(irange(10,2,-2)), list(xrange(10,2,-2)))

    def test_slicing(self):
        self.assertEqual(list(irange(2,10)[0:5]), [2, 3, 4, 5, 6])
        self.assertEqual(list(irange(2,10)[0:100]), [2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(list(irange(2,10)[-100:2]), [2, 3])

    def test_cycle_slicing(self):
        self.assertEqual(list(irange(2,10)[2:-2]), [4, 5, 6, 7])

    def test_negative_step_with_ascending_definition_should_produce_empty_sequence(self):
        self.assertEqual(list(irange(2,10,-2)), [])

    def test_should_raise_IndexError(self):
        self.assertRaises(IndexError, lambda x: irange(2,10)[x], (100))
        self.assertRaises(IndexError, lambda x: irange(2,10)[x], (-100))

    def test_shouldnt_raise_IndexError_for_valid_negative_numbers(self):
        self.assertEqual(irange(2,10)[-2], 8)

    def test_huge_step(self):
        self.assertEqual(list(irange(2,10,100)), [2])




