#!/usr/bin/env python
from __future__ import division

import inspect
from functools import wraps
from itertools import chain



class Curried(object):
    def __init__(self,f):
        self.f = f
        self.__name__ = 'curried_{}'.format(f.func_name)
        self.__module__ = f.__module__
        self.__doc__ = f.__doc__

        arguments = inspect.getargspec(f).args
        defaults = inspect.getargspec(f).defaults
        self.all_arguments = {} if defaults is None else dict(zip(arguments[-len(defaults):], defaults))
        self.expected_args = set(arguments if defaults is None else arguments[:len(arguments)-len(defaults)])
        self.positional_args = arguments
        self.args = []
        pass

    def __call__(self, *args, **kwargs):
        if len(args) > len(self.positional_args):
            self.args.extend(args[len(args) - len(self.positional_args):])
            args = args[:len(args) - len(self.positional_args)]
        arguments_update = dict(zip(self.positional_args, args))
        self.all_arguments.update(arguments_update)
        self.expected_args.difference_update(arguments_update.viewkeys())
        self.positional_args = self.positional_args[len(arguments_update):]

        self.all_arguments.update(kwargs)
        self.expected_args.difference_update(kwargs.viewkeys())

        if not self.expected_args:
            arguments = inspect.getargspec(self.f).args
            positional_values = [self.all_arguments[arg] for arg in arguments]
            keyword_arguments = dict(((key,value) for (key,value) in self.all_arguments.iteritems() if key not in set(arguments)))
            return self.f(*(positional_values + self.args), **keyword_arguments)
        else:
            return self

    def __repr__(self):
        arguments = inspect.getargspec(self.f).args
        arguments_dict = dict(((key,value) for (key,value) in self.all_arguments.iteritems() if key in set(arguments)))
        keyword_arguments = dict(((key,value) for (key,value) in self.all_arguments.iteritems() if key not in set(arguments)))
        return 'curry({})({})'.format(self.f.func_name,
            ', '.join('{}={}'.format(key,value) for key, value in chain(arguments_dict.iteritems(),keyword_arguments.iteritems())))

def curry(f):
    """
    Make function curried, so that it will accept this parameters passing.
    @curry
    def f(a,b,c):
        return a+b+c

    f(a,b,c) = f(a,b)(c) = f(a)(b,c) = f(a)(b)(c)
    """
    @wraps(f)
    def helper(*args,**kwargs):
        return Curried(f)(*args,**kwargs) #first invocation of curried function must return a new Curried object
    helper.__name__ = 'curried_{}'.format(f.func_name)
    return helper


def tests():

    @curry
    def mul(a,b,c,d=4):
        """
        Return multiplication of all arguments
        """
        return a*b*c*d

    assert(mul(1,2,3,4)==24)
    assert(mul(1)(2,3,4)==24)
    assert(mul(1,2)(3,4) == 24)
    assert(mul(1,2,3) == 24)
    assert(mul(a=1,b=2,c=3) == 24)
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
