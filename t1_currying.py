#!/usr/bin/env python
from __future__ import division

import inspect
from functools import wraps
from itertools import chain, izip




class Curried(object):
    def __init__(self,f):
        self.f = f

        self.__name__ = 'curried_{}'.format(f.func_name)
        self.__module__ = f.__module__
        self.__doc__ = f.__doc__

        self.positional_arguments = inspect.getargspec(f).args
        self.positional_arguments_required = inspect.getargspec(f).args
        default_arguments = inspect.getargspec(f).defaults
        if default_arguments is None:
            self.gathered_arguments = {}
            self.expected_arguments = set(self.positional_arguments)
        else:
            args_first, args_second = Curried._list_split_helper(
                self.positional_arguments_required, -len(default_arguments))
            self.gathered_arguments = dict(zip(args_second, default_arguments))
            self.expected_arguments = set(args_first)
        self.extra_positional_arguments = []

    @staticmethod
    def _list_split_helper(alist, *indices):
        """
        Split alist at positions specified by indices and return iterator over resulting lists.
        """
        list_length = len(alist)
        indices = [list_length + index if index < 0 else index for index in indices]
        pairs = izip(chain([0], indices), chain(indices, [None]))
        return (alist[i:j] for i, j in pairs)

    def _update_gathered_and_expected_args_with_dict(self, args_as_dict):
        self.gathered_arguments.update(args_as_dict)
        self.expected_arguments.difference_update(args_as_dict.viewkeys())

    def __call__(self, *args, **kwargs):
        # get only needed part of args
        if len(args) > len(self.positional_arguments_required):
            self.extra_positional_arguments.extend(args[len(self.positional_arguments_required):])
            args = args[:len(self.positional_arguments_required)]

        args_as_dict = dict(zip(self.positional_arguments_required, args))
        self._update_gathered_and_expected_args_with_dict(args_as_dict)
        self.positional_arguments_required = self.positional_arguments_required[len(args_as_dict):]

        self._update_gathered_and_expected_args_with_dict(kwargs)

        if not self.expected_arguments: # We have all obligatory arguments as for now
            positional_dict, keyword_arguments = self._get_output_args_and_kwargs()
            return self.f(*(positional_dict.values() + self.extra_positional_arguments), **keyword_arguments)
        else:
            return self

    def _get_output_args_and_kwargs(self):
        args_dict = dict(((key, value) for (key, value) in self.gathered_arguments.iteritems()
            if key in set(self.positional_arguments)))
        kwargs = dict(((key, value) for (key, value) in self.gathered_arguments.iteritems()
            if key not in set(self.positional_arguments)))
        return args_dict, kwargs

    def __repr__(self):
        arguments_dict, keyword_arguments = self._get_output_args_and_kwargs()
        return 'curry({})({})'.format(self.f.func_name,
            ', '.join(
                '{}={}'.format(key,value)
                for key, value in chain(arguments_dict.iteritems(),keyword_arguments.iteritems())))

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
    def mul(a,b,c,d=4,*args,**kwargs):
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
