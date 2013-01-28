#!/usr/bin/env python
from __future__ import division

import inspect
from functools import wraps


class Curried(object):
    """
    Make function curried, so that it will accept this parameters passing.
    @curry
    def f(a,b,c):
        return a+b+c

    f(a,b,c) = f(a,b)(c) = f(a)(b,c) = f(a)(b)(c)
    """

    def __init__(self,f):
        self.f = f

        arguments = inspect.getargspec(f).args
        defaults = inspect.getargspec(f).defaults
        self.arguments = {} if defaults is None else dict(zip(arguments[-len(defaults):], defaults))
        self.expected_args = arguments if defaults is None else arguments[len(arguments)-len(defaults):]

    def __call__(self, *args, **kwargs):
        if len(args) > len(self.expected_args):
            raise(TypeError('You have provided more positional arguments than needed.'))
        arguments_update = zip(self.expected_args, args)
        self.arguments.update(arguments_update)
        self.expected_args = self.expected_args[len(arguments_update):]

        self.arguments.update(kwargs)
        self.expected_args = [arg for arg in self.expected_args if arg not in kwargs]

        if not self.expected_args:
            return self.f(**self.arguments)
        else:
            return self

    def __repr__(self):
        return '\n'.join((
        'You have provided arguments: {}'.format(self.arguments),
        'You have left to provide: {}'.format(self.expected_args)
        ))

def curry(f):
    @wraps(f)
    def helper(*args,**kwargs):
        return Curried(f)(*args,**kwargs)
    return helper


def tests():

    @curry
    def mul(a,b,c,d):
        """
        Return multiplication of all arguments
        """
        return a*b*c*d

    assert(mul(1,2,3,4)==24)
    assert(mul(1)(2,3,4)==24)
    assert(mul(1,2)(3,4) == 24)
    assert(mul(1,2,3)(4) == 24)
    assert(mul(a=1,b=2,c=3)(d=4) == 24)
    assert(mul(1,b=2,c=3,d=4) == 24)

    @curry
    def mul(a,b,c,d,**kwargs):
        return a*b*c*d

    assert(mul(1,2,3,4, i_am_a_key_word = 'my treasure') == 24)
    assert(mul(1,2)(3,4, i_am_a_key_word = 'my treasure') == 24)
    assert(mul(1,2, i_am_a_key_word = 'my treasure')(3,4) == 24)
    assert(mul(1,2, i_am_a_key_word = 'my treasure')(c=3,d=4) == 24)


    print('Test passed!')

if __name__ == '__main__':
    tests()