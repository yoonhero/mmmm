> > 삼, 육, 구~~ 삼, 육, 구~

![boj](https://www.acmicpc.net/problem/18765)

![]+-\* 만을 활용해서 0부터 1000까지 만들어보자!

basics

```js
![] = false
+![] = 0
+!![] = 1
```

fun facts

```js
+"1" = 1
+![]+[] = "0"
["1"]+["1"] = "11"
"1"+1="11"
+[+!![]+[]+[+!![]]] = 11
```

왜? -> EvaluateStringOrNumericBinaryExpression(lhs, "+", rhs)

binary op

-   \+ = Any string ? string concat : numeric op
-   \- = numeric op(BigInt, Number)
-   \* = numeric op

unary op

-   \+ = ToNumber(GetValue(expr))
-   \- = ToNumeric(GetValue(expr))
-   \! = !ToBoolean(GetVAlue(expr))

> Evaluate from left subtree = side effect가 많은 언어에서 평가 순서라도..
