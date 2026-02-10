#include <bits/stdc++.h>

// If you need to
// using namespace std;
#define pair std::pair
#define make_pair std::make_pair
#define string std::string
#define function std::function

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

template <class A> class optional {
    bool _isValid;
    A _value;

  public:
    optional() : _isValid(false) {}
    optional(A v) : _isValid(true), _value(v) {}
    bool isValid() const { return _isValid; }
    A value() const { return _value; }
};

optional<double> safe_root(double x) {
    if (x >= 0)
        return optional<double>{sqrt(x)};
    else
        return optional<double>{};
}

optional<double> safe_reciprocal(double x) {
    if (x != 0)
        return optional<double>{1 / x};
    else
        return optional<double>{};
}

// template <class A, class B>
// optional<B> partial_function(function<optional<B>(A)> f, optional<A> x) {
//     if (!x.isValid()) {
//         return optional<B>{};
//     }
//     return f(x.value());
// }

template <class A> optional<A> partial_identity(A x) { return optional<A>{x}; }
template <class A, class B, class C>
function<optional<C>(A)> partial_compose(function<optional<B>(A)> m1,
                                         function<optional<C>(B)> m2) {
    return [m1, m2](A x) {
        auto p1 = m1(x);
        if (!p1.isValid()) {
            return optional<C>{};
        }
        auto p2 = m2(p1.value());
        return p2;
    };
}

optional<double> safe_root_reciprocal(double x) {
    return partial_compose<double, double, double>(safe_reciprocal,
                                                   safe_root)(x);
}

int main(void) {
    Writer<bool> is = isOdd(3);
    std::cout << is.first << is.second << "\n";

    std::cout << safe_root_reciprocal(4).value();
    std::cout << safe_root_reciprocal(0).isValid();
    return 0;
}