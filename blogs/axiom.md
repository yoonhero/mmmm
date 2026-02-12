```
'호기심'을 주어진 공리에서 연역적으로 이끌어낼 수 있는 사실들 중에 "아름다운" 것을 고르는 능력으로 정의하자.
```

단순한 형태의 지능은 상태(state)가 주어졌을 때 특정한 행동(action)을 하는 함수로 정의할 수 있다. 이렇게 정의한 단순한 지능을 'mere intelligence'라고 부르자. 이보다 상위 단계의 지능을 '호기심'을 가지고 행동하는 것이라고 정의하자. 이는 단순히 상태의 변화에 따른 multivariable calculus 수준의 'mere intelligence'을 넘어서 '욕구'를 가지고 행동하는 것을 말한다. ('욕구'는 '호기심' 있는 것을 하려고 하는 능력이다.)

두 지능의 타입(haskell)을 아래와 같이 표현할 수 있다.

-   `mere intelligence` :: state -> action
-   `curiosity intelligence` :: (Curiosity c) => c axiom -> s -> (c axiom -> s -> a) -> action

후술하겠지만, 'mere intelligence'는 일반적인 Policy function 이라고 생각할 수 있다. 'curiosity intelligence'에서 *c axiom*는 공리에 따라서 'mere intelligence'(probablistic)를 선택하는 모나드이며, (c axiom -> s -> a)는 '욕구'로 매슬로의 욕구단계를 따르거나, 공리주의자(utilitarian)처럼 행동할 수 있다. 이 두 지능의 "Computable" 차이를 분석함으로서 현재의 'mere intelligence' 모델이 표현하지 못하는 "Curiosity"에 대해 분석하고자 한다.
