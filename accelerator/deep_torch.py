import torch
import numpy as np
import os

os.environ["TORCH_SHOW_CPP_STACKTRACES"] = "1"
os.environ["TORCH_LOGS"] = "not_implemented"
# torch._C._set_dispatch_debug(True)

# YOU NEED TO BUILD PYTORCH WITH DEBUG MODE ON.
# > TORCH_LOGS="all" python - <<'EOF' 2>debug.log
# import torch
# x = torch.ones(100, 100)
# y = torch.ones(100, 100)
# z = x+y
# EOF

# print(torch._C._dispatch_dump_table("aten::add.Tensor"))
print(torch._C._dispatch_has_kernel_for_dispatch_key("aten::add.Tensor", "CPU"))
# torch.ops.aten.add.Tensor._schema

from torch.profiler import profile, record_function, ProfilerActivity
# -> Python: Tensor.__add__ (torch의 builtin)
# -> C++ Dispatcher: {AutogradCUDA, CUDA}
#   (device, dtype, layout) 알맞은 커널을 선택, 호출
# -> AutogradCUDA (wrapping) -> CUDA kernel
# -> wrapping result -> back to python
# deprecated approach?

device = "cpu"
param = {"device": device, "requires_grad": True, "dtype": torch.float}
x = torch.tensor([0,1,2], **param)
y = torch.tensor([4,5,6], **param)

sx = np.zeros((10000, 10000))
sx[0, 0] = 1
sparse_x = torch.tensor(sx, **param)
sparse_y = torch.zeros_like(sparse_x)

print(x.layout, sparse_x.T.layout)

initial_grad = torch.ones_like(x)
# with profile(activities=[ProfilerActivity.CPU], record_shapes=True, with_stack=True, profile_memory=True) as prof:
    # with record_function("add"):
with torch.autograd.profiler.profile(use_cpu=True) as prof:
    # z = x + y
    # torch.square(z).backward()
    torch.softmax(x, 0).backward(initial_grad)
print(prof.key_averages().table())
prof.export_chrome_trace("trace.json")

with profile(activities=[ProfilerActivity.CPU], record_shapes=True, with_stack=True, profile_memory=True) as prof:
    with record_function("sparse_add"):
        z = sparse_x + sparse_y
print(prof.key_averages().table())

from torch.fx.experimental.proxy_tensor import make_fx

def f(x, y):
    return x+y
gm = make_fx(f)(x, y)
print(gm.graph)

# def square(a):
#     for _ in range(5):
#         a = torch.square(a)
#     return a
# opt_square = torch.compile(square)
# opt_square(torch.randn(1000, 1000).to(device))

# from torch.utils.cpp_extension import load_inline
# cpp_source = """
# std::string hello_world() {
#     return "Hello World";
# }
# """

# mymodule = load_inline(
#     name='my_module',
#     cpp_sources=[cpp_source],
#     functions=['hello_world'],
#     verbose=True
# )

# print(mymodule.hello_world())

from torch.utils._python_dispatch import TorchDispatchMode
from dispatch_tracer import *
import pdb
import re
import pathlib

def get_snippet(schema: torch._C.FunctionSchema, pad=5):
    print(schema, type(schema), dir(schema), schema.returns)
    name = str(schema).split("(")[0]
    dump = torch._C._dispatch_dump_table(name)
    match = re.search(r"CPU: registered at .*?aten/src/(ATen/.*?):(\d+)", dump)
    rel_path, line = match.groups()
    line = int(line)
    file = pathlib.Path("./pytorch/build/aten/src") / rel_path
    lines = file.read_text(encoding="utf-8").splitlines()
    s, e = max(0, line-pad), min(len(lines), line+pad)
    print(f"\n>>> {file} (L{line})\n")
    for i in range(s, e):
        mark = ">>" if i + 1 == line else " "
        print(f"{mark} {i+1:5d}: {lines[i]}")

class DispatchTracer(TorchDispatchMode):
    def __init__(self):
        super().__init__()
        self._seen_ops = set()

    def __torch_dispatch__(self, func, types, args=(), kwargs=None):
        kwargs = kwargs or {}
        qname = op_qualified_name(func)

        print(f"\n=== aten call → {qname} ===")
        schema = getattr(func, "_schema", None)
        print(f"schema: {schema}")
        get_snippet(schema)
        
        # 실제 호출
        out = func(*args, **kwargs)
        print("→ result:", summarize_tensor(out))
        return out
    
x = torch.randn(4, 4, device="mps", requires_grad=True)
y = torch.randn(4, 4, device="mps", requires_grad=True)

# ~from native_functions.yml
# - func: mm(Tensor self, Tensor mat2) -> Tensor
#   structured_delegate: mm.out
#   variants: function, method
#   dispatch:
#     SparseCPU, SparseCUDA, SparseMPS: _sparse_mm
#     SparseCsrCPU, SparseCsrCUDA, SparseCsrMeta: _sparse_csr_mm
#   tags: core
with DispatchTracer():
    z = y.add(x)       # aten::add.Tensor
    w = torch.mm(x, y) # aten::mm
    loss = (z + w).sum()
    loss.backward()