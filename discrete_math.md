## Discrete math

> I am newbie on counting number.

-   Stanley-Style: enumeratic / algebric / geometry
-   Erdos-Style: extermal / probablistic

**Thm 1.1** (Pigeon-Hole Principle)

Let n and k be postiive integers, and let $n \geq k$. Suppose we have to place n identical balls into k identical boxes. Then there will be at least one box in which we place at least two balls.

(**pf**) by contradiction

**Example 1.2**: There is an element in the sequence 7, 77, 777, 7777, ... that is divisible by 2003.

solution: there are more than 2003 elements and 2002 possible remainders(mod 2003). for some i, jth remainders are same. $a_i - a_j$ be the $a_k * 10^k$.

-   [related problem](https://www.acmicpc.net/problem/8112)
-   prove that among eight integers, there are always two whose difference is divisible by seven.

**Example 1.5**: Ten points are given within a square of unit size. Then there are two of them that are close to each other than 0.48, and there are three of them that can be covered by a disk of radius 0.5

solution:

1. divide nine equal areas. some area contain more than 1. $\frac{\sqrt{2}}{3}<0.48$.
2. divide four equal areas in which connects the diagonal. some area contains more than 2.

---

**This is Elementary Counting Broh**

-   Double counting: help you.
-   Finding Bijection: you need to smart.

### Ch4

-   Catalan Number
-   [Young Diagram & Grassmannian](https://ocw.mit.edu/courses/18-212-algebraic-combinatorics-spring-2019/0ed77654f610e0432a288bb27abc202d_MIT18_212S19_lec8.pdf)

### Ch5. Partition

**Composition**

> distribute same n-object into different k-box.

**Thm 5.2**

For $n\geq k$, the number of weak composition of n into k parts is $\binom{n+k-1}{k-1}$.

**Cor**: # of composition = $\binom{n-1}{k-1}$

Q: what if k is not fixed?

weak composition -> infinite / composition $2^{n-1}$

---

**Set Partition**

> distribute different n-object into same k-box

_Note_: # of perm $[n]$ into k non-empty block is $S(n, k)$("Stirling number")

**Cor**: $S(n, n-1)=\binom{n}{2}$, $S(n,1)=S(n,n)=1$

---

**Thm 5.8**

$n \geq k$, $S(n, k)=S(n-1, k-1)+kS(n-1, k)$

(**pf**) think the each case

1. n forms a singleton -> $S(n-1, k-1)$
2. not -> $kS(n-1, k)$

---

**Cor**: # of all surjective functions $f:[n]\to[k]$ is $k! S(n, k)$

**Cor 5.10**:

For any real number $x$, and $n\in \mathbb{N}$. we have $x^n=\sum S(n, k)(x)_k$ ($(x)_k=x(x-1)...(x-k+1)$)

(**pf**) since both sides are polynomial. it is enough to prove (\*) for all positive $x$

Assume $x \in \mathbb{N}$, $x^n$ is # of $[n] \to [x]$.

$RHS = \sum_{size of im(f)}$ (# of possible Image I) $= \sum_{k}^{n} \binom{x}{k} k!S(n, k)$

Thus, $x^n=\sum S(n, k)(x)_k$.

**Def**: The nubmer of all set partition of $[n]$ into non-empty parts is denoted by $B(n):=\sum S(n, k)$(Bell number)

**HW 01 #3**: Let $B_k(n)$ be # of partitions of $[n]$ so that if i and j are in the same block, then $|i-j| \gt k$. Prove that $B_k(n)=B(n-k)$, for all $n \geq k$.

(**pf**)

B_k를 작은 구성요소로 나누어서 관찰해보면 $S(n, k)$와 동치인 것을 발견할 수 있고 $n-\alpha$일 때 조건을 만족하게 되어 이를 다시 재구성하면 증명 완.

**HW 01 #6**: Let $F(n)$ denote # of partitions of $[n]$ which contain no singleton blocks. Find a formula for the numbers of $F(n)$ in terms of the $B(n)$.

(**pf**) 포함-배제 원리

---

**Thm 5.12**:

$B(n+1)=\sum \binom{n}{i} B(i)$

(**pf**) n+1 belongs to block of size (n-i+1)

---

**Integer Paritition**

> distribute same n-object into same k-box.

**Def**: Let $a_1 \geq a_2 \geq ... \geq a_k \geq 1$ s.t. $\sum a_i = n$

-   The sequence $(a_1, ..., a_k)$ is called a partition of n.
-   The # of partitions is denoted by $p(n)$ (Exactly k parts $p_k(n)$)

**Def**: A partition of n is self-conjugate if it is equal to its conjugate.

---

**Thm 5.17**:

the # of partitions of n into at most k parts is equal to that of paritions of n into parts not larger than k.

(**pf**) by conjugation

---

**Thm 5.18**:

the # of partitions of n into distinct odd parts is equal to that of all self conjugate parts of n.

(**pf**) construct the following bijection($f: {self-conjugate partition} \to {partition into distinctive odd parts}$)

i행 j열에 있는 원소를 min(i, j)번째 수에 더해준다. self-conjugate이기에 항상 distinct odd 개수만큼 counting 된다.

반대 방향이 있음도 자명하다.

---

**Thm 5.22**:

Let $\bold{a}=(a_1, ..., a_k)$ partition of n and let $m_i$ be the multiplicity of i as a part of a. Then # of set partition $[n]$ that are of $type(\bold{a})$ is equal to $P_a=\frac{\binom{n}{a_1 ... a_k}}{\prod m!}$

(**pf**) trivial

**Def**: pentagonal number: $\frac{k(3k-1)}{2}$ for any integer k.

_Me_: 삼각수(triangular number)는 relu function의 (2d plane max division) - 1이다.

-   다음의 사실은 삼각수가 자연수 순서대로 더하는 성질 때문이다.
-   사각수는 홀수를 더한다.

---

**Lemma 2**[Bona Ch8]:

$\sum p(n)x^n=\prod \frac{1}{1-x^k}$

(**pf**) coeff of $x^n$ = # of $\{ (a_1, a_2, ..., a_n) | a_1 + 2 \times a_2 + ... + n \times a_n \}$

---

**Thm 3** [Stanley ECI Prep 1.8.7]:

$\prod (1-x^k) = \sum (-1)^k x^{\frac{n(3n-1)}{2}}$

(Franklin's **pf**) let $f(n) = q_e(n) - q_o(n)$, where $q_e(n)$(resp) is # of partition of n into an even number of distinct part. $\prod (1-x^k)=\sum f(n) x^n$ (trivial)

Hence, (WTS). $f(n)=(-1)^k$ if k is pentagonal number.

by defining involution $\pi(\lambda) \neq \pi(f(\lambda))$ ($\pi(\lambda) := $ # of parts)

right most NE diagonal과 가장 아래 줄 원소 개수를 비교해서 더 적은 쪽을 많은 쪽으로 옮긴다. (involution이 된다!)

다음이 어긋날 때는 두 크기가 같을 때 아니면, 아래 부분이 1만큼 길때이다. 그 경우에는 odd/even 개수가 다른 한쪽이 하나가 더 많게 되고 이때를 구해보면 pentagonal number가 나온다.

-   [well-known theorem](https://en.wikipedia.org/wiki/Pentagonal_number_theorem)
-   [ps](https://codeforces.com/blog/entry/104312)

---

**Thm 1**:

$p(n)=p(n-1)+p(n-2)-p(n-5)-p(n-7)...$

-> to prove this, we need to use generating ft.

(**pf**) By Lemma 2 and Thm 3

$(\sum p(n)x^n)(1-x-x^2+x^5+x^7+...)=1$

consider the coeff of $x^m$ (it's 0)

$p(m)=p(m-1)+p(m-2)-p(m-5)-p(m-7)...$

---

**Thm 5.20**:

Let $g(n)$ be the number of partitions of n in which each part is at least two. Then $q(n) = p(n)-p(n-1), \forall n\geq 2$

(**pf**) subtract the case whose smallest part is 1.

**Cor**: least three. $q(n)=p(n)-p(n-1)-p(n-2)+p(n-3)$

### Ch6. Permutation
