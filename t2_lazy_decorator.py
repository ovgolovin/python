#!/usr/bin/env python
from __future__ import division

from functools import wraps
import unittest

def make_decorator_lazy(decorator, apply_on_each_call = False):
    """
    Make decorator lazy, so that it would be applied right before first run of decorated function.
    """
    @wraps(decorator)
    def new_lazy_decorator(f):
        lazy_decorated = []
        @wraps(f)
        def decorated(*args, **kwargs):
            if apply_on_each_call:
                return decorator(f)(*args, **kwargs)
            else:
                if not lazy_decorated:
                    lazy_decorated.append(decorator(f))
                return lazy_decorated[0](*args, **kwargs)
        return decorated
    return new_lazy_decorator


def make_decorator_returning_function_returning_lazy_decorator(decorator_factory, apply_on_each_call = False):
    """
    Make function returning decorators return lazy decorators,
    so that each of them would be applied right before first run of decorated function.
    """
    @wraps(decorator_factory)
    def new_factory(*fargs, **fkwargs):
        def new_lazy_decorator(f):
            lazy_decorated = []
            @wraps(f)
            def decorated(*args, **kwargs):
                if apply_on_each_call:
                    return decorator_factory(*fargs, **fkwargs)(f)(*args, **kwargs)
                else:
                    if not lazy_decorated:
                        lazy_decorated.append(decorator_factory(*fargs, **fkwargs)(f))
                    return lazy_decorated[0](*args, **kwargs)
            return decorated
        return new_lazy_decorator
    return new_factory



class Tests_decorator(unittest.TestCase):
    def setUp(self):
        def decorator(f):
            self.cumulative += 1
            @wraps(f)
            def new_decorated_f(*args, **kwargs):
                return f(*args, **kwargs)
            return new_decorated_f
        self.decorator = decorator

        def f():
            pass
        self.f = f


    def test_without_lazy_decorator(self):
        self.cumulative = 0

        decorated = self.decorator(self.f)
        self.assertEqual(self.cumulative, 1)

        decorated()
        self.assertEqual(self.cumulative, 1)


    def test_with_lazy_decorator(self):
        self.cumulative = 0

        decorator_made_lazy = make_decorator_lazy(self.decorator)
        self.assertEqual(self.cumulative, 0)

        decorated = decorator_made_lazy(self.f)
        self.assertEqual(self.cumulative, 0)

        decorated()
        self.assertEqual(self.cumulative, 1)


    def test_with_lazy_decorator_two_calls(self):
        self.cumulative = 0

        decorator_made_lazy = make_decorator_lazy(self.decorator)
        self.assertEqual(self.cumulative, 0)

        decorated = decorator_made_lazy(self.f)
        self.assertEqual(self.cumulative, 0)

        decorated()
        self.assertEqual(self.cumulative, 1)

        decorated()
        self.assertEqual(self.cumulative, 1)


    def test_with_lazy_decorator_two_calls_with_application_on_each_call(self):
        self.cumulative = 0

        decorator_made_lazy = make_decorator_lazy(self.decorator, apply_on_each_call=True)
        self.assertEqual(self.cumulative, 0)

        decorated = decorator_made_lazy(self.f)
        self.assertEqual(self.cumulative, 0)

        decorated()
        self.assertEqual(self.cumulative, 1)

        decorated()
        self.assertEqual(self.cumulative, 2)


class Tests_factory(unittest.TestCase):
    def setUp(self):
        def factory(option):
            def decorator(f):
                self.cumulative += 1
                @wraps(f)
                def new_decorated_f(*args, **kwargs):
                    return f(*args, **kwargs)
                return new_decorated_f
            return decorator
        self.factory = factory

        def f():
            pass
        self.f = f


    def test_without_lazy_decorator(self):
        self.cumulative = 0

        decorated = self.factory(10)(self.f)
        self.assertEqual(self.cumulative, 1)

        decorated()
        self.assertEqual(self.cumulative, 1)


    def test_with_lazy_decorator(self):
        self.cumulative = 0

        decorator_factory_made_lazy = make_decorator_returning_function_returning_lazy_decorator(self.factory)
        self.assertEqual(self.cumulative, 0)

        decorated = decorator_factory_made_lazy(10)(self.f)
        self.assertEqual(self.cumulative, 0)

        decorated()
        self.assertEqual(self.cumulative, 1)


    def test_with_lazy_decorator_two_calls(self):
        self.cumulative = 0

        decorator_factory_made_lazy = make_decorator_returning_function_returning_lazy_decorator(self.factory)
        self.assertEqual(self.cumulative, 0)

        decorated = decorator_factory_made_lazy(10)(self.f)
        self.assertEqual(self.cumulative, 0)

        decorated()
        self.assertEqual(self.cumulative, 1)

        decorated()
        self.assertEqual(self.cumulative, 1)


    def test_with_lazy_decorator_two_calls_with_application_on_each_call(self):
        self.cumulative = 0

        decorator_factory_made_lazy = make_decorator_returning_function_returning_lazy_decorator(self.factory,
            apply_on_each_call=True)
        self.assertEqual(self.cumulative, 0)

        decorated = decorator_factory_made_lazy(10)(self.f)
        self.assertEqual(self.cumulative, 0)

        decorated()
        self.assertEqual(self.cumulative, 1)

        decorated()
        self.assertEqual(self.cumulative, 2)
