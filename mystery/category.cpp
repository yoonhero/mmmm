#include <bits/stdc++.h>

// If you need to
using namespace std;

pair<bool, string> negate_(bool b) { return make_pair(!b, "This is negate"); }

pair<bool, string> even(int n) { return make_pair(n % 2 == 0, "This is even"); }

pair<bool, string> odd(int n) {
    pair<bool, string> isEven = even(n);
    pair<bool, string> isOdd = negate_(isEven.first);
    return make_pair(isOdd.first, isEven.second + isOdd.second);
}

// We are programmer, so abstrac it! - Book
template <class A> using Writer = pair<A, string>;

template <class A, class B, class C>
function<Writer<C>(A)> compose(function<Writer<B>(A)> m1,
                               function<Writer<C>(B)> m2) {
    return [m1, m2](A x) {
        auto p1 = m1(x);
        auto p2 = m2(p1.first);
        return make_pair(p2.first, p1.second + p2.second);
    };
}

Writer<bool> isOdd(int n) { return compose<int, bool, bool>(even, negate_)(n); }

template <class A> Writer<A> identity(A x) { return make_pair(x, ""); }

int main(void) {
    Writer<bool> is = isOdd(3);
    cout << is.first << is.second << "\n";
    return 0;
}