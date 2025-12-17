#!/usr/bin/env python
# python is well-known functional-language!

# lambda calculus: a-conversion / b-reduction
##   Type: lambda x.M : A \to B
##   -> constrain input!
##
# "Church-Turing Thesis"
##   turing machine can define being algorithmic!!!!!!
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
human_logic = lambda f: f(1)(0)


# Church Encoding - How can I store value using function?
pair = lambda a: lambda b: lambda s: s(a)(b)
fst = lambda p: p(true)
scd = lambda p: p(false)


# numbers - Neuman Approach
zero = lambda f: lambda s: s
isZero = lambda n: n(lambda _: false)(true)

succ = lambda n: lambda f: lambda s: f(n(f)(s))
one = lambda f: lambda s: succ(zero)(f)(s) # f(s)
two = lambda f: lambda s: succ(one)(f)(s) # f(f(s))
three = lambda f: lambda s: succ(two)(f)(s) # f(f(f(s)))

pred = lambda n: fst(n(lambda p: pair(scd(p))(succ(scd(p))))(pair(zero)(zero)))

add = lambda m: lambda n: lambda f: lambda s: m(f)(n(f)(s)) # m(n(s))
mul = lambda m: lambda n: lambda f: lambda s: m(n(f))(s) # recursion

reduce_num = lambda n: n(lambda x: x+1)(0)
print(reduce_num(succ(zero)))
print(reduce_num(add(one)(two)))
print(reduce_num(mul(two)(two)))
print(reduce_num(mul(three)(three)))

print(human_logic(isZero(mul(one)(one))))  # 0
print(human_logic(isZero(mul(one)(zero)))) # 1


# arithmetic
sub = lambda m: lambda n: n(pred)(m) # m-n
leq = lambda m: lambda n: isZero(sub(m)(n)) # m <= n
eq = lambda m: lambda n: AND(leq(m)(n))(leq(n)(m)) # m <= n & n <= m
lt = lambda m: lambda n: AND(leq(m)(n))(NOT(leq(n)(m))) # m < n
print("Sub 3-1 =", reduce_num(sub(three)(one)))
print("3 < 1 is", human_logic(lt(three)(one)))
print("3 = 3 is", human_logic(eq(three)(three)))

# example
fibo = lambda n: fst(n(lambda p: pair(scd(p))(add(fst(p))(scd(p))))(pair(zero)(one)))
five = succ(succ(three))
print("5th fibo num is", reduce_num(fibo(five)))

power = lambda n: lambda m: fst(m(
    lambda p: pair(scd(p))(mul(fst(p))(scd(p)))
)(pair(one)(n)))
print("3^5 is", reduce_num(power(three)(five)))

factorial = lambda n: fst(n(
    lambda p: ifthen(isZero(scd(p)))(p)(
        pair(mul(fst(p))(scd(p)))(pred(scd(p)))
    )
)(pair(one)(n)))
print("5! is", reduce_num(factorial(five)))
print("0! is", reduce_num(factorial(zero)))

# pair-list: easy to come up with
# church-list: more likely to numeral def
li = pair(zero)(zero) # length / nil
push = lambda li: lambda el: pair(succ(fst(li)))(pair(el)(scd(li)))
index = lambda li: lambda n: fst(sub(fst(li))(n)(
    lambda p: scd(p)
)(li))
length = lambda li: fst(li)

lambda_list_ex = push(push(push(li)(one))(two))(three)
print("length of [1, 2, 3] is", reduce_num(length(lambda_list_ex)))
print("[1, 2, 3][1] is", reduce_num(index(lambda_list_ex)(one)))

nil = lambda c: lambda n: n
cons = lambda h: lambda t: lambda c: lambda n: c(h)(t(c)(n))
## (cons 1 nil) c n = c 1 (nil c n) = c 1 n
## (cons 2 (cons 1 nil)) = c 2 (c 1 n)
length = lambda xs: xs(lambda x: lambda k: succ(k))(zero)
append = lambda xs: lambda ys: lambda c: lambda n: xs(c)(ys(c)(n)) ## xs ++ ys
sum = lambda xs: xs(lambda x: lambda k: add(x)(k))(zero)

church_list_ex = cons(three)(cons(two)(cons(one)(nil)))
print("length of [1, 2, 3] is", reduce_num(length(church_list_ex)))
print("sum([1, 2, 3]) is", reduce_num(sum(church_list_ex)))


# partial function = A \to B(probably)
# Church Numeral: finite call -> total functions
# Y combinator: possible infinite recursion -> total/partial functions (find fixed point)
##   In Lambda Calculus recursion is not possible as ft don't have name.
##   in other words, alpha-conversion!(=local name)
##   
##   Strategy:
##     eager: call-by-value
##     lazy: call-by-name
##
##   Z = f.(x.f(v.x x v))(x.f(v.x x v))
##     A = f(v.x x v)
##     Z F = F(v. A A v) = A A
##     !!! Z F = F(v. Z F v) !!! // self-referencial structure
##   this is not allowed in typed-functional lang
##   
IF = lambda b: lambda t: lambda e: b(t)(e)()
Z = lambda f: (
    lambda x: f(lambda v: x(x)(v))
)(
    lambda x: f(lambda v: x(x)(v))
)
## value-evaluation is prior to branch in Eager-Mode
fact = Z(
    lambda f: lambda n: IF(isZero(n))(
        lambda: one
    )(
        lambda: mul(n)(f(pred(n)))
    )
)
## fact(two) = (Z(F))(two)
## -> F(v. Z(F)v)(two)
## -> mul(2)( (v. Z(F)v)(1) )
## -> mul(2)( Z(F)(1) )
## -> mul(2) fact(one)
## -> mul(2)(mul(1)(fact(zero)))
## -> mul(2)(mul(1)(1)) !!!
print("5! is", reduce_num(fact(five)))
print(fact)


# HALT on lambda calculus
# D = p. if HALT(p)(p) then omega else zero
##   HALT(D)(D)=true -> no halt
##   HALT(D)(D)=false -> halt
##
# EQUAL: Term \to Term \to Bool (impossible)


