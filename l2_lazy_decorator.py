#!/usr/bin/env python
from __future__ import division

from functools import wraps

def make_decorator_lazy(decorator):
    def apply_decorator(f):
        return lambda *args, **kwargs: decorator(f)(*args, **kwargs)
    return apply_decorator

def tests():
    def special_heavy_decorator_for_print_function(f):
        print("Hi! I'm a brand-new print function decorator. I output the huge next message while decorating!")
        print("HUGE MESSAGE")

        @wraps(f)
        def new_decorated_f(*args, **kwargs):
            print('This is output by decorated function before the real function is called.')
            return f(*args, **kwargs)
        return new_decorated_f

    print('\n')

    print('Without lazy decorator\n----')
    @special_heavy_decorator_for_print_function
    def print_function():
        print("I (namely 'print_function', no-no, again 'PRINT_FUNCTION') have just printed this kewl piece of text.")
    print('*Now the decorated function is about to be called.')
    print_function()

    print('\n')

    print('Using lazy decorator\n----')
    @make_decorator_lazy(special_heavy_decorator_for_print_function)
    def print_function():
        print("I (namely 'print_function', no-no, again 'PRINT_FUNCTION') have just printed this kewl piece of text.")
    print('*Now the decorated function is about to be called.')
    print_function()

if __name__ == '__main__':
    tests()