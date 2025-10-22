# Source Code -> Lexer -> Parser -> Compiler -> Virtual Machine

# Parser - AST
import ast
source_code = """
x = 3 + 4
y = x - 4
def foo():
    y = x + 1
    print(y)
print(x)
foo()

if x > 4:
    print("hello world")

    
while x < 10:
    x += 1
    print(x)

def fibonacci(a, b):
    if a + b > 100:
        return a
    return fibonacci(a+b, a)
print(fibonacci(1, 1))
"""

class MultiplyTransformer(ast.NodeTransformer):
    def visit_BinOp(self, node):
        if isinstance(node.op, ast.Add):
            node.op = ast.Mult()
        return node
tree = ast.parse(source_code)
# new_tree = MultiplyTransformer().visit(tree)
print(ast.dump(tree, indent=4))

# Bytecode Level - Stack Machine IR
import dis
# dis.dis(f)
code_obj = compile(tree, filename="<ast>", mode="exec")
dis.dis(code_obj)

# Virtual Machine - PyEval_EvalFrame
print(f"==== PyEval_EvalFrame: ====")
exec(code_obj) # haha

import builtins
import types

class Function():
    def __init__(self, code_obj, defaults={}, kwdefaults={}):
        self.code_obj = code_obj
        self.kwdefaults = kwdefaults
        self.defaults = defaults
    def __call__(self, args, globals_, locals_):
        frame_locals = {}
        frame_locals.update(self.defaults)
        argnames = self.code_obj.co_varnames[:self.code_obj.co_argcount]
        for kw, arg in zip(argnames, args):
            frame_locals[kw] = arg
        result = mini_vm(code_obj=self.code_obj, globals_=globals_, locals_=frame_locals)
        return result
        
def mini_vm(code_obj, globals_=None, locals_={}):
    stack = []
    # locals -> globals -> builtins
    # f_builtins = {"len": len, "print": print, "range": range}
    globals_ = {"__builtins__": builtins.__dict__} if globals_ is None else globals_
    instructions = list(dis.get_instructions(code_obj))
    offset_to_index = {instr.offset: idx for idx, instr in enumerate(instructions)}
    
    i=0
    while i < len(instructions):
        instr = instructions[i]
        # print(i, instr)
        op = instr.opname
        arg = instr.argval
        if op == "RESUME":
            pass
        elif op == "LOAD_CONST":
            stack.append(arg)
        elif op == "LOAD_NAME" or op == "LOAD_GLOBAL":
            if arg in locals_:
                stack.append(locals_[arg])
            if arg in globals_:
                stack.append(globals_[arg])
            elif arg in globals_["__builtins__"]:
                # stack.append(f_builtins[arg])
                stack.append(globals_["__builtins__"][arg])
            else:
                raise NameError(f"name '{arg}' is not defined.")
        elif op == "LOAD_FAST":
            stack.append(locals_[arg])
        elif op == "STORE_NAME":
            globals_[arg] = stack.pop()
        elif op == "STORE_FAST":
            locals_[arg] = stack.pop()
        elif op == "BINARY_OP":
            b, a = stack.pop(), stack.pop()
            op_type = instr.argrepr
            if op_type == "+" or op_type == "+=": stack.append(a + b)
            elif op_type == "-"  or op_type == "-=": stack.append(a - b)
            elif op_type == "*"  or op_type == "*=": stack.append(a * b)
            elif op_type == "/" or op_type == "/=": stack.append(a / b)
            elif op_type == "**" or op_type == "**=": stack.append(a ** b)
            elif op_type == "//" or op_type == "//=": stack.append(a // b)
            elif op_type == "%" or op_type == "%=": stack.append(a % b)
            else:
                raise NotImplementedError(f"BINARY_OP {op_type}")
        elif op == "COMPARE_OP":
            b, a = stack.pop(), stack.pop() 
            op_type = arg
            if op_type == ">": stack.append(a > b)
            elif op_type == ">=": stack.append(a >= b) 
            elif op_type == "<": stack.append(a < b)
            elif op_type == "<=": stack.append(a <= b)
            elif op_type == "==": stack.append(a == b)
            elif op_type == "!=": stack.append(a != b)
        elif op == "POP_JUMP_FORWARD_IF_FALSE" or op == "POP_JUMP_BACKWARD_IF_FALSE":
            if not stack.pop():
                target_offset = arg
                i = offset_to_index[target_offset]
                continue
        elif op == "POP_JUMP_FORWARD_IF_TRUE" or op == "POP_JUMP_BACKWARD_IF_TRUE":
            if stack.pop():
                target_offset = arg
                i = offset_to_index[target_offset]
                continue
        elif op in ("JUMP_FORWARD", "JUMP_BACKWARD"):
            i = offset_to_index[arg]
            continue
        elif op == "PUSH_NULL":
            stack.append(None)
        elif op == "MAKE_FUNCTION":
            flags = instr.arg
            code = stack.pop()
            defaults = kwdefaults = annotations = closure = None
            # CPython 플래그 의미(하위 호환):
            # 0x01: defaults tuple
            # 0x02: kwdefaults dict
            # 0x04: annotations dict
            # 0x08: closure tuple of cells
            # if flags & 0x08:
            func = Function(code_obj=code) 
            stack.append(func)
        elif op == "PRECALL":
            stack.append(arg)
        elif op == "CALL":
            argc = stack.pop()
            args = [stack.pop() for _ in range(argc)][::-1]
            while stack and stack[-1] is None: # call stack 정리
                stack.pop()
            func = stack.pop()
            # print(f"[CALL] func={func} args={args} stack={stack[-5:]}")
            result = None
            if isinstance(func, Function):
                result = func(args, globals_, locals_)
            else:
                result = func(*args)
            stack.append(result)
        elif op == "POP_TOP":
            stack.pop()
        elif op == "RETURN_VALUE":
            return stack.pop() if stack else None
        else:
            raise NotImplementedError(f"opcode {op} not implemented")
        i += 1
print("==== Mini VM by me: ====")
mini_vm(code_obj)

# import sys
# import pdb
# import inspect
# def tracer(frame, event, arg):
#     print(f"[TRACE] {event} at {frame.f_code.co_name}:{frame.f_lineno}")
#     return tracer
# # sys.settrace(tracer)

# def f():
#     a = 1
#     b = 2
#     return a + b
# f()
# # pdb.set_trace()
# frame = inspect.currentframe()
# print(frame.f_locals)