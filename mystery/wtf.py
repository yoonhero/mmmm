import inspect

# binary files are buffered in fied-size chunks; (default 8MiB)
# with open("wtf.py", "r+") as f:
#     text = f.read()
#     f.seek(0)
#     f.write("hi" + text)

print(type.mro)

class MyMeta(type):
    def mro(cls): # read only (__new__ or __init__)
        print(f"mro called for {cls.__name__}")
        return [cls, object]

# class instantiatinon
# ㄴ type: C3 linearization
class A():
    def a(self): return "a"

class B(A, metaclass=MyMeta):
    _x = None
    @property
    def x(self): return self._x
    @x.setter
    def x(self, value): self._x = value
    @x.deleter
    def x(self): del self._x

b = B()
b.x = 10
print(b.x)
del b.x
print(b.x)

class C(B):
    # super(C, self).method()가 호출되기 때문에
    # "diamond diagram" 등을 구현할 수 있다.
    def a(self): return super() # with __mro__!

# class          <- object
# class of class <- type / meta-class(?)
print(C.__mro__) # Method Resolution Order
# print(B().a()) -> u can delete class dependency
print(C().a())

class X: a = 1
print(X, type('X', (), dict(a=1)))

# type is instance of itself -> bootstrapping
# 뱀이 자기 꼬리를 무는 우아한 기행.
print(type(type) is type)
print(type(type(type(type)))) # type!
c = C()
print(c.__class__ is C) # c is instance of C
print(C.__class__ is MyMeta) # C is instance of MyMeta
print(A.__class__ is type)
print(C.__bases__ == (B,))
print(C.__mro__ == (C, object))
# print(str.__mro__)

# the root class is "object"
print(object.__new__(object))
print(object.__hash__(object) == object.__hash__(object))
print(object.__hash__(object) == object.__hash__(object()))