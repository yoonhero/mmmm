import torch
from huggingface_hub import hf_hub_download

# https://blog.janestreet.com/can-you-reverse-engineer-our-neural-network/
repo_id = "jane-street/2025-03-10"
# if you have python>3.11, setup 3.11
# from my investigation, they use cloudpickle what supports only exact same version of Python
# 
filename = "model_3_11.pt"

model_path = hf_hub_download(repo_id=repo_id, filename=filename)
print(model_path)

import pickletools
import zipfile
import os
import cloudpickle

squared = lambda x: x**2
pickled_lambda = cloudpickle.dumps(squared)
# cloudpickle.cloudpickle._make_function
#    SHORT_BINUNICODE 'cloudpickle.cloudpickle'
#    SHORT_BINUNICODE '_make_function'
#    STACK_GLOBAL
# print(pickletools.dis(pickled_lambda))

# print(zipfile.is_zipfile(model_path))
if not os.path.exists("data"):
    with zipfile.ZipFile(model_path, "r") as z:
        # this is typical serialization
            # data/0
            # data.pkl
            # byteorder
            # version
            # .data/serialization_id -> pt2(?)
        names = [n for n in z.namelist() if n.endswith(".pkl")]
        for name in names:
            with z.open(name, "r") as f:
                data = f.read()
                with open("data", "w") as f:
                    pickletools.dis(data, out=f)

from torch.nn.modules.container import Sequential

model = torch.load(model_path, weights_only=False, map_location="cpu")
# model.eval()
# <class 'torch.nn.modules.container.Sequential'>
print(type(model))

import inspect
from pprint import pprint
# pprint(dir(model))
# pprint(inspect.getsource(model.__class__))
# pprint(inspect.getsource(model.__call__))
# pprint(inspect.getsource(model.forward))
pprint(inspect.getsource(model._call_impl))
f = model._call_impl
print(f.__code__.co_filename) # '/tmp/ipykernel_1060068/378402040.py' -> fake; not exist

import dis
# Opcode on here: https://github.com/python/cpython/blob/main/Lib/pickle.py
# MARK: push special markobject on stack
# BINUNICODE: counted UTF-8 string argument
# REDUCE: apply callable to argtuple, both on stack
# LONG_BINGET: push item from memo on stack; index is 4-byte arg
dis.dis(model._call_impl)
#   2           0 RESUME                   0
#               2 LOAD_GLOBAL              0 (model)        
#              14 LOAD_METHOD              1 (forward)
#              36 LOAD_GLOBAL              4 (torch)
#              48 LOAD_METHOD              3 (Tensor)
#              70 LOAD_GLOBAL              9 (NULL + list)
#              82 LOAD_GLOBAL             11 (NULL + map)
#              94 LOAD_GLOBAL             12 (ord)
#             106 LOAD_GLOBAL             15 (NULL + str)
#             118 LOAD_FAST                0 (x)
#             120 PRECALL                  1                  
#             124 CALL                     1                str(x)
#             134 LOAD_CONST               0 (None)         -> const table
#             136 LOAD_CONST               1 (55)
#             138 BUILD_SLICE              2                -> slice(None, 55)
#             140 BINARY_SUBSCR                             -> s=str(x)[None:55] = str(x)[:55]
#             150 LOAD_METHOD              8 (ljust)
#             172 LOAD_CONST               1 (55)
#             174 LOAD_CONST               2 ('\x00')
#             176 PRECALL                  2                
#             180 CALL                     2                -> ljust(55, '\x00')
#             190 PRECALL                  2
#             194 CALL                     2                -> map(ord, x)
#             204 PRECALL                  1
#             208 CALL                     1                -> list
#             218 PRECALL                  1
#             222 CALL                     1                -> torch.Tensor
#             232 PRECALL                  1
#             236 CALL                     1                -> model.forward
#             246 RETURN_VALUE
decoded_tokenizer = lambda x: torch.tensor(list(map(ord, str(x)[None:55].ljust(55, '\x00'))))
# jane street genius make a trick with "lambda" to prevent easy reverse engineering... GOAT

first_block = model[0]
before_last_block = model[-4]
last_block = model[-2]
linears = [x for x in model if isinstance(x, torch.nn.Linear)]

import torch.optim as optim
import tqdm
x = torch.arange(0, 256, 1).unsqueeze(1).repeat(1, 55).to(torch.float)
parameters = [x]
for p in parameters:
    x.requires_grad_()
print(x.dtype)
opt = optim.SGD(parameters, lr=0.01)
# for _ in tqdm.trange(10):
#     y=model.forward(x)
#     loss = (1-y)**2
#     loss = loss.mean()
#     loss.backward()
#     print(x.grad.norm())
#     opt.step()
#     opt.zero_grad()
# simple bruteforce GD isn't working
# too deeeeeep

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# print(last_block.weight)
# fig = px.imshow(last_block.weight.detach()) # 16~31
# fig.show()
fig = go.Figure()
for i in range(100):
    w = linears[-i].weight.detach().cpu().numpy()
    fig.add_trace(
        go.Heatmap(
            z=w,
            visible=(i == 0),
            colorscale="Viridis",
            coloraxis="coloraxis",
            xgap=1,
            ygap=1,
            hoverongaps=False
        )
    )

steps = []
for i in range(100):
    visible = [False] * 100
    visible[i] = True
    steps.append({
        "method": "update",
        "args": [{"visible": visible}, {"title": f"linears[-{i}].weight"}],
        "label": str(i),
    })

fig.update_layout(
    coloraxis=dict(
        cmin=-2,
        cmax=2,
        colorscale="Viridis"
    ),
    sliders=[{"steps": steps, "active": 0}],
    title="linears[0].weight",
)

fig.show()