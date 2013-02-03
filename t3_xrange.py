#!/usr/bin/env python
from __future__ import division
import unittest


class irange(object):
    """
    Pure Python implementation of xrange.
    Implements slicing and iteration.
    """

    def __init__(self, *args):
        if len(args) > 3:
            raise(TypeError("irange expects at most 3 arguments"))
        if len(args) < 1:
            raise(TypeError("irange expects at least 1 argument"))
        for arg in args:
            if not isinstance(arg, int):
                raise(ValueError("irange accept only arguments of int type. You gave '{arg}'".format(arg=arg)))

        if len(args) == 1:
            self._start, self._stop, self._step = 0, args[0], 1
        elif len(args) == 2:
            (self._start, self._stop), self._step = args, 1
        else:
            self._start, self._stop, self._step = args

        if self._step == 0:
            raise ValueError("Step cannot be equal to 0.")


    def __hash__(self):
        return hash(self._slice)


    def __repr__(self):
        return 'irange({self._start}, {self._stop}, {self._step})'.format(self=self)


    def __len__(self):
        if (self._stop - self._start) * (self._step / abs(self._step)) <= 0:
            return 0
        else:
            return 1 + (abs(self._stop - self._start) - 1) // abs(self._step)


    def __getitem__(self, index):
        # this also makes the object support iteration protocol
        # see http://docs.python.org/2/library/functions.html#iter

        if isinstance(index, slice):
            start, stop, step = index.indices(len(self))
            # slice(...).index(len) produces slice which is equivalent to len elements of intial slice
            return irange(self._get_index_of_ith_element(start), self._get_index_of_ith_element(stop), step*self._step)

        if isinstance(index, (int, long)):
            index =  index + len(self) if index < 0 else index

            if not 0 <= index < len(self):
                raise IndexError('Index {index} out of {self}'.format(index=index, self=self))

            return self._get_index_of_ith_element(index)
        else:
            raise TypeError('irange indices must be slices or integers')

    def _get_index_of_ith_element(self, i):
        return self._start + self._step * i


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

    def test_empty_sequence_with_step(self):
        self.assertEqual(list(irange(10,2,2)), [])

    def test_raises_typeerror_on_more_than_three_arguments(self):
        self.assertRaises(TypeError, irange, 10,2,2,1)

    def test_raises_valueerror_on_arguments_other_than_int(self):
        self.assertRaises(ValueError, irange, 10.2)
        self.assertRaises(ValueError, irange, 2, 10.1)
        self.assertRaises(ValueError, irange, 2, 10, 1.1)

    def test_raises_valueerror_on_zero_step(self):
        self.assertRaises(ValueError, irange, 2, 10, 0)


if __name__ == "__main__":
    unittest.main()