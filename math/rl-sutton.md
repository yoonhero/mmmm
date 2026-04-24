1. Exercise 3.11 - If the current state is St, and actions are selected according to stochastic policy pi, then what is the expectation of Rt+1 in terms of pi and the four-argument function p (3.2)?

<!-- $R_{t+1}=\sum_{s' \in S} p(s'|s) \sum_{a \in A} \pi(a|s') R(s',a)$ -->

$R_{t+1}=\sum_a \pi(a|s) \sum_{s', r}p(s'|s, a)r$

pi를 중심으로 생각하였을 때의 식은 다음과 같음.

-   Bellman eq. 생각하면 recursive한 form이! -> $R(s', a)+\gamma V(s')$

2. Exercise 3.12 - Give an equation for vpi in terms of qpi and pi

$v_{\pi}(s)=\sum \pi(a|s) q_{\pi}(s, a)$

3. Exercise 3.13 - Give an equation for qpi in terms of vpi and the four-argument p.

$q(s, a)=\pi(a|s) \sum_{s'} p(s'|s)V(s')$

4. Exercise 3.14 - Grid World Numeric

$0.25 * (0 + 0.9 * (2.3 + 0.4 + -0.4 + 0.7)) = ~0.74$

5. Exercise 3.15 - relative values depending on "interval" or "sign"?

$v_c=(\gamma / 4) *c + (\gamma / 4) *v_c$

-> v*c가 등비급수.. why? = R*{t+k}에 대해서 항상 4가지 action이 존재하기 때문에 결국은 $\gamma ^ k * (c / 4^k) * 4^k$

6. Exercise 3.16 - reward+c remains unchanged?

yeah -> $c \in \R$

7.
