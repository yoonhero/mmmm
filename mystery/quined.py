#!/usr/bin/env python
self = """#!/usr/bin/env python
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