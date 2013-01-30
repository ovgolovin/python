#!/usr/bin/env python
from __future__ import division

from functools import wraps
import unittest

def make_decorator_lazy(decorator):
    @wraps(decorator)
    def new_lazy_decorator(f):
        lazy_decorated = []
        @wraps(f)
        def decorated(*args, **kwargs):
            if not lazy_decorated:
                lazy_decorated.append(decorator(f))
            return lazy_decorated[0](*args, **kwargs)
        return decorated
    return new_lazy_decorator


def tests():
    def decorator(f):
        print("Running decoration")
        @wraps(f)
        def new_decorated_f(*args, **kwargs):
            print('Calling f')
            return f(*args, **kwargs)
        return new_decorated_f

    def f():
        print("f is running")

    # Without lazy decorator
    print('Without lazy decorator\n----')
    decorated = decorator(f)
    print('About to call decorated f')
    decorated()
    print('\n')

    # With lazy decorator.
    print('With lazy decorator\n----')
    decorator_made_lazy = make_decorator_lazy(decorator)
    decorated = decorator_made_lazy(f)
    print('About to call decorated f')
    decorated()
    print("About to call decorated f (decoration shouldn't be applied again)")
    decorated()


if __name__ == '__main__':
    tests()