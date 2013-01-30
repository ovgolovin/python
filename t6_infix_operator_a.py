#!/usr/bin/env python
from __future__ import division

import itertools
from operator import mul
import unittest

class PartiallyAppliedInfix(object):
    def __init__(self, f, left_argument):
        self.f = f
        self.left_argument = left_argument

    def __or__(self, right_argument):
        return self.f(self.left_argument, right_argument)


class Infix(object):
    def __init__(self, f):
        self.f = f

    def __ror__(self, left_argument):
        return PartiallyAppliedInfix(self.f, left_argument)


def make_infix(f):
    return Infix(f)



class Tests(unittest.TestCase):
    def setUp(self):
        def dot_product(x, y): return sum(itertools.starmap(mul, itertools.izip(x, y)))
        self.dot_product = dot_product
        self.dot = make_infix(self.dot_product)

        def cross_product(x,y): return list(itertools.starmap(mul, itertools.izip(x, y)))
        self.cross_product = cross_product
        self.cross = make_infix(self.cross_product)

    def test_double(self):
        A = [1, 2, 3, 4, 5]
        B = [1, 2, 3, 4, 5]
        self.assertEqual(A |self.dot| B, self.dot_product(A,B))

    def test_tripple(self):
        A = [1, 2, 3, 4, 5]
        B = [1, 2, 3, 4, 5]
        C = [7, 8, 9, 10, 11]
        self.assertEqual(A |self.cross| B |self.cross| C, self.cross_product(self.cross_product(A,B),C))




