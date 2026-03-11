from __future__ import annotations
from collections.abc import Callable
from typing import overload, Type, Any, Protocol, Self
import ast, sys, pprint

# you know what? py3.12 be like this.
type Alias = str
a: Alias = "1"

@overload
def f(x: str) -> str: ...
@overload
def f[T](x: T) -> T: ...

def f(x): # template on python!
    if isinstance(x, str): x += " !"
    return x

print(f("a"))
print(f(1))

class HasEq[T](Protocol):
    def __eq__(self, y: T) -> bool: ...
    def __lt__(self, y: T) -> bool: ...

class Eq[T]:
    def __eq__(self, y: T): return NotImplementedError
    def __lt__(self, y: T): return NotImplementedError
    def __gt__(self, y: T): return not (self.__lt__(y) or self.__eq__(y))

class Show(Protocol):
    def __repr__(self) -> str: ...

def ab(a: HasEq, b: HasEq):
    return a == b

# functor ㄱ-
class IsFunctor[T](Protocol):
    def mmap[B](self, f: Callable[[T], B]) -> IsFunctor[B]: ...

class HasEqShow(HasEq, Show, Protocol):
    pass

# there's no intersection type in python!
class BTree[A: HasEqShow](IsFunctor[A]):
    def __init__(self, x: A):
        self.value: A = x
        self.left: BTree[A] | None = None
        self.right: BTree[A] | None = None
    def append(self, y: A):
        if y > self.value:
            if self.right is not None: self.right.append(y)
            else: self.right = BTree(y)
        else:
            if self.left is not None: self.left.append(y) 
            else: self.left = BTree(y)
    
    def mmap[B: HasEqShow](self, f: Callable[[A], B]) -> BTree[B]:
        new = BTree[B](f(self.value))
        new_left = None
        new_right = None
        if self.left:
            new_left = self.left.mmap(f)
        if self.right:
            new_right = self.right.mmap(f)
        new.left = new_left
        new.right = new_right
        return new

    def __print__(self, depth=0):
        indent = '\t'*(depth+1)
        left_repr = self.left.__print__(depth+1) if self.left is not None else "None"
        right_repr = self.right.__print__(depth+1) if self.right is not None else "None"
        return f"Node(value={self.value},\n{indent}left={left_repr},\n{indent}right={right_repr})"
    def __repr__(self): return self.__print__()

def larger_than_1(functor: IsFunctor):
    f = lambda x: x > Int(1)
    return functor.mmap(f)

class Int(Eq):
    def __init__(self, x):
        self.x = x
    def __lt__(self, y: Int) -> bool: return self.x < y.x
    def __eq__(self, y: Int) -> bool: return self.x == y.x
    def __repr__(self): return f"Int(value={self.x})"

print(ab(Int(1), Int(2)))

print(type(type))
print(type(HasEq))

tree = BTree(Int(2))
tree.append(Int(3))
tree.append(Int(1))
tree.append(Int(-1))
print(Int(3) > Int(1))
# print(Int(3) > 1)
print(larger_than_1(tree))

code = """
def greet(name: str | None) -> str:
    if name is None:
        return 42
    return "Hello " + name

age: int = "42"

def length(xs: list[int]) -> int:
    return len(xs) + xs"""

tree = ast.parse(code, type_comments=True)
# pprint.pp(ast.dump(tree, indent=4))

tables = {}

def travel(tree):
    if len(tree.body) == 0: return
    for item in tree.body:
        if isinstance(item, ast.FunctionDef) and len((args := item.args.args)) > 0:
            fn_name = item.name
            annotation = args[0].annotation
            if isinstance(annotation, ast.Subscript): # it's MVP type checker! won't care
                pass

travel(tree)
print(tables)