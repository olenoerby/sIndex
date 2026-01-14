import sys
from pathlib import Path

p = Path(sys.argv[1])
s = p.read_text(encoding='utf-8')
lines = s.splitlines()
stack = []

for i, line in enumerate(lines, 1):
    stripped = line.lstrip('\t ')
    indent = len(line) - len(stripped)
    if stripped.startswith('try:'):
        stack.append((i, indent))
    elif stripped.startswith('except') or stripped.startswith('finally'):
        # match the nearest try with indent <= this indent
        matched = None
        for j in range(len(stack)-1, -1, -1):
            if stack[j][1] <= indent:
                matched = j
                break
        if matched is not None:
            stack.pop(matched)
        else:
            print(f"Unmatched except/finally at line {i}")

if stack:
    for ln, ind in stack:
        print(f"Unmatched try at line {ln} (indent {ind})")
    sys.exit(2)
else:
    print('All try/except/finally blocks appear balanced (by indentation heuristic).')
