#!/usr/bin/env python
from __future__ import division

from functools import wraps

def make_decorator_lazy(decorator):
    lazy_decorated = []
    def new_lazy_decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not lazy_decorated:
                lazy_decorated.append(decorator(f))
            return lazy_decorated[0](*args, **kwargs)
        return decorated
    return new_lazy_decorator

def tests():
    # Without decorator
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

    # With decorator
    # First variant of application: lazy decorator is applied to decorator every time decorator is applied.
    # Not very good way of using it as decorator is applied every time the decorator is applied to function
    print('Using lazy decorator\n----')
    @make_decorator_lazy(special_heavy_decorator_for_print_function)
    def print_function():
        print("I (namely 'print_function', no-no, again 'PRINT_FUNCTION') have just printed this kewl piece of text.")
    print('*Now the decorated function is about to be called.')
    print_function()


    print('\n\n')
    print('Decorator here should be applied again')

    @make_decorator_lazy(special_heavy_decorator_for_print_function)
    def print_function():
        print("I (namely 'print_function', no-no, again 'PRINT_FUNCTION') have just printed this kewl piece of text.")
    print('*Now the decorated function is about to be called.')

    print_function()


    # With decorator (second variant of application: decorated decorator; good if you want the decorator to become
    # lazy forever)
    @make_decorator_lazy
    def special_heavy_decorator_for_print_function(f):
        print("Hi! I'm a brand-new print function decorator. I output the huge next message while decorating!")
        print("HUGE MESSAGE")

        @wraps(f)
        def new_decorated_f(*args, **kwargs):
            print('This is output by decorated function before the real function is called.')
            return f(*args, **kwargs)
        return new_decorated_f

    print('\n')

    print('Using lazy decorator\n----')
    @special_heavy_decorator_for_print_function
    def print_function():
        print("I (namely 'print_function', no-no, again 'PRINT_FUNCTION') have just printed this kewl piece of text.")
    print('*Now the decorated function is about to be called.')
    print_function()

    print('\n\n')
    print('Decorator should NOT be applied again')
    @special_heavy_decorator_for_print_function
    def print_function():
        print("I (namely 'print_function', no-no, again 'PRINT_FUNCTION') have just printed this kewl piece of text.")
    print('*Now the decorated function is about to be called.')
    print_function()

if __name__ == '__main__':
    tests()