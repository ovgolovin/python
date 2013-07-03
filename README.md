Python tasks
======

##### Task 1
Write decorator which makes function supporting currying.
```
@curry
def f(a,b,c):
   pass
   
f(a)(b)(c) == f(a,b)(c)  == f(a,b,c)
```

##### Task 2
Write decroator applying to another decorator making the latter lazy,
so that they are applied just before function is called.

##### Task 3
Write your own `xrange` implementstion.

##### Task 4
Write `ireduce`.

##### Task 5
Write *Sieve of Eratosthenes* using lambda, comprehensions, map reduce filter, itertools, etc. so as the whole function is expression.

##### Task 6
Make it possible for a user to create infix operators

http://www.haskell.org/haskellwiki/Infix_operator

##### Task 7
Implement function topological sorting.

Create decorator which allows you to achieve this:
http://blog.getprismatic.com/blog/2012/10/1/prismatics-graph-at-strange-loop.html
