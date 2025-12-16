#!/usr/bin/env python
# python is well-known functional-language!

# lambda calculus: a-conversion / b-reduction
##   Type: lambda x.M : A \to B
##   -> constrain input!
##
# "Church-Turing Thesis"
##   
##
# "Curry-Howard Isomorphism"
##   -> where (pf) : prop
##   - There may indeed, be other applications of the system than its use of logic (Alonzo Church, 1932)

# logics
true = lambda x: lambda y: x
false = lambda x: lambda y: y
ifthen = lambda b: lambda x: lambda y: b(x)(y)

NOT = lambda b: b(false)(true)
AND = lambda p: lambda q: p(q)(q) # true(false)(false) -> false
OR = lambda p: lambda q: p(p)(q) # false(false)(true) -> true

print(ifthen(true)(1)(2))
print(ifthen(NOT(true))(1)(2))


# numbers - Neuman Approach
zero = lambda f: lambda s: s
isZero = lambda n: n(lambda _: false)(true)

succ = lambda f: lambda n: f(n)
one = lambda f: lambda s: succ(f)(zero(f)(s)) # f(s)
two = lambda f: lambda s: succ(f)(one(f)(s)) # f(f(s))
three = lambda f: lambda s: succ(f)(two(f)(s)) # f(f(f(s)))

add = lambda m: lambda n: lambda f: lambda s: m(f)(n(f)(s)) # m(n(s))
mul = lambda m: lambda n: lambda f: lambda s: m(n(f))(s) # recursion

for_human = lambda x: x+1
print(succ(for_human)(succ(for_human)(0)))
print(add(one)(two)(for_human)(0))
print(mul(two)(two)(for_human)(0))
print(mul(three)(three)(for_human)(0))

print(isZero(mul(one)(one))(1)(0))  # 0
print(isZero(mul(one)(zero))(1)(0)) # 1

# loop
#rorin = lambda 
