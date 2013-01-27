#!/usr/bin/env python
from __future__ import division

from functools import reduce
from operator import imul
import inspect


def curry(f, *args, **kwargs):
    """
    Make function curried, so that it will accept this parameters passing.
    @curry
    def f(a,b,c):
        return a+b+c

    f(a,b,c) = f(a,b)(c) = f(a)(b,c) = f(a)(b)(c)
    """
    if len(args) + len(kwargs) >= len(inspect.getargspec(f).args):
        return f(*args, **kwargs)
    else:
        return lambda *largs, **lkwargs: curry(f, *(args + largs), **(kwargs.update(lkwargs) or kwargs))


def tests():

    @curry
    def mul(a,b,c,d):
        """
        Return multiplication of all arguments
        """
        return a*b*c*d

    assert(mul(1,2,3,4) == 24)
    assert(mul(1)(2,3,4) == 24)
    assert(mul(1,2)(3,4) == 24)
    assert(mul(1,2,3)(4) == 24)
    assert(mul(a=1,b=2,c=3)(d=4) == 24)

    @curry
    def mul(a,b,c,d,**kwargs):
        print('This are stashed key-word arguments: {}'.format(kwargs))
        return a*b*c*d

    assert(mul(1,2,3,4, i_am_a_key_word = 'my treasure') == 24)
    assert(mul(1,2)(3,4, i_am_a_key_word = 'my treasure') == 24)
    assert(mul(1,2, i_am_a_key_word = 'my treasure')(3,4) == 24)


    print('Test passed!')

if __name__ == '__main__':
    tests()