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

### Ch6. Not So Vicious Cycles. Cycles in Permutations.

> permutation은 bijective function $[n] \to [n]$과 동형이다.

_Note_: you need to know the basics of Symmetric Group($S_n$).

**Cor**: All permutations can be decomposed into disjoint union of the cycles.

(**pf**)

1. By **lemma 6.4** each entry is a member of a cycle.
2. distinct cycles are disjoint.

---

_Note_: there are many ways to write same cycle decomposition.

**Def**: Canonical cycle form iff

1. each cycle is written with its largest first.
2. the cycles is written increasing order.

---

**Thm 6.9**

Let $a_1, ..., a_n$ be non-negative integer s.t. $\sum ia_i = n$.
Then # of n-permutatinos with $a_i$ cycles of length i is $\frac{n!}{\prod a_i! \prod i^{a_i}}$

(**pf**) easy to show

**Def**: $(a_1, ..., a_n)$ is called the type of cycle.

$f, g \in S_n$, $type(f) = type(g)$ iff $\exists h \in S_n$ s.t. $hfh^-1=g$

_Me_: conjugancy class! (결국 동형)

---

**Def**: # of n-perm with k cycles is called signless Stirling number of first kind and is denoted by $c(n, k)$.

The number $s(n, k)=(-1)^{n-k}c(n, k)$ is called a Stirling number of first kind.

**Thm 6.12**

let $n \geq k \gt 0$, then $c(n, k)=c(n-1, k-1)+(n-1)c(n-1, k)$

(**pf**)

1. 2~n까지 canonical form으로 적은 경우에 1을 추가한다고 생각(개인적으로 이게 깔금하다고 생각)
2. cycle 길이를 연장한다고 생각($b\to a$를 $b\to n \to a$로)

---

**Lemma 6.13**

$\sum c(n, k)x^k=x(x+1)...(x+n-1)$

(**pf**)

$x(x+1)...(x+n-1)(x+n)=\sum c(n+1, k)x^k \times x + \sum c(n+1, k)x^k \times n=\sum (c(n, k-1)+n \times c(n, k))x^k$

By **Thm 6.12**, $\sum (c(n, k-1)+n \times c(n, k))x^k=\sum c(n+1, k)x^k$

_Note_: $c(0, 0)=1$, $c(n, 0)=1$

By replacing $x$ by $-x$ and multiply $(-1)^n$ we have $\sum s(n, k)x^k = (x)_k$.

=> S(n, k) c(n, k) are entries of transition matrix between $\{1, x, x^2, ...\}$ and $\{1, (x)_1, (x)_2, ...\}$

**Thm 6.14**: Two matrices $[S(n, k)]_{n, k}$, $[s(n, k)]_{n, k}$ are inverse of each other.

---

**Lemma 6.15** Transition Lemma

g: permutation written in canonical cycle form. Then $g: S_n \to S_n$ is a bijection.

(**pf**)

1. g is well-defined (in group-theory it refers to output without ambiguity)
2. It is enough to construct an inverse

1) 사이클을 시작한다.
2) left-to-right maximum 원소가 나오기 전까지 오른쪽으로 이동한다.
3) permutation의 끝이 아니라면 1)로 돌아간다.

e.g. p=215436 -> (21)5436 -> (21)(543)(6)

---

**Prop 6.18**

let i and j be two elements of $[n]$. Then i and j are in the same cycle in exactly half of all permutation.

(**pf**) WLOG, assume $i=n, j=n-1$

Canonical cycle form으로 주어진 permutation을 작성했을 때 $n$과 $n-1$이 같은 사이클에 위치하는 경우는 $n-1$이 $n$ 뒤에 등장하는 것으로 이를 통해서 절반의 경우라는 것을 알 수 있음.

**Lemma 6.19**

$i \in [n]$ then probability of $i\in (k-cycle)=\frac{1}{n}$

(**pf**) WLOG, assume $i=n$

k-cycle 내부에 존재하는 경우는 n가 끝에서 k번째 위치할 때, 따라서 증명을 마침.

**Note**: i, j 대신 n-1, n으로 생각해도 괜찮은 이유는 택갈이.

---

**Def**: let ODD(m) (resp.) be the set of m-permutations with all cycles length is odd.

**Lemma 6.20**: $|ODD(2m)| = |EVEN(2m)|$

(**pf**)

ODD(2m)은 2k개의 사이클을 가진다.
