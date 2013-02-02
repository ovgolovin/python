#!/usr/bin/env python
from __future__ import division
import inspect
from itertools import izip, chain, imap, takewhile, count, islice
from collections import namedtuple, defaultdict
from copy import deepcopy
import unittest
import t7_scc


_Node = namedtuple('node', ['function', 'depends_on'])

def _split_list(alist, *indices):
    """
    Split alist at positions specified by indices and return iterator over resulting lists.
    """
    list_length = len(alist)
    indices = [list_length + index if index < 0 else index for index in indices]
    pairs = izip(chain([0], indices), chain(indices, [None]))
    return (alist[i:j] for i, j in pairs)

class Graph(object):
    def __init__(self, verbose_level = 0):
        """
        Create a new Graph object.
        After that you may use it to add functions and their dependencies to it.
        After that you may compile it.

        verbose_level: the higher the level the more debug messages will be output
        """
        self._verbose_level = verbose_level
        self._dependencies = {}
        self._defaults = {}



    def _debug_print(self, verbose_level, message, **format_options):
        if self._verbose_level >= verbose_level: # interpolate string only when it's necessary
            message = message.format(**format_options)
            print(message)


    def add_function(self, f):
        """
        Add function to current graph object.


        Usage:
        @graph_object.add_function
        def y(x):
            return sum(x)

        or

        def y(x):
            return sum(x)

        graph_object.add_function(y)

        All the dependencies will be taken from the function the application of add_function is being made to,
        e.g. in case of abovementioned y, add_function will figure out that y depends on the results of function x,
        which should be added to graph_object as well, otherwise x will be regarded as parameter.

        You may specify default values, e.g.

        @graph_object.add_function
        def within(x, y , tolerance = 0.5):
            return abs(y - x) <= tolerance

        tolerance, if not specified, will be taken from default value (even if it is somewhere in the middle
        of the dependency graph, in which case it will be tried to calculate based on its dependencies
        and if failed, then the default value will be taken)

        """

        arguments = inspect.getargspec(f).args
        default_values = inspect.getargspec(f).defaults
        default_values = () if default_values is None else default_values
        fname = f.__name__


        if default_values:
            non_default_names, default_names = _split_list(arguments, -len(default_values))
        else:
            non_default_names, default_names = arguments, ()

        defaults_dict = dict(izip(default_names, default_values))

        if fname in self._dependencies:
            raise(ValueError("The function '{fname}' has already been declared".format(fname = fname)))

        for name in defaults_dict:
            if name in self._defaults:
                raise(ValueError("The default value for '{name}' has already been specified".format(name = name)))

        self._dependencies[fname] = _Node(function = f, depends_on = set(arguments))
        self._defaults.update(defaults_dict)


        return f


    def compile(self):
        """
        Get a compiled object of a graph which can be later used to make calculations.
        """
        if not self._dependencies:
            raise(ValueError("There are no dependencies to be compiled. Add them by 'add_function' method."))

        # Search for cycles
        sccs = t7_scc.get_leaders_from_edges((name, dependent) for (name, value) in self._dependencies.iteritems()
            for dependent in value.depends_on)
        if any(imap(lambda x: len(x) > 1, sccs)):
            message = ["You have cyclic dependencies between functions:"]
            for scc in sccs:
                if len(scc) > 1:
                    message.append(' <-> '.join(scc))
            raise(ValueError('\n'.join(message)))
        return _CompiledGraph(deepcopy(self._dependencies), deepcopy(self._defaults), self._verbose_level)


class _CompiledGraph(object):
    def __init__(self, dependencies, defaults, verbose_level = 0):
        self._dependencies = dependencies
        self._defaults = defaults
        self._verbose_level = verbose_level
        self._topologically_sorted = self._sort_topologically()

    def _sort_topologically(self):

        levels_by_name = {}
        names_by_level = defaultdict(set)

        def walk_depth_first(name):
            if name in levels_by_name:
                return levels_by_name[name]
            node = self._dependencies.get(name, None)
            depends_on = None if node is None else node.depends_on
            level = 0 if depends_on is None else (1 + max(walk_depth_first(lname) for lname in depends_on))
            levels_by_name[name] = level
            names_by_level[level].add(name)
            return level

        for name in self._dependencies:
            walk_depth_first(name)

        return list(takewhile(lambda x: x is not None, (names_by_level.get(i, None) for i in count())))


    def sort_topologically(self):
        """
        Get a topologically sorted functions in layers with each layer dependent only on the previous one.
        """
        return deepcopy(self._topologically_sorted)


    def _debug_print(self, verbose_level, message, **format_options):
        if self._verbose_level >= verbose_level: # interpolate string only when it's necessary
            message = message.format(**format_options)
            print(message)


    def lazily_calculate(self, **kwargs):
        """
        Get a lazy function which will calculate the needed value (and all the values
        it depends on) only when this value is queried.
        Specify in parameters the initial values.

        To get the value of the needed function, use
        - access by index result['name']
        - attribute access result.name

        Note, that this function is lazy and may trigger exception, when a needed parameter is missing,
        some time later after a few successful queries, only when it stumbles into not having the needed
        parameter in the calculation being performed.
        """
        return _Evaluator(self, **kwargs)


    def calculate(self, **kwargs):
        """
        Calculate the values of all the functions basing on the parameters provided in the arguments.

        To get the value of the needed function, use
        - access by index result['name']
        - attribute access result.name
        """
        result = self.lazily_calculate(**kwargs)
        result.calculate_all()
        return result


class _Evaluator(object):
    def __init__(self, compiled_graph, **kwargs):
        """
        Create an evaluator of compiled_graph object
        """


        self._dependencies = compiled_graph._dependencies
        self._defaults = compiled_graph._defaults
        self._verbose_level = compiled_graph._verbose_level
        self._topologically_sorted = compiled_graph._topologically_sorted
        self._all_names = set(name for level in self._topologically_sorted for name in level)
        self._cache = {}
        self._failed_to_calculate = set()


        for name,value in kwargs.iteritems():
            if name not in self._topologically_sorted[0]:
                raise(TypeError("You have provided redundant argument {name}".format(name=name)))

        self._cache.update(kwargs)


    def _debug_print(self, verbose_level, message, **format_options):
        if self._verbose_level >= verbose_level: # interpolate string only when it's necessary
            message = message.format(**format_options)
            print(message)
        if self._verbose_level >= 4:
            print(" Cache: '{cache}'".format(cache=self._cache))
            print(" Failed_to_calculate cache: '{cache}'".format(cache=self._failed_to_calculate))

    def _calculate_value_directly_from_dependants(self, name):
        kwargs = {}
        for dependant in self._dependencies[name].depends_on:
            kwargs[dependant] = self._calculate_value(dependant)
        return self._dependencies[name].function(**kwargs)

    def _calculate_value(self, name):
        if name in self._cache:
            return self._cache[name]
        if name in self._failed_to_calculate:
            raise ValueError("No value for '{name}'".format(name=name))
        if name in self._topologically_sorted[0]:
            if name in self._defaults:
                result = self._defaults[name]
            else:
                self._failed_to_calculate.add(name)
                raise ValueError("No value for '{name}'".format(name=name))
        else:
            try:
                result = self._calculate_value_directly_from_dependants(name)
            except ValueError:
                if name in self._defaults: # fall back on default value
                    result = self._defaults[name]
                else:
                    self._failed_to_calculate.add(name)
                    raise ValueError("Can't calculate value for '{name}'".format(name=name))
        self._cache[name] = result
        return result


    def calculate_all(self):
        """
        Calculate the values of all functions.
        """
        for layer in islice(self._topologically_sorted, 1):
            for name in layer:
                self._calculate_value(name)


    def calculate_all_possible(self):
        """
        Calculate all the values which could be calculated.
        The values unable to be calculated will be skipped.
        """
        for layer in islice(self._topologically_sorted, 1, None):
            for name in layer:
                try:
                    self._calculate_value(name)
                except ValueError:
                    pass # just silently skip it


    def __getitem__(self, item):
        if item not in self._dependencies:
            raise KeyError("No name '{}'".format(item))
        return self._calculate_value(item)


    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError("No name '{}'".format(item))


    def __iter__(self):
        return ((name, self[name]) for level in islice(self._topologically_sorted, 1, None) for name in level)


    def iterate_over_successfully_calculated(self):
        self.calculate_all_possible()
        return ((name, self[name]) for level in islice(self._topologically_sorted, 1, None) for name in level if name not in self._failed_to_calculate)




class Tests(unittest.TestCase):

    def test_adding_one_function(self):
        graph = Graph()

        @graph.add_function
        def a(x):
            return x*x
        compiled = graph.compile()
        result_one = compiled.lazily_calculate(x=7)['a']
        self.assertEqual(result_one, 49)


    def test_raises_valueerror_on_adding_function_with_the_same_name_twice(self):
        graph = Graph()

        @graph.add_function
        def a(x):
            return x*x

        self.assertRaises(ValueError, graph.add_function, a)


    def test_raises_valueerror_on_specifiying_default_value_twice(self):
        graph = Graph()

        @graph.add_function
        def a(x=7):
            return x*x

        def b(x=9):
            return x*x

        self.assertRaises(ValueError, graph.add_function, b)


    def test_sharing_compiled_object(self):
        graph = Graph()

        @graph.add_function
        def a(x):
            return x*x
        compiled = graph.compile()
        result_one = compiled.lazily_calculate(x=7)['a']
        result_two = compiled.lazily_calculate(x=9)['a']
        self.assertEqual(result_one, 49)
        self.assertEqual(result_two, 81)


    def test_compilation_produces_valueerror_on_cycles_in_dependencies(self):
        graph = Graph()

        @graph.add_function
        def a(x):
            return x*x

        @graph.add_function
        def b(a):
            return a*a

        @graph.add_function
        def c(b):
            return b*b

        @graph.add_function
        def x(c):
            return c*c

        self.assertRaises(ValueError, graph.compile)


    def test_topological_sort_has_all_arguments_on_level_zero(self):
        graph = Graph()

        @graph.add_function
        def a(x):
            return x*x

        @graph.add_function
        def b(a, x):
            return a*a

        @graph.add_function
        def c(b, a, x , q):
            return b*b

        self.assertEqual(graph.compile().sort_topologically()[0], set(['x', 'q']))


    def test_should_raise_valueerror_on_missing_parameters_at_full_calculate(self):
        graph = Graph()

        @graph.add_function
        def a(x,y):
            return x*y

        @graph.add_function
        def b(y):
            return y*y

        self.assertRaises(ValueError, graph.compile().calculate, y=5)


    def test_shouldnt_raise_valueerror_on_missing_parameters_at_lazy_calculate(self):
        graph = Graph()

        @graph.add_function
        def a(x,y):
            return x*y

        @graph.add_function
        def b(y):
            return y*y

        self.assertEquals(graph.compile().lazily_calculate(y=5)['b'], 25)


    def test_access_by_attribute(self):
        graph = Graph()

        @graph.add_function
        def a(x):
            return x*x

        result = graph.compile().calculate(x=5)

        self.assertEquals(result.a, result['a'])


    def test_using_default_value_for_initial(self):
        graph = Graph()

        @graph.add_function
        def a(x=2):
            return x*x

        @graph.add_function
        def b(a):
            return a*a

        result = graph.compile().calculate()

        self.assertEquals(result.b, 16)


    def test_overriding_initial_default(self):
        graph = Graph()

        @graph.add_function
        def a(x=2):
            return x*x

        @graph.add_function
        def b(a):
            return a*a

        result = graph.compile().calculate(x=3)

        self.assertEquals(result.b, 81)


    def test_using_function_default(self):
        graph = Graph()

        @graph.add_function
        def a(x):
            return x*x

        @graph.add_function
        def b(a=2):
            return a*a

        result = graph.compile().lazily_calculate()

        self.assertEquals(result.b, 4)


    def test_function_default_is_overridden_by_downstream_parameter(self):
        graph = Graph()

        @graph.add_function
        def a(x):
            return x*x

        @graph.add_function
        def b(a=1):
            return a*a

        result = graph.compile().lazily_calculate(x=3)

        self.assertEquals(result.b, 81)


    def test_dict_of_successfully_calculated(self):
        graph = Graph(verbose_level=0)

        @graph.add_function
        def a(x,y):
            return 2*x

        @graph.add_function
        def b(y):
            return 2*y

        @graph.add_function
        def c(a,b):
            return a + b


        @graph.add_function
        def d(y,b):
            return y + b

        result = graph.compile().lazily_calculate(y=3)
        self.assertEquals(dict(result.iterate_over_successfully_calculated()), {'b': 6, 'd': 9})




def example():

    graph = Graph(verbose_level=0)

    @graph.add_function
    def n(xs):
        return len(xs)

    @graph.add_function
    def m(xs, n):
        return sum(xs) / n

    @graph.add_function
    def m2(xs, n):
        return sum(x**2 for x in xs) / n

    @graph.add_function
    def var(m, m2):
        return m2 - m**2

    compiled = graph.compile()
    result = compiled.calculate(xs = [1,2,3,4])
    print(result._topologically_sorted)
    print(dict(result))

if __name__ == '__main__':
    example()
