#!/usr/bin/env python
# Reflections on Trusting Trust (Ken thompson) - quine can become trojan horse in the level of binary, ISA, even circuit.
self = """#!/usr/bin/env python
# Reflections on Trusting Trust (Ken thompson) - quine can become trojan horse in the level of binary, ISA, even circuit.
self = \"\"\"?\"\"\"
for i, t in enumerate(self):
    if t == \"?\" and self[i-2] == \"\\\"\":
        for t in self:
            if t == \"\\\"\": print(\"\\\\\\\"\", end=\"\")
            elif t == \"\\\\\": print(\"\\\\\\\\\", end=\"\")
            else: print(t, end=\"\")
    else:
        print(t, end=\"\")"""
for i, t in enumerate(self):
    if t == "?" and self[i-2] == "\"":
        for t in self:
            if t == "\"": print("\\\"", end="")
            elif t == "\\": print("\\\\", end="")
            else: print(t, end="")
    else:
        print(t, end="")